import bcrypt

from database.connection import get_connection


class AccountModel:
    @staticmethod
    def get_user_by_id(user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, full_name, username, password, role "
                "FROM users WHERE id = %s LIMIT 1",
                (user_id,)
            )
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

    @staticmethod
    def update_profile(user_id, full_name, username):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_update_user_profile", [user_id, full_name, username])
            conn.commit()
            return AccountModel.get_user_by_id(user_id)
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_password(user_id, current_plain_password, new_plain_password):
        conn = None
        cursor = None
        try:
            user = AccountModel.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found.")
            if not AccountModel.verify_password(current_plain_password, user["password"]):
                raise ValueError("Current password is incorrect.")

            new_plain_password = new_plain_password.strip()

            if not new_plain_password:
                raise ValueError("New password cannot be empty or contain only spaces.")
            if len(new_plain_password) < 8:
                raise ValueError("New password must be at least 8 characters.")
            if new_plain_password == current_plain_password.strip():
                raise ValueError("New password must be different from your current password.")

            hashed = bcrypt.hashpw(
                new_plain_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_change_user_password", [user_id, hashed])
            conn.commit()
            return True
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
