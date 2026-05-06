from controllers.login_controller import LoginController
from models.message_model import MessageModel
from utils.error_logger import log_exception


class MessageController:
    def __init__(self, user=None):
        self._user = user or LoginController.get_current_user() or {}

    def _user_id(self):
        try:
            return int((self._user or {}).get("id") or 0)
        except (TypeError, ValueError):
            return 0

    def _role(self):
        return str((self._user or {}).get("role") or "").strip().lower()

    def _validate_staff_user(self):
        if self._user_id() <= 0:
            raise ValueError("No signed-in user found.")
        if self._role() not in {"admin", "owner"}:
            raise ValueError("Only owners and admins can use messaging.")

    def unread_count(self):
        try:
            self._validate_staff_user()
            return True, MessageModel.get_unread_count(self._user_id())
        except Exception as exc:
            log_exception(exc, source="controllers.message_controller", action="unread_count")
            return False, str(exc)

    def list_conversations(self):
        try:
            self._validate_staff_user()
            return True, MessageModel.list_conversations(self._user_id())
        except Exception as exc:
            log_exception(exc, source="controllers.message_controller", action="list_conversations")
            return False, str(exc)

    def open_conversation(self, other_user_id):
        try:
            self._validate_staff_user()
            other_user_id = int(other_user_id or 0)
            if other_user_id <= 0:
                raise ValueError("Choose a staff member to message.")
            MessageModel.mark_thread_read(self._user_id(), other_user_id)
            return True, MessageModel.get_thread(self._user_id(), other_user_id)
        except Exception as exc:
            log_exception(
                exc,
                source="controllers.message_controller",
                action="open_conversation",
                context={"other_user_id": other_user_id},
            )
            return False, str(exc)

    def send_message(self, receiver_id, body):
        try:
            self._validate_staff_user()
            receiver_id = int(receiver_id or 0)
            MessageModel.send_message(self._user_id(), receiver_id, body)
            return True, None
        except Exception as exc:
            log_exception(
                exc,
                source="controllers.message_controller",
                action="send_message",
                context={"receiver_id": receiver_id},
            )
            return False, str(exc)
