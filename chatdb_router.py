import os
from openai import OpenAI
from sqlalchemy import text
from dotenv import load_dotenv
from connection_db import ENGINES
from schema_loader import get_schema_description
import subprocess
import json

# reset/refresh DB
def reset_database():
    print("\nResetting all datasets to original state...\n")
    scripts = [
        "data_import_student.py",
        "data_import_movielens.py",
        "data_import_berka.py"
    ]
    # runs individually on each dataset, and checks each one
    for script in scripts:
        try:
            result = subprocess.run(["python3", script], capture_output=True, text=True)
            print(f"{script} ran successfully.")
        except Exception as e:
            print(f"Failed to run {script}: {e}")

# load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# settings for user
settings = {
    "show_sql": False,
    "show_raw": False,
    "summary_only": False
}

# user config menu
def configure_settings():
    print("\nChatDB Settings")
    print("1. Toggle show_sql      (currently: {})".format(settings["show_sql"]))
    print("2. Toggle show_raw      (currently: {})".format(settings["show_raw"]))
    print("3. Toggle summary_only  (currently: {})".format(settings["summary_only"]))
    print("4. Back to main\n")

    choice = input("Select an option: ").strip()

    # display appropriate settings choice
    if choice == "1":
        settings["show_sql"] = not settings["show_sql"]
    elif choice == "2":
        settings["show_raw"] = not settings["show_raw"]
    elif choice == "3":
        settings["summary_only"] = not settings["summary_only"]
    elif choice == "4":
        return
    else:
        print("Invalid choice.")

    configure_settings()

# prompt builder for SQL
def build_prompt(user_input):
    schema_info = get_schema_description()
    system_prompt = f"""
You are a PostgreSQL assistant. When a user asks a natural language question, you must:
1. Determine which of the following databases to use:
{list(ENGINES.keys())}
2. Write a valid SQL query for that database based on the schema below:

{schema_info}

Respond in valid JSON format like this:
{{
  "database": "dsci551_movielens",
  "action": "query" | "modification" | "schema_explore",
  "sql": "your SQL query here"
}}

- Use "query" for SELECTs
- Use "modification" for INSERT, UPDATE, DELETE
- Use "schema_explore" for questions about tables/columns
Do not return any results. Only provide the correct JSON.

When deciding which tables to use:
- Only use columns listed in the schema.
- Never invent columns that aren't listed in the schema, so dont use a column from a non-corresponding table.
- Always write SQL in a single line string.

"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

# LLM call 1: generate SQL
def get_llm_response(user_input):
    messages = build_prompt(user_input)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    try:
        # pick up message
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed

    except Exception as e:
        print("Error parsing LLM response:", e)
        print("Raw response:", content)
        return None

# execute SQL
def execute_sql(database, sql, is_modification=False):
    engine = ENGINES.get(database)
    if not engine:
        print(f"Unknown database: {database}")
        return None
    # connect to engine and make sql call
    with engine.connect() as conn:
        try:
            if is_modification:
                with conn.begin():
                    conn.execute(text(sql))
                return [("Modification successful.",)]
            else:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                return rows
        except Exception as e:
            print("SQL execution error!:", e)
            return None

# LLM #2 call
def summarize_result(user_question, result_rows, columns):
    if not result_rows:
        return "No results found."

    schema_info = get_schema_description()

    # max display rows to avoid context window breaking
    max_llm_rows = 25
    visible_rows = result_rows[:max_llm_rows]

    result_text = ""
    if columns:
        result_text += ", ".join(columns) + "\n"
        for row in visible_rows:
            row_text = ", ".join(f"{columns[i]}={value}" for i, value in enumerate(row))
            result_text += row_text + "\n"
    else:
        for row in visible_rows:
            result_text += ", ".join(str(value) for value in row) + "\n"

    # explain max display if reached for user clarity as datasets can be very large
    if len(result_rows) > max_llm_rows:
        result_text += f"\n...Only the first {max_llm_rows} of {len(result_rows)} rows are shown.\n"

    prompt = [
        {
            "role": "system",
            "content": "You are a helpful assistant that explains SQL query results. Always respect the column names and respond in a way that reflects the actual data. Use the schema as reference."
        },
        {
            "role": "user",
            "content": f"The user asked: {user_question}\n\nHere are the first {len(visible_rows)} rows of the result:\n{result_text}\n\nHere is the current schema:\n{schema_info}\n\nTry and display a table with the results and breifly summarize based on what is shown, and make note that the total number of rows is {len(result_rows)}."
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=prompt
    )

    return response.choices[0].message.content.strip()


# === Main Loop ===
if __name__ == "__main__":
    # display menu
    while True:
        print("1. Ask a question")
        print("2. Configure settings")
        print("3. Reset databases to original state")
        print("4. Exit")

        action = input("Choose an option: ").strip()
        # call action from user input
        if action == "4":
            break
        elif action == "2":
            configure_settings()
            continue
        elif action == "3":
            reset_database()
            continue
        elif action != "1":
            print("Invalid choice.")
            continue

        user_question = input("Ask your question: ")
        response = get_llm_response(user_question)

        # if question makes no sense/ cant interpret
        if not response:
            print("Failed to understand the query!")
            continue

        action_type = response.get("action", "query")
        # display sql command
        if settings["show_sql"]:
            print("\nSQL to run:")
            print(response["sql"])

        if action_type == "modification":
            print("\nThis is a data modification operation:")
            print(response["sql"])
            confirm = input("Do you want to execute this modification? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Modification canceled!")
                continue

        rows = execute_sql(response["database"], response["sql"], is_modification=(action_type == "modification"))

        # if table schema changes refresh to avoid issues
        sql_text_lower = response["sql"].lower()
        if any(kw in sql_text_lower for kw in ["alter table", "create table", "drop table"]):
            get_schema_description(force_refresh=True)
            print("Schema cache refreshed after structural change.")

        if rows is None:
            print("A SQL error occurred.")
        # if sql command returns no rows/empty table
        elif not rows:
            print("ℹ️ The query executed successfully, but returned no rows.")
            # llm 2 to summarize results
            summary = summarize_result(user_question, [], [])
            print("\nSummary:")
            print(summary)
        else:
            if settings["summary_only"]:
                columns = [col for col in rows[0].keys()] if hasattr(rows[0], 'keys') else []
                summary = summarize_result(user_question, rows, columns)
                print("\nSummary:")
                print(summary)
            else:
                if settings["show_raw"]:
                    print("\nRaw Query Results:")
                    for row in rows:
                        print(row)

                columns = [col for col in rows[0].keys()] if hasattr(rows[0], 'keys') else []
                summary = summarize_result(user_question, rows, columns)
                print("\nSummary:")
                print(summary + "\n")



