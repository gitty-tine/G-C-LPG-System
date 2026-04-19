import os
import sys

from PySide6.QtCore import QObject

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from controllers.login_controller import LoginController
from models.audit_actor_model import AuditActorModel
from models.admin_transaction_model import TransactionModel


class AdminTransactionController(QObject):
    """Controller that mediates between the admin transaction view and model."""

    def __init__(self, view=None):
        super().__init__()
        self._view = view

    def attach_view(self, view):
        """Assign/replace the view this controller should update."""
        self._view = view
        return self

    def _user_id(self):
        current_user = LoginController.get_current_user()
        if current_user and isinstance(current_user, dict):
            return current_user.get("id", 0)
        return 0

    # Public API -----------------------------------------------------------------
    def load(self, date_from=None, date_to=None):
        """
        Load transactions within an optional date range and push them to the view.
        """
        try:
            transactions = TransactionModel.get_all(date_from, date_to)
            if self._view:
                self._view.load_transactions(transactions)
            return True, transactions
        except Exception as exc:
            if self._view:
                self._view.show_error("Load Failed", str(exc))
            return False, str(exc)

    def mark_paid(self, delivery_id):
        """
        Mark a transaction as paid, then reload the list. Handles already-paid cases.
        """
        # Keep user id handy for any model/backend audit needs.
        user_id = self._user_id()
        try:
            TransactionModel.mark_paid(delivery_id)
            updated = TransactionModel.get_by_delivery_id(delivery_id)
            if updated and updated.get("transaction_id"):
                AuditActorModel.sync_actor(
                    "transactions",
                    updated.get("transaction_id"),
                    "UPDATE",
                    user_id,
                    old_value="Payment Status: unpaid",
                    new_value="Payment Status: paid",
                )
            if self._view:
                date_from, date_to = None, None
                if hasattr(self._view, "current_date_range"):
                    date_from, date_to = self._view.current_date_range()
                self.load(date_from, date_to)
            return True, None
        except ValueError as exc:
            if self._view:
                self._view.show_error("Already Paid", str(exc))
            return False, str(exc)
        except Exception as exc:
            if self._view:
                self._view.show_error("Update Failed", str(exc))
            return False, str(exc)


# Convenience alias for legacy-style calls
def load(date_from=None, date_to=None):
    controller = AdminTransactionController()
    return controller.load(date_from, date_to)
