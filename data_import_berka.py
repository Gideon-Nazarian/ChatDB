from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# DB credentials from .env
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

# create connection
engine = create_engine(
    f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/dsci551_berka"
)

# map files to table names to streamline table creation
csv_to_table = {
    "account.csv": "account",
    "card.csv": "card",
    "client.csv": "client",
    "disp.csv": "disp",
    "district.csv": "district",
    "loan.csv": "loan",
    "order.csv": "bank_order",
    "trans.csv": "transactions"
}

# base path for student data
base_path = "/Users/gideonnazarian/Desktop/DSCI_551/Final_Project/Berka DATA/"

# load all student tables
for file, table in csv_to_table.items():
    full_path = base_path + file
    # for debug/progress
    print(f"Loading {file} into {table}...")
    df = pd.read_csv(full_path, sep=";")
    df.columns = [col.lower() for col in df.columns]
    # for debug/progress
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"Loaded: {table}")

print("Done")