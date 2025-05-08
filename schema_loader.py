from sqlalchemy import inspect, text
from connection_db import ENGINES

_cached_schema = None

# schema is made and displayed to llm calls to make more accurate sql query and output
def get_schema_description(force_refresh=False):
    global _cached_schema
    if _cached_schema and not force_refresh:
        return _cached_schema

    schema_str = "You have access to the following PostgreSQL databases:\n"

    for db_name, engine in ENGINES.items():
        schema_str += f"\nDatabase `{db_name}` contains the following tables:\n"
        inspector = inspect(engine)
        with engine.connect() as conn:
            for table in inspector.get_table_names():
                # List columns
                columns = inspector.get_columns(table)
                col_list = [col["name"] for col in columns]
                col_str = ", ".join(col_list)
                schema_str += f"- `{table}({col_str})`\n"

                # Add sample row (1 line)
                try:
                    sample = conn.execute(text(f"SELECT * FROM {table} LIMIT 1")).fetchone()
                    if sample:
                        sample_data = ", ".join(f"{col}={sample[i]}" for i, col in enumerate(col_list))
                        schema_str += f"   Example: {sample_data}\n"
                except Exception as e:
                    schema_str += f"    Could not retrieve sample row\n"

    _cached_schema = schema_str
    return schema_str

