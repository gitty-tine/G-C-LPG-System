import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.audit_logs_model import AuditLogModel
from utils.error_logger import log_exception


class AuditLogsController:
    def __init__(self, view=None, model=None):
        self._view = view
        self._model = model or AuditLogModel()

    def attach_view(self, view):
        self._view = view
        return self

    def load(self, action=None, section=None, date_from=None, date_to=None):
        try:
            logs = self._model.get_logs(
                action=action,
                section=section,
                date_from=date_from,
                date_to=date_to,
            )
            if self._view:
                self._view.load_logs(logs)
            return True, logs
        except Exception as exc:
            log_exception(
                exc,
                source="controllers.audit_logs_controller",
                action="load",
                context={
                    "action": action,
                    "section": section,
                    "date_from": date_from,
                    "date_to": date_to,
                },
            )
            if self._view:
                self._view.show_error("Load Failed", str(exc))
            return False, str(exc)
