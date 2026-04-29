import random
import string

from database.connection import get_connection


class LoginModel:
    @staticmethod
    def get_user_by_username(username):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, full_name, username, password, role, email "
                "FROM users WHERE BINARY username = %s LIMIT 1",
                (username,),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_user_by_email(email):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, full_name, username, role, email "
                "FROM users WHERE email = %s LIMIT 1",
                (email.strip(),),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def authenticate(username, password):
        user = LoginModel.get_user_by_username(username)
        if user is None:
            return None
        if not LoginModel.verify_password(password, user["password"]):
            return None
        return user

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            import bcrypt
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

    @staticmethod
    def generate_reset_code():
        return "".join(random.choices(string.digits, k=6))

    @staticmethod
    def save_reset_code(user_id, code):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.callproc("sp_save_reset_code", [user_id, code])
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def verify_reset_code(email, code):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, full_name FROM users
                WHERE email = %s
                  AND reset_code = %s
                  AND reset_code_expires_at > NOW()
                LIMIT 1
                """,
                (email.strip(), code.strip()),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def reset_password(user_id, new_plain_password):
        import bcrypt

        conn = None
        cursor = None
        try:
            hashed = bcrypt.hashpw(
                new_plain_password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.callproc("sp_change_user_password", [user_id, hashed])
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


UserModel = LoginModel
