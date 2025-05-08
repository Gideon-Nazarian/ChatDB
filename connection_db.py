from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read DB credentials from .env
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

# Engines for 3 separate databases
ENGINES = {
    "dsci551_students": create_engine(f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/dsci551_students"),
    "dsci551_movielens": create_engine(f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/dsci551_movielens"),
    "dsci551_berka": create_engine(f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/dsci551_berka")
}