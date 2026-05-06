import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "tinesql",
    "database": "gnc_lpg_db",
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        try:
            from utils.error_logger import log_exception

            log_exception(
                e,
                source="database.connection",
                action="get_connection",
                severity="CRITICAL",
            )
        except Exception:
            pass
        raise Exception(f"Database connection failed: {e}")
