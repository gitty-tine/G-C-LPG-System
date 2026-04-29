from controllers.login_controller import LoginController
from models.account_model import AccountModel
from utils.error_handler import clean_db_error
from utils.validators import validate_email, validate_password_strength


class AccountController:
    @staticmethod
    def _current_user():
        user = LoginController.get_current_user()
        if not user or not isinstance(user, dict):
            raise ValueError("No signed-in user found.")
        return user

    @classmethod
    def update_profile(cls, full_name, username, email=None):
        user = cls._current_user()
        full_name = (full_name or "").strip()
        username = (username or "").strip()
        email_raw = email or ""

        if not full_name:
            raise ValueError("Full name cannot be empty.")
        if not username:
            raise ValueError("Username cannot be empty.")

        if email_raw.strip():
            is_valid, error = validate_email(email_raw)
            if not is_valid:
                raise ValueError(error)
            email_clean = email_raw.strip()
        else:
            email_clean = None

        try:
            updated_user = AccountModel.update_profile(
                user["id"], full_name, username, email_clean
            )
            if not updated_user:
                raise ValueError("Unable to refresh the updated user profile.")
            updated_user.update({
                "full_name": full_name,
                "username": username,
                "email": email_clean,
            })
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(clean_db_error(exc))

        LoginController.set_current_user(updated_user)
        return updated_user

    @classmethod
    def change_password(cls, current_password, new_password):
        user = cls._current_user()
        current_password = (current_password or "").strip()
        new_password = new_password or ""

        if not current_password:
            raise ValueError("Current password is required.")
        if new_password.strip() == current_password:
            raise ValueError("New password must be different from your current password.")

        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error)

        try:
            AccountModel.update_password(user["id"], current_password, new_password.strip())
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(clean_db_error(exc))
        return True
