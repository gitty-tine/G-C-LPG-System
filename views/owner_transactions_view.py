import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QScrollArea, QTableWidget

from views.admin_dashboard_view import owner_scrollbar_qss
from views.admin_transaction_view import TransactionView


class OwnerTransactionsView(TransactionView):
	"""Owner-facing read-only transactions page."""

	AUTO_REFRESH_INTERVAL_MS = 5000
	DEFAULT_LOOKBACK_YEARS = 10

	def __init__(self, parent=None, show_topbar=True, controller=None):
		super().__init__(parent=parent, show_topbar=show_topbar, controller=controller)
		# Keep source layout but hide the admin action column for owners.
		self._table.setColumnHidden(6, True)
		self._apply_owner_scrollbar_style()

	def _apply_owner_scrollbar_style(self):
		scrollbar_qss = owner_scrollbar_qss()
		for scroll_area in self.findChildren(QScrollArea):
			scroll_area.setStyleSheet(scroll_area.styleSheet() + scrollbar_qss)
		for table_widget in self.findChildren(QTableWidget):
			table_widget.setStyleSheet(table_widget.styleSheet() + scrollbar_qss)

	def _render_table(self):
		paid_total = 0.0
		unpaid_total = 0.0

		for transaction in self._all_transactions:
			amount = self._safe_float(transaction.get("total_amount"))
			if str(transaction.get("payment_status", "")).lower() == "paid":
				paid_total += amount
			else:
				unpaid_total += amount

		self._metric_paid.value_lbl.setText(self._format_amount(paid_total))
		self._metric_unpaid.value_lbl.setText(self._format_amount(unpaid_total))

		if not self._filtered_transactions:
			self._stack.setCurrentWidget(self._empty_state)
			self._table.setRowCount(0)
			return

		self._stack.setCurrentWidget(self._table)
		self._table.setRowCount(len(self._filtered_transactions))

		for row_index, transaction in enumerate(self._filtered_transactions):
			self._set_item(row_index, 0, transaction.get("customer_name", ""))
			self._set_item(row_index, 1, self._format_date(transaction.get("delivery_date")))
			self._set_item(row_index, 2, transaction.get("product_summary", ""))
			self._set_item(row_index, 3, self._format_amount(transaction.get("total_amount")))
			self._set_status_pill(row_index, 4, transaction.get("payment_status", ""))
			self._set_item(
				row_index,
				5,
				self._format_paid_at(transaction.get("paid_at"), transaction.get("payment_status")),
			)

		self._table.resizeRowsToContents()
