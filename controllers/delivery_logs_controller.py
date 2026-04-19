import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.delivery_logs_model import DeliveryLogsModel


class DeliveryLogsController:
    def __init__(self, view=None, model=None):
        self._view = view
        self._model = model or DeliveryLogsModel()

    def attach_view(self, view):
        self._view = view
        return self

    def load(self):
        try:
            logs = self._model.get_all_logs()
            if self._view:
                self._view.load_logs(logs)
            return True, logs
        except Exception as exc:
            if self._view:
                self._view.show_error("Load Failed", str(exc))
            return False, str(exc)


# Backward-compatible alias for existing imports.
DeliveryLogController = DeliveryLogsController
