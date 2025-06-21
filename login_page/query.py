import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # Load environment variables from .env file

database_url = os.getenv("DB_URL")

engine = create_engine(database_url) 

def auth(username, password) :
    with engine.connect() as conn : 
        query = text(
            "SELECT * FROM user_admin WHERE username = :username AND password = :password"
        )
        result = conn.execute(
            query, {"username": username, "password": password}
        ).fetchone()

        if result is not None : 
            return True
        else : 
            return False 
        
def get_user_id(username) :
    with engine.connect() as conn :
        query = text("""
            select user_id
            from user_admin
            where username = :username
        """)
        result = conn.execute(
            query, {"username": username}
        ).fetchone()
    user_id = result[0]
    return user_id

def get_role(user_id) :
    with engine.connect() as conn :
        query = text("""
            select role
            from user_admin
            where user_id = :user_id
        """)
        result = conn.execute(
            query, {"user_id": user_id}
        ).fetchone()
    role = result[0]
    return role

def get_id_operation(user_id) :
    with engine.connect() as conn:
        query = text(
            """
            SELECT operation_id 
            FROM operation 
            WHERE user_id = :id 
            ORDER BY start_time DESC 
            LIMIT 1
            """
        )
        result = conn.execute(query, {"id": user_id}).fetchone()
    id_operation = result[0]
    return id_operation 

def log_in_session(user_id) :
    with engine.connect() as conn : 
        query = text("""
            INSERT INTO operation (start_time, user_id)
            VALUES (NOW(), :user_id)
        """)
        conn.execute(query, {"user_id": user_id})
        conn.commit()