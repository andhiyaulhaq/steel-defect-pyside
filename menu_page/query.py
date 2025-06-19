import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # Load environment variables from .env file

database_url = os.getenv("DB_URL")

engine = create_engine(database_url) 