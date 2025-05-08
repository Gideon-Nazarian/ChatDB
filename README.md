# ChatDB — Natural Language Interface to PostgreSQL

ChatDB is a lightweight natural language interface (NLI) that allows users to interact with PostgreSQL databases using plain English. It translates user input into SQL using an LLM (OpenAI GPT) and executes those queries across three structured datasets.

---

## Project Structure
```text
Final_Project/
├── Movies DATA/             # MovieLens dataset CSVs
├── Berka DATA/              # Berka dataset CSVs
├── Student DATA/            # Student Performance dataset
├── chatdb_router.py         # Main NL-to-SQL routing script
├── connection_db.py         # PostgreSQL connection engine
├── data_import_movies.py    # Loads MovieLens CSVs
├── data_import_berka.py     # Loads Berka CSVs
├── data_import_student.py   # Loads Student CSVs
├── schema_loader.py         # Schema parsing and caching
├── .env                     # API keys and DB config (not included)
└── requirements.txt         # Python dependencies
```


---
## Setup Instructions

### 1. Clone the Repo or Download the Files

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Libraries

```bash
pip install -r requirements.txt
```

### 4. Create Your PostgreSQL Databases

You must create **three PostgreSQL databases manually** before running anything:

```sql
CREATE DATABASE dsci551_movielens;
CREATE DATABASE dsci551_berka;
CREATE DATABASE dsci551_students;
```

Use a tool like `psql`, pgAdmin, or DBeaver.

### 5. Add Your `.env` File

Create a `.env` file in the root directory with the following values:

```env
DB_USER=your_username
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your_openai_key
```

> **Do not commit this file to GitHub**

### 6. Load the CSVs into PostgreSQL

Make sure the folders `Movies DATA/`, `Berka DATA/`, and `Student DATA/` contain the appropriate CSVs.

Then run the following scripts to import data:

```bash
python data_import_movies.py
python data_import_berka.py
python data_import_student.py
```

---

## Running ChatDB

Once everything is set up, start ChatDB:

```bash
python chatdb_router.py
```

You’ll be prompted to enter a natural language question or command, and the system will return both the SQL query and the query results.

---

## Notes & Manual Setup Reminders

- Ensure the **file names and column names in your CSVs match exactly** with what the import scripts expect.  
- If you move the folders or rename files, update the paths in the import scripts (`data_import_*.py`).  
- The databases **must exist prior to running** any data load or query script.  
- This project assumes **local development only**.

---

## Prerequisites

- Python 3.11+  
- PostgreSQL is installed and running locally  
- An OpenAI API key  
- Internet connection (for LLM API calls)  

---

## Example `.env`

```env
DB_USER=USER
DB_PASS=PASS
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=sk-xxxxxx
```
---

## License

This project was developed for DSCI 551 at USC. All datasets are used for academic purposes only.
