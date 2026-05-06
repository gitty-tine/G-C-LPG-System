import weakref

from controllers.login_controller import LoginController
from models.notification_model import NotificationModel
from utils.error_logger import log_exception


class _NotificationSignal:
    def __init__(self):
        self._subscribers = []

    def connect(self, callback):
        if getattr(callback, "__self__", None) is None:
            self._subscribers.append(lambda: callback)
            return
        try:
            ref = weakref.WeakMethod(callback)
        except TypeError:
            ref = weakref.ref(callback)
        self._subscribers.append(ref)

    def emit(self, reason):
        alive = []
        for ref in self._subscribers:
            callback = ref()
            if callback is None:
                continue
            alive.append(ref)
            try:
                callback(reason)
            except RuntimeError:
                continue
        self._subscribers = alive


class NotificationEventBus:
    def __init__(self):
        self.notifications_changed = _NotificationSignal()


_notification_events = None


def notification_events():
    global _notification_events
    if _notification_events is None:
        _notification_events = NotificationEventBus()
    return _notification_events


def notify_notifications_changed(reason="data_changed"):
    notification_events().notifications_changed.emit(str(reason or "data_changed"))


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
            log_exception(
                exc,
                source="controllers.notification_controller",
                action="list_notifications",
            )
            return False, str(exc)

    def mark_read(self, notification_key):
        try:
            NotificationModel.mark_read(self._user_id(), notification_key)
            return True, None
        except Exception as exc:
            log_exception(
                exc,
                source="controllers.notification_controller",
                action="mark_read",
                context={"notification_key": notification_key},
            )
            return False, str(exc)

    def mark_all_read(self, notification_keys):
        try:
            NotificationModel.mark_many_read(self._user_id(), notification_keys)
            return True, None
        except Exception as exc:
            log_exception(
                exc,
                source="controllers.notification_controller",
                action="mark_all_read",
                context={"notification_count": len(notification_keys or [])},
            )
            return False, str(exc)
