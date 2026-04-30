import os
import sys
from datetime import date as dt_date, timedelta

from PySide6.QtCore import QObject

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.report_model import ReportModel


class ReportController(QObject):
    """Controller that connects the report view to ReportModel."""

    def __init__(self, view=None):
        super().__init__()
        self._view = view

    def attach_view(self, view):
        self._view = view
        return self

    def load_period(self, period_name, date_from, date_to):
        try:
            live_summary = ReportModel.get_summary(date_from, date_to) or {}
            snapshot_summary = self._snapshot_summary_for_period(period_name, date_from, date_to)
            summary = self._merge_summaries(live_summary, snapshot_summary)
            insights = ReportModel.get_report_insights(date_from, date_to) or {}
            summary = {**summary, **insights}
            breakdown = ReportModel.get_detailed_breakdown(date_from, date_to) or []
            payload = self._build_payload(period_name, summary, breakdown)

            if self._view and hasattr(self._view, "load_report_data"):
                self._view.load_report_data(period_name, payload, date_from, date_to)

            return True, payload
        except Exception as exc:
            if self._view and hasattr(self._view, "show_error"):
                self._view.show_error("Load Failed", str(exc))
            return False, str(exc)

    def _snapshot_summary_for_period(self, period_name, date_from, date_to):
        period_key = str(period_name or "").strip().lower()
        if period_key == "daily" and self._is_completed_daily_range(date_to):
            summary = ReportModel.get_daily_snapshot_summary(date_from, date_to) or {}
            return summary if self._has_complete_snapshot(summary, self._day_count(date_from, date_to)) else {}
        if (
            period_key == "weekly"
            and self._is_full_week_range(date_from, date_to)
            and self._is_completed_week_range(date_to)
        ):
            summary = ReportModel.get_weekly_snapshot_summary(date_from, date_to) or {}
            return summary if self._has_complete_snapshot(summary, self._week_count(date_from, date_to)) else {}
        if (
            period_key == "monthly"
            and self._is_full_month_range(date_from, date_to)
            and self._is_completed_month_range(date_to)
        ):
            summary = ReportModel.get_monthly_snapshot_summary(date_from, date_to) or {}
            return summary if self._has_complete_snapshot(summary, self._month_count(date_from, date_to)) else {}
        return {}

    def _merge_summaries(self, live_summary, snapshot_summary):
        if not snapshot_summary:
            return live_summary
        merged = dict(live_summary or {})
        for key in (
            "total_deliveries",
            "total_delivered",
            "total_cancelled",
            "total_pending",
            "total_in_transit",
            "total_sales",
            "total_paid",
            "total_unpaid",
        ):
            if key in snapshot_summary and snapshot_summary.get(key) is not None:
                merged[key] = snapshot_summary.get(key)
        return merged

    def _has_complete_snapshot(self, summary, expected_count):
        if expected_count <= 0:
            return False
        return int(summary.get("snapshot_count", 0) or 0) >= expected_count

    def _day_count(self, date_from, date_to):
        return (date_to - date_from).days + 1

    def _week_count(self, date_from, date_to):
        return max(1, self._day_count(date_from, date_to) // 7)

    def _month_count(self, date_from, date_to):
        count = 0
        current = date_from.replace(day=1)
        end = date_to.replace(day=1)
        while current <= end:
            count += 1
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return count

    def _is_full_week_range(self, date_from, date_to):
        return date_from.weekday() == 0 and date_to.weekday() == 6

    def _is_full_month_range(self, date_from, date_to):
        if date_from.day != 1:
            return False
        if date_to.month == 12:
            next_month = date_to.replace(year=date_to.year + 1, month=1, day=1)
        else:
            next_month = date_to.replace(month=date_to.month + 1, day=1)
        return date_to == (next_month - timedelta(days=1))

    def _today(self):
        return dt_date.today()

    def _current_week_start(self):
        today = self._today()
        return today - timedelta(days=today.weekday())

    def _current_month_start(self):
        today = self._today()
        return today.replace(day=1)

    def _is_completed_daily_range(self, date_to):
        return date_to < self._today()

    def _is_completed_week_range(self, date_to):
        return date_to < self._current_week_start()

    def _is_completed_month_range(self, date_to):
        return date_to < self._current_month_start()

    def _build_payload(self, period_name, summary, breakdown_rows):
        normalized_rows = []
        for row in breakdown_rows:
            normalized_rows.append(
                {
                    "id": str(row.get("id", "")),
                    "date": self._format_date_value(row.get("schedule_date"), row.get("date")),
                    "customer": row.get("customer", ""),
                    "product": row.get("product", ""),
                    "quantity": int(row.get("quantity", 0) or 0),
                    "type": self._display_text(row.get("type", "")),
                    "amount": float(row.get("amount", 0) or 0),
                    "payment_status": self._display_text(row.get("payment_status", "unpaid")),
                    "status": self._display_text(row.get("status", row.get("delivery_status", ""))),
                    "delivery_status": self._display_text(row.get("delivery_status", row.get("status", ""))),
                }
            )

        return {
            "period_name": period_name,
            "summary": {
                "total_deliveries": int(summary.get("total_deliveries", 0) or 0),
                "total_delivered": int(summary.get("total_delivered", 0) or 0),
                "total_cancelled": int(summary.get("total_cancelled", 0) or 0),
                "total_pending": int(summary.get("total_pending", 0) or 0),
                "total_in_transit": int(summary.get("total_in_transit", 0) or 0),
                "total_sales": float(summary.get("total_sales", 0) or 0),
                "total_paid": float(summary.get("total_paid", 0) or 0),
                "total_unpaid": float(summary.get("total_unpaid", 0) or 0),
                "avg_transaction_value": float(summary.get("avg_transaction_value", 0) or 0),
                "peak_sales_day": summary.get("peak_sales_day", ""),
                "peak_sales_amount": float(summary.get("peak_sales_amount", 0) or 0),
                "most_sold_product": summary.get("most_sold_product", ""),
                "most_sold_product_quantity": int(summary.get("most_sold_product_quantity", 0) or 0),
                "most_sold_product_revenue": float(summary.get("most_sold_product_revenue", 0) or 0),
            },
            "rows": normalized_rows,
        }

    def _display_text(self, value):
        raw = str(value or "").strip().replace("_", " ")
        return raw.title() if raw else ""

    def _format_date_value(self, raw_date, fallback_text):
        if raw_date is not None:
            try:
                return raw_date.strftime("%Y-%m-%d")
            except Exception:
                pass
        if fallback_text:
            text = str(fallback_text).strip()
            if len(text) >= 10 and text[4] == "-" and text[7] == "-":
                return text[:10]
        return ""
