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
        
def get_id_user(username) :
    with engine.connect() as conn :
        query = text("""
            select id_user
            from user_admin
            where username = :username
        """)
        result = conn.execute(
            query, {"username": username}
        ).fetchone()
    id_user = result[0]
    return id_user

def get_role(id_user) :
    with engine.connect() as conn :
        query = text("""
            select role
            from user_admin
            where id_user = :id_user
        """)
        result = conn.execute(
            query, {"id_user": id_user}
        ).fetchone()
    role = result[0]
    return role

def get_id_operation(id_user) :
    with engine.connect() as conn:
        query = text(
            """
            SELECT id_operation 
            FROM operation 
            WHERE id_user = :id 
            ORDER BY start_time DESC 
            LIMIT 1
            """
        )
        result = conn.execute(query, {"id": id_user}).fetchone()
    id_operation = result[0]
    return id_operation 

def log_in_session(id_user) :
    with engine.connect() as conn : 
        query = text("""
            INSERT INTO operation (start_time, id_user)
            VALUES (NOW(), :id_user)
        """)
        conn.execute(query, {"id_user": id_user})
        conn.commit()