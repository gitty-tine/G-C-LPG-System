import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QScrollArea

from views.admin_dashboard_view import owner_scrollbar_qss
from views.admin_transaction_view import TransactionView


class OwnerTransactionsView(TransactionView):
	"""Owner-facing read-only transactions page."""

	AUTO_REFRESH_INTERVAL_MS = 5000
	DEFAULT_LOOKBACK_YEARS = 10

	def __init__(self, parent=None, show_topbar=True, controller=None):
		super().__init__(
			parent=parent,
			show_topbar=show_topbar,
			controller=controller,
			read_only=True,
		)
		self._apply_owner_scrollbar_style()

	def _apply_owner_scrollbar_style(self):
		scrollbar_qss = owner_scrollbar_qss()
		for scroll_area in self.findChildren(QScrollArea):
			scroll_area.setStyleSheet(scroll_area.styleSheet() + scrollbar_qss)
