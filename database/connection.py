import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "database": "gnclpgdb",
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")