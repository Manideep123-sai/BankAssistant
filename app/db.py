import mysql.connector
from mysql.connector import pooling
from .config import DB_CONFIG


# Create a simple connection pool for the application
db_pool = pooling.MySQLConnectionPool(
    pool_name="bank_pool",
    pool_size=10,
    **DB_CONFIG,
)


def get_connection():
    """Get a connection from the pool."""
    return db_pool.get_connection()


def fetch_one(query: str, params=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        row = cur.fetchone()
        return row
    finally:
        cur.close()
        conn.close()


def fetch_all(query: str, params=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


def execute(query: str, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

