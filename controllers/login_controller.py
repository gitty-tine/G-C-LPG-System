from models.login_model import LoginModel


class LoginController:
    _current_user = None

    @classmethod
    def login(cls, username, password, role_hint=None):
        if not username or not password:
            return False, "Please enter your username and password."

        try:
            user = LoginModel.authenticate(username, password)
        except Exception as e:
            return False, f"Could not connect to the database.\n{e}"

        if user is None:
            return False, "Incorrect username or password."

        selected_role = (role_hint or "").strip().lower()
        actual_role = (user.get("role") or "").strip().lower()
        if selected_role and actual_role and selected_role != actual_role:
            expected_label = "Owner" if actual_role == "owner" else "Admin"
            return False, f"This account is for {expected_label}. Please switch the role and try again."

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

    def handle_login(self, username, password, role_hint=None):
        success, message = self.login(username, password, role_hint=role_hint)
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
