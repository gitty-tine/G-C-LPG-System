from controllers.login_controller import LoginController
from models.notification_model import NotificationModel


class NotificationController:
    def __init__(self, user=None):
        self._user = user or LoginController.get_current_user() or {}

    def _user_id(self):
        try:
            return int((self._user or {}).get("id") or 0)
        except (TypeError, ValueError):
            return 0

    def _role(self):
        return str((self._user or {}).get("role") or "").strip().lower()

    def list_notifications(self):
        try:
            notifications = NotificationModel.get_for_user(
                self._user_id(),
                role=self._role(),
            )
            return True, notifications
        except Exception as exc:
            return False, str(exc)

    def mark_read(self, notification_key):
        try:
            NotificationModel.mark_read(self._user_id(), notification_key)
            return True, None
        except Exception as exc:
            return False, str(exc)

    def mark_all_read(self, notification_keys):
        try:
            NotificationModel.mark_many_read(self._user_id(), notification_keys)
            return True, None
        except Exception as exc:
            return False, str(exc)
