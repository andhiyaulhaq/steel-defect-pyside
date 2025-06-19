import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # Load environment variables from .env file

database_url = os.getenv("DB_URL")

engine = create_engine(database_url) 

def log_out_session(id_operation) :
    with engine.connect() as conn:
        query = text(
            "UPDATE operation SET end_time = NOW() WHERE id_operation = :id_operation"
        )
        conn.execute(query, {"id_operation": id_operation})
        conn.commit()