import os
import sys

from PySide6.QtCore import QObject

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.owner_dashboard_model import OwnerDashboardModel


class OwnerDashboardController(QObject):
    """Thin controller for the owner dashboard MVC flow."""

    def __init__(self, view=None):
        super().__init__()
        self._view = None
        if view is not None:
            self.attach_view(view)

    def attach_view(self, view, request_initial=True):
        self._view = view
        if hasattr(view, "_controller"):
            view._controller = self
        if request_initial:
            self.refresh_dashboard()
        return self

    def create_view(self, user=None):
        from views.owner_dashboard_view import OwnerDashboardView

        view = OwnerDashboardView(user=user)
        self.attach_view(view, request_initial=True)
        return view

    def refresh_dashboard(self, silent=False):
        ok, payload = self.get_dashboard_data()
        if ok:
            self._push(payload)
        elif not silent:
            self._error("Dashboard Load Failed", payload)

    @staticmethod
    def get_dashboard_data():
        try:
            return True, OwnerDashboardModel.get_all_dashboard_data()
        except Exception as exc:  # pylint: disable=broad-except
            return False, str(exc)

    def _push(self, data):
        if self._view is not None and hasattr(self._view, "set_dashboard_data"):
            self._view.set_dashboard_data(data)

    def _error(self, title, message):
        if self._view is not None and hasattr(self._view, "show_error"):
            self._view.show_error(title, message)
        else:
            sys.stderr.write(f"{title}: {message}\n")


def build_owner_dashboard(user=None):
    """Create the owner dashboard with its controller already attached."""
    return OwnerDashboardController().create_view(user=user)
