from controllers.login_controller import LoginController
from models.account_model import AccountModel
from models.audit_actor_model import AuditActorModel


class AccountController:
    @staticmethod
    def _current_user():
        user = LoginController.get_current_user()
        if not user or not isinstance(user, dict):
            raise ValueError("No signed-in user found.")
        return user

    @classmethod
    def update_profile(cls, full_name, username):
        user = cls._current_user()
        before = f"Full Name: {user.get('full_name', '')}, Username: {user.get('username', '')}"
        full_name = (full_name or "").strip()
        username = (username or "").strip()

        if not full_name:
            raise ValueError("Full name cannot be empty.")
        if not username:
            raise ValueError("Username cannot be empty.")

        updated_user = AccountModel.update_profile(user["id"], full_name, username)
        if not updated_user:
            raise ValueError("Unable to refresh the updated user profile.")

        LoginController.set_current_user(updated_user)
        AuditActorModel.sync_actor(
            "users",
            user["id"],
            "UPDATE",
            user["id"],
            old_value=before,
            new_value=f"Full Name: {updated_user.get('full_name', '')}, Username: {updated_user.get('username', '')}",
        )
        return updated_user

    @classmethod
    def change_password(cls, current_password, new_password):
        user = cls._current_user()
        current_password = current_password or ""
        new_password = new_password or ""

        if not current_password:
            raise ValueError("Current password is required.")
        if not new_password:
            raise ValueError("New password is required.")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters.")
        if current_password == new_password:
            raise ValueError("New password must be different from the current password.")

        AccountModel.update_password(user["id"], current_password, new_password)
        AuditActorModel.sync_actor(
            "users",
            user["id"],
            "UPDATE",
            user["id"],
            old_value="Password: hidden",
            new_value="Password updated",
        )
        return True
