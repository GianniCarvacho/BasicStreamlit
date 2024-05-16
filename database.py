import sqlite3
import pandas as pd
from sqlalchemy import create_engine

DATABASE_NAME = "Database/lifting_weights.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def create_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise TEXT NOT NULL,
                weight_lbs INTEGER NOT NULL,
                datetime datetime DEFAULT CURRENT_TIMESTAMP  
            );
        ''')
        conn.commit()
        conn.close()
    except Exception as e: 
        print(e)

def insert_weight(exercise, weight):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO weights (exercise, weight_lbs) VALUES (?, ?)', (exercise, weight))
    conn.commit()
    conn.close()

def fetch_all_weights():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM weights')
    data = c.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=['id', 'exercise', 'weight_lbs', 'datetime'])

def load_data_from_db():
    engine = create_engine('sqlite:///Database/lifting_weights.db')
    query = """
    SELECT datetime, weight_lbs, exercise FROM weights
    """
    return pd.read_sql(query, engine)
