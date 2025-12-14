import pandas as pd
import mysql.connector
from mysql.connector import Error

DB_HOST = "localhost"
DB_PORT = 3307           # IMPORTANT: docker expose 3307 -> 3306
DB_USER = "adam"
DB_PASSWORD = "1234"
DB_NAME = "hotel_db"

def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Error as e:
        raise RuntimeError(f"Erreur connexion MySQL: {e}")

def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()
