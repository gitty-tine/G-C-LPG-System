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
                "SELECT id, full_name, username, password, role "
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


UserModel = LoginModel