from models.login_model import LoginModel
from utils.error_logger import log_exception


class LoginController:
    _current_user = None

    @classmethod
    def login(cls, username, password):
        if not username or not password:
            return False, "Please enter your username and password."

        try:
            user = LoginModel.authenticate(username, password)
        except Exception as e:
            log_exception(
                e,
                source="controllers.login_controller",
                action="login",
                severity="CRITICAL",
                context={"username": username},
            )
            return False, "Could not connect to the database. Please check the database server and try again."

        if user is None:
            return False, "Incorrect username or password."

        cls._current_user = user
        return True, ""

    @classmethod
    def build_dashboard_for_user(cls, user):
        user_role = (user or {}).get("role", "").lower()
        if user_role == "admin":
            from controllers.admin_dashboard_controller import build_admin_dashboard
            return build_admin_dashboard(user=user)

        from controllers.owner_dashboard_controller import build_owner_dashboard
        return build_owner_dashboard(user=user)

    def handle_login(self, username, password):
        success, message = self.login(username, password)
        if not success:
            return False, message, None

        dashboard = self.build_dashboard_for_user(self.get_current_user())
        return True, "", dashboard

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def set_current_user(cls, user):
        cls._current_user = user

    @classmethod
    def logout(cls):
        cls._current_user = None


AuthController = LoginController
