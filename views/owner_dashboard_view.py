import datetime
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import (
    QDate,
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTime,
    QTimer,
    QVariantAnimation,
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from controllers.notification_controller import NotificationController
from controllers.message_controller import MessageController
from views.message_view import MessageIconButton, MessagingPanel
from views.admin_dashboard_view import (
    AMBER,
    BASE_DIR,
    ChangePasswordModal,
    GRAY_1,
    GRAY_2,
    GRAY_3,
    GRAY_4,
    GRAY_5,
    HDivider,
    NavItemWidget,
    NotificationBellButton,
    NotificationDropdown,
    PersonIconWidget,
    ProfileDropdown,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEAL_MID,
    TEAL_PALE,
    WHITE,
    EditNameModal,
    inter,
    load_fonts,
    owner_scrollbar_qss,
    playfair,
    show_ok_success_popup,
)


def animate_fade_slide(widget, y_offset=12, dur=220):
    """Fade + slide down-in for a widget."""
    eff = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(eff)
    widget.move(widget.x(), widget.y() + y_offset)

    group = QParallelAnimationGroup(widget)

    a_opacity = QPropertyAnimation(eff, b"opacity", widget)
    a_opacity.setStartValue(0)
    a_opacity.setEndValue(1)
    a_opacity.setDuration(dur)
    a_opacity.setEasingCurve(QEasingCurve.OutCubic)

    a_pos = QPropertyAnimation(widget, b"pos", widget)
    a_pos.setStartValue(widget.pos())
    a_pos.setEndValue(widget.pos() - QPoint(0, y_offset))
    a_pos.setDuration(dur)
    a_pos.setEasingCurve(QEasingCurve.OutCubic)

    group.addAnimation(a_opacity)
    group.addAnimation(a_pos)
    group.start(QParallelAnimationGroup.DeleteWhenStopped)


def animate_number(label, end_value, prefix="", dur=700, decimals=0):
    """Animate numeric text inside a QLabel."""
    existing_anim = getattr(label, "_value_anim", None)
    if existing_anim is not None:
        try:
            existing_anim.stop()
            existing_anim.deleteLater()
        except RuntimeError:
            pass

    anim = QVariantAnimation(label)
    anim.setStartValue(0.0 if decimals else 0)
    anim.setEndValue(end_value)
    anim.setDuration(dur)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    label._value_anim = anim

    if decimals:
        anim.valueChanged.connect(lambda v: label.setText(f"{prefix}{float(v):,.{decimals}f}"))
    else:
        anim.valueChanged.connect(lambda v: label.setText(f"{prefix}{int(v):,}"))

    def _cleanup():
        if getattr(label, "_value_anim", None) is anim:
            label._value_anim = None

    anim.finished.connect(_cleanup)
    anim.finished.connect(anim.deleteLater)
    anim.start()


def animate_bar(bar_fill, target_h, delay_ms=0, dur=350):
    """Grow a vertical bar with optional delay."""
    existing_timer = getattr(bar_fill, "_height_anim_timer", None)
    if existing_timer is not None:
        try:
            existing_timer.stop()
            existing_timer.deleteLater()
        except RuntimeError:
            pass

    existing_anim = getattr(bar_fill, "_height_anim", None)
    if existing_anim is not None:
        try:
            existing_anim.stop()
            existing_anim.deleteLater()
        except RuntimeError:
            pass

    # Ensure layout can grow the widget by driving its minimumHeight.
    bar_fill.setMaximumHeight(max(target_h, bar_fill.maximumHeight()))
    anim = QPropertyAnimation(bar_fill, b"minimumHeight", bar_fill)
    anim.setStartValue(0)
    anim.setEndValue(target_h)
    anim.setDuration(dur)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    # Keep a Python-side reference so the animation isn't garbage-collected mid-flight.
    bar_fill._height_anim = anim

    def _start():
        if getattr(bar_fill, "_height_anim", None) is not anim:
            return
        anim.start()

    def _cleanup():
        if getattr(bar_fill, "_height_anim", None) is anim:
            bar_fill._height_anim = None
        timer = getattr(bar_fill, "_height_anim_timer", None)
        if timer is not None:
            try:
                timer.stop()
                timer.deleteLater()
            except RuntimeError:
                pass
            bar_fill._height_anim_timer = None

    anim.finished.connect(_cleanup)
    anim.finished.connect(anim.deleteLater)

    if delay_ms:
        delay_timer = QTimer(bar_fill)
        delay_timer.setSingleShot(True)
        delay_timer.timeout.connect(_start)
        bar_fill._height_anim_timer = delay_timer
        delay_timer.start(delay_ms)
    else:
        bar_fill._height_anim_timer = None
        _start()


class OwnerKpiCard(QFrame):
    def __init__(self, label, value, desc, top_color, parent=None, value_prefix=""):
        super().__init__(parent)
        self._top_color = top_color
        self.setObjectName("ownerKpiCard")
        self.setStyleSheet(
            f"""
            QFrame#ownerKpiCard {{
                background: {WHITE};
                border: 1px solid {GRAY_2};
                border-radius: 8px;
            }}
        """
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(120)

        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        top_border = QFrame()
        top_border.setFixedHeight(4)
        top_border.setStyleSheet(
            f"background:{self._top_color};border:none;border-top-left-radius:8px;border-top-right-radius:8px;"
        )
        root_lay.addWidget(top_border)

        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(18, 14, 18, 12)
        lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setFont(inter(9, QFont.DemiBold))
        lbl.setMinimumHeight(16)
        lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.3px;background:transparent;border:none;")

        val = QLabel()
        val.setFont(inter(22, QFont.DemiBold))
        val.setMinimumHeight(34)
        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        if isinstance(value, (int, float)):
            numeric_value = float(value)
            decimals = 2 if not numeric_value.is_integer() else 0
            if decimals:
                val.setText(f"{value_prefix}{numeric_value:,.2f}")
            else:
                val.setText(f"{value_prefix}{int(numeric_value):,}")
        else:
            val.setText(str(value))

        dsc = QLabel(desc)
        dsc.setFont(inter(11))
        dsc.setMinimumHeight(18)
        dsc.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addWidget(dsc)
        lay.addStretch()
        root_lay.addWidget(body)


class SalesChartCard(QFrame):
    def __init__(self, weekly_sales, parent=None):
        super().__init__(parent)
        self._bar_entries = []

        self.setObjectName("salesChartCard")
        self.setStyleSheet(f"QFrame#salesChartCard{{background:{WHITE};border:1px solid {GRAY_2};border-radius:8px;}}")
        self.setFixedHeight(640)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(72)
        head.setStyleSheet(f"background:#fbfdfc;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 0, 18, 0)

        t = QLabel("Delivered Sales - Current Week")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        h_lay.addWidget(t)
        lay.addWidget(head)

        body = QWidget()
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(18, 14, 18, 14)
        b_lay.setSpacing(12)

        max_val = max([float(value or 0) for _, value in weekly_sales] + [1.0])
        total_week = sum(float(value or 0) for _, value in weekly_sales)
        avg_day = (total_week / len(weekly_sales)) if weekly_sales else 0

        stat_row = QHBoxLayout()
        stat_row.setSpacing(10)

        total_lbl = QLabel(f"Week Total: PHP {total_week:,.2f}")
        total_lbl.setFont(inter(11, QFont.DemiBold))
        total_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        avg_lbl = QLabel(f"Daily Avg: PHP {avg_day:,.2f}")
        avg_lbl.setFont(inter(11, QFont.Medium))
        avg_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        stat_row.addWidget(total_lbl)
        stat_row.addStretch()
        stat_row.addWidget(avg_lbl)
        b_lay.addLayout(stat_row)

        self._chart_shell = QFrame()
        self._chart_shell.setStyleSheet("QFrame{background:transparent;border:none;}")
        self._chart_shell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        c_lay = QHBoxLayout(self._chart_shell)
        c_lay.setContentsMargins(0, 6, 0, 0)
        c_lay.setSpacing(6)

        for idx, (day, value) in enumerate(weekly_sales):
            col_wrap = QWidget()
            col_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            col_lay = QVBoxLayout(col_wrap)
            col_lay.setContentsMargins(2, 0, 2, 0)
            col_lay.setSpacing(3)
            col_lay.setAlignment(Qt.AlignHCenter)

            amount_lbl = QLabel(self._compact_amount(value))
            amount_lbl.setFont(inter(9, QFont.Medium))
            amount_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            amount_lbl.setAlignment(Qt.AlignCenter)

            bar_slot = QWidget()
            bar_slot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            bar_slot.setStyleSheet("background:transparent;border:none;")
            slot_lay = QVBoxLayout(bar_slot)
            slot_lay.setContentsMargins(0, 4, 0, 4)
            slot_lay.setSpacing(0)

            bar_fill = QFrame()
            bar_fill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            bar_fill.setStyleSheet(
                f"QFrame{{background:{TEAL};border:none;border-top-left-radius:6px;border-top-right-radius:6px;}}"
            )
            bar_fill.setMinimumHeight(0)

            slot_lay.addStretch(1)
            slot_lay.addWidget(bar_fill)

            day_lbl = QLabel(day)
            day_lbl.setFont(inter(10, QFont.Medium))
            day_lbl.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")
            day_lbl.setAlignment(Qt.AlignCenter)

            col_lay.addWidget(amount_lbl)
            col_lay.addWidget(bar_slot)
            col_lay.addWidget(day_lbl)

            c_lay.addWidget(col_wrap, 1)
            self._bar_entries.append((bar_slot, bar_fill, value, max_val, idx))

        b_lay.addWidget(self._chart_shell)
        lay.addWidget(body)

        QTimer.singleShot(0, self._sync_bar_heights)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_bar_heights()

    def _sync_bar_heights(self):
        for bar_slot, bar_fill, value, max_val, idx in self._bar_entries:
            slot_height = max(80, bar_slot.height())
            usable_height = max(24, slot_height - 12)
            bar_height = max(8, int((value / max_val) * usable_height) - 10)
            animate_bar(bar_fill, bar_height, delay_ms=60 * idx)

    @staticmethod
    def _compact_amount(value):
        amount = float(value or 0)
        if amount >= 1000:
            return f"{amount / 1000:.1f}k"
        if amount.is_integer():
            return str(int(amount))
        return f"{amount:,.2f}"


class OwnerDashboardView(QMainWindow):
    _NAV_ICONS = {
        "Dashboard": "dashboard_icon",
        "LPG Products": "products_icon",
        "Transactions": "transactions_icon",
        "Reports": "reports_icon",
        "Delivery Logs": "logs_icon",
        "Audit Logs": "logs_icon",
    }

    def __init__(self, user=None, controller=None, action_handlers=None, page_factories=None):
        super().__init__()
        load_fonts()
        self._user = user or {"full_name": "", "role": "owner"}
        self._controller = None
        self._dashboard_data = self._empty_dashboard_data()
        self._dashboard_refresh_interval_ms = 15000
        self._notification_controller = NotificationController(self._user)
        self._notifications = []
        self._message_controller = MessageController(self._user)
        self._dropdown_open = False
        self._action_handlers = {}
        self._page_factories = {}
        self._set_default_action_handlers()
        self._set_default_page_factories()
        if action_handlers:
            self.bind_action_handlers(**action_handlers)
        if page_factories:
            self.bind_page_factories(**page_factories)
        self.setWindowTitle("G and C LPG Trading - Owner Dashboard")
        self._build_ui()
        if controller is not None:
            self.bind_controller(controller, request_initial=True)
        self.showFullScreen()

    def bind_action_handlers(self, update_profile=None, change_password=None, logout=None):
        if update_profile is not None:
            self._action_handlers["update_profile"] = update_profile
        if change_password is not None:
            self._action_handlers["change_password"] = change_password
        if logout is not None:
            self._action_handlers["logout"] = logout
        return self

    def bind_page_factories(
        self,
        products=None,
        transactions=None,
        reports=None,
        delivery_logs=None,
        audit_logs=None,
    ):
        if products is not None:
            self._page_factories["products"] = products
        if transactions is not None:
            self._page_factories["transactions"] = transactions
        if reports is not None:
            self._page_factories["reports"] = reports
        if delivery_logs is not None:
            self._page_factories["delivery_logs"] = delivery_logs
        if audit_logs is not None:
            self._page_factories["audit_logs"] = audit_logs
        return self

    def _set_default_action_handlers(self):
        self._action_handlers = {
            "update_profile": self._default_update_profile,
            "change_password": self._default_change_password,
            "logout": self._default_logout,
        }

    def _set_default_page_factories(self):
        self._page_factories = {
            "products": self._default_create_products_page,
            "transactions": self._default_create_transactions_page,
            "reports": self._default_create_reports_page,
            "delivery_logs": self._default_create_delivery_logs_page,
            "audit_logs": self._default_create_audit_logs_page,
        }

    def bind_controller(self, controller, request_initial=True):
        self._controller = controller
        if hasattr(controller, "attach_view"):
            controller.attach_view(self, request_initial=request_initial)
        elif request_initial and hasattr(controller, "refresh_dashboard"):
            controller.refresh_dashboard()
        self._sync_dashboard_refresh_timer()
        return controller

    def reload_dashboard(self, silent=False):
        if self._controller is not None and hasattr(self._controller, "refresh_dashboard"):
            self._controller.refresh_dashboard(silent=silent)

    def set_dashboard_data(self, data):
        self._dashboard_data = self._normalize_dashboard_data(data)
        if not hasattr(self, "_content_stack") or self._content_stack is None:
            return

        new_page = self._build_dashboard_content()
        old_page = getattr(self, "_dashboard_page", None)
        current_is_dashboard = old_page is not None and self._content_stack.currentWidget() is old_page
        old_index = self._content_stack.indexOf(old_page) if old_page is not None else -1
        insert_index = old_index if old_index >= 0 else 0

        self._content_stack.insertWidget(insert_index, new_page)
        if old_page is not None and old_index >= 0:
            self._content_stack.removeWidget(old_page)
            old_page.deleteLater()

        self._dashboard_page = new_page
        if current_is_dashboard or self._content_stack.currentWidget() is None:
            self._content_stack.setCurrentWidget(new_page)
        self._sync_dashboard_refresh_timer()

    def show_error(self, title, message):
        QMessageBox.warning(self, title, str(message))

    @staticmethod
    def _empty_dashboard_data():
        return {
            "sales_kpis": {
                "total_sales_today": 0,
                "total_sales_this_week": 0,
                "total_sales_this_month": 0,
                "total_sales_last_month": 0,
                "month_sales_change_pct": 0,
                "total_receivables": 0,
            },
            "delivery_counts": {
                "total_today": 0,
                "delivered_today": 0,
                "cancelled_today": 0,
                "pending_today": 0,
                "in_transit_today": 0,
                "delivery_success_rate": 0,
                "cancellation_rate": 0,
            },
            "weekly_chart": [],
            "top_customers": [],
            "recent_transactions": [],
        }

    def _normalize_dashboard_data(self, data):
        normalized = self._empty_dashboard_data()
        if not isinstance(data, dict):
            return normalized

        sales_kpis = data.get("sales_kpis")
        if isinstance(sales_kpis, dict):
            normalized["sales_kpis"].update(sales_kpis)

        delivery_counts = data.get("delivery_counts")
        if isinstance(delivery_counts, dict):
            normalized["delivery_counts"].update(delivery_counts)

        weekly_chart = data.get("weekly_chart")
        if isinstance(weekly_chart, list):
            normalized["weekly_chart"] = weekly_chart

        top_customers = data.get("top_customers")
        if isinstance(top_customers, list):
            normalized["top_customers"] = top_customers

        recent_transactions = data.get("recent_transactions")
        if isinstance(recent_transactions, list):
            normalized["recent_transactions"] = recent_transactions

        return normalized

    @staticmethod
    def _to_int(value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _text(value, fallback=""):
        text = str(value or "").strip()
        return text if text else fallback

    def _money(self, value, formatted=None):
        if formatted not in (None, ""):
            return f"PHP {formatted}"
        return f"PHP {self._to_float(value):,.2f}"

    def _percent_text(self, value):
        return f"{self._to_float(value):.0f}%"

    def _revenue_comparison_value(self, sales_kpis):
        current_month = self._to_float(sales_kpis.get("total_sales_this_month"))
        last_month = self._to_float(sales_kpis.get("total_sales_last_month"))
        if last_month <= 0 and current_month > 0:
            return "First active month"
        return f"{self._to_float(sales_kpis.get('month_sales_change_pct')):+.0f}%"

    def _revenue_comparison_desc(self, sales_kpis):
        last_month = self._to_float(sales_kpis.get("total_sales_last_month"))
        if last_month <= 0:
            return "No last-month sales to compare"
        return f"Last month PHP {last_month:,.2f}"

    def _open_deliveries_today(self):
        delivery_counts = self._dashboard_data.get("delivery_counts", {})
        pending = self._to_int(delivery_counts.get("pending_today"))
        in_transit = self._to_int(delivery_counts.get("in_transit_today"))
        return pending + in_transit

    def _open_deliveries_desc(self):
        delivery_counts = self._dashboard_data.get("delivery_counts", {})
        pending = self._to_int(delivery_counts.get("pending_today"))
        in_transit = self._to_int(delivery_counts.get("in_transit_today"))
        return f"Pending {pending} | In transit {in_transit}"

    def _modern_scrollbar_qss(self):
        return owner_scrollbar_qss()

    def _display_name(self):
        full_name = str(self._user.get("full_name", "") or "").strip()
        if full_name:
            return full_name
        username = str(self._user.get("username", "") or "").strip()
        if username:
            return username
        return "Owner"

    def _greeting_name(self):
        username = str(self._user.get("username", "") or "").strip()
        if username:
            return username
        return self._display_name()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background:{GRAY_1};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())

        main_col = QWidget()
        main_col.setStyleSheet("background:transparent;")
        main_lay = QVBoxLayout(main_col)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self._build_topbar())

        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet("background:transparent;border:none;")
        self._dashboard_page = self._build_dashboard_content()
        self._content_stack.addWidget(self._dashboard_page)
        main_lay.addWidget(self._content_stack)

        root.addWidget(main_col)

        self._dashboard_refresh_timer = QTimer(self)
        self._dashboard_refresh_timer.setInterval(self._dashboard_refresh_interval_ms)
        self._dashboard_refresh_timer.timeout.connect(self._refresh_dashboard_if_visible)

        self._notification_timer = QTimer(self)
        self._notification_timer.setInterval(15000)
        self._notification_timer.timeout.connect(self._refresh_notifications)
        self._notification_timer.start()
        QTimer.singleShot(750, self._refresh_notifications)
        QTimer.singleShot(1100, self._refresh_message_badge)

        self._name_modal = EditNameModal(central)
        self._pass_modal = ChangePasswordModal(central)

    def _build_sidebar(self):
        sb = QWidget()
        sb.setFixedWidth(280)
        sb.setStyleSheet(
            f"""
            QWidget {{
                background:{TEAL_DARK};
                border-right:1px solid {TEAL};
            }}
        """
        )

        lay = QVBoxLayout(sb)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        logo = QWidget()
        logo.setStyleSheet(
            "background:transparent;border:none;border-bottom:1px solid rgba(255,255,255,0.1);"
        )
        l_lay = QVBoxLayout(logo)
        l_lay.setContentsMargins(18, 20, 18, 20)
        l_lay.setSpacing(2)

        name_lbl = QLabel("G and C LPG Trading")
        name_lbl.setFont(playfair(13, QFont.DemiBold))
        name_lbl.setStyleSheet(
            "color:#a8e6df;letter-spacing:0.5px;background:transparent;border:none;"
        )

        sub_lbl = QLabel("DELIVERY & TRACKING SYSTEM")
        sub_lbl.setFont(inter(9, QFont.Normal))
        sub_lbl.setStyleSheet(
            "color:rgba(255,255,255,0.4);letter-spacing:1.5px;background:transparent;border:none;"
        )

        l_lay.addWidget(name_lbl)
        l_lay.addWidget(sub_lbl)
        lay.addWidget(logo)

        self._profile_block = QWidget()
        self._profile_block.setStyleSheet(
            """
            QWidget {
                background:transparent;
                border:none;
                border-bottom:1px solid rgba(255,255,255,0.1);
            }
            QWidget:hover { background:rgba(255,255,255,0.07); }
            """
        )
        self._profile_block.setCursor(Qt.PointingHandCursor)
        self._profile_block.setFixedHeight(64)
        self._profile_block.mousePressEvent = self._toggle_dropdown

        p_lay = QHBoxLayout(self._profile_block)
        p_lay.setContentsMargins(18, 10, 14, 8)
        p_lay.setSpacing(10)

        icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
        avatar = PersonIconWidget(TEAL, icon_path)

        info = QVBoxLayout()
        info.setSpacing(0)
        info.setContentsMargins(0, 0, 0, 0)
        self._name_display = QLabel(self._display_name())
        self._name_display.setFont(inter(12, QFont.Medium))
        self._name_display.setStyleSheet("color:#fff;background:transparent;border:none;")

        role_lbl = QLabel("Owner")
        role_lbl.setFont(inter(10, QFont.Normal))
        role_lbl.setStyleSheet(
            "color:rgba(255,255,255,0.5);letter-spacing:0.3px;background:transparent;border:none;"
        )

        info.addWidget(self._name_display)
        info.addWidget(role_lbl)

        self._chevron = QLabel("▾")
        self._chevron.setFont(inter(14, QFont.Bold))
        self._chevron.setFixedSize(18, 18)
        self._chevron.setAlignment(Qt.AlignCenter)
        self._chevron.setStyleSheet("color:rgba(255,255,255,0.75);background:transparent;border:none;")

        p_lay.addWidget(avatar)
        p_lay.addLayout(info)
        p_lay.addStretch()
        p_lay.addWidget(self._chevron)
        lay.addWidget(self._profile_block)

        self._dropdown = ProfileDropdown()
        self._dropdown.edit_name_btn.clicked.connect(self._open_edit_name)
        self._dropdown.change_pass_btn.clicked.connect(self._open_change_password)

        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet(self._modern_scrollbar_qss())

        nav_w = QWidget()
        nav_w.setStyleSheet("background:transparent;")
        nav_lay = QVBoxLayout(nav_w)
        nav_lay.setContentsMargins(0, 0, 0, 0)
        nav_lay.setSpacing(0)

        nav_lay.addWidget(self._nav_section("Main"))
        self.btn_dashboard = self._nav_item("Dashboard", active=True)
        nav_lay.addWidget(self.btn_dashboard)

        nav_lay.addWidget(self._nav_section("Management"))
        self.btn_products = self._nav_item("LPG Products")
        self.btn_transactions = self._nav_item("Transactions")
        self.btn_reports = self._nav_item("Reports")
        for b in [self.btn_products, self.btn_transactions, self.btn_reports]:
            nav_lay.addWidget(b)

        nav_lay.addWidget(self._nav_section("Records"))
        self.btn_del_logs = self._nav_item("Delivery Logs")
        self.btn_audit_logs = self._nav_item("Audit Logs")
        for b in [self.btn_del_logs, self.btn_audit_logs]:
            nav_lay.addWidget(b)

        self.btn_dashboard.mousePressEvent = lambda event: self._show_dashboard_page()
        self.btn_products.mousePressEvent = lambda event: self._show_products_page()
        self.btn_transactions.mousePressEvent = lambda event: self._show_transactions_page()
        self.btn_reports.mousePressEvent = lambda event: self._show_reports_page()
        self.btn_del_logs.mousePressEvent = lambda event: self._show_delivery_logs_page()
        self.btn_audit_logs.mousePressEvent = lambda event: self._show_audit_logs_page()

        nav_lay.addStretch()
        nav_scroll.setWidget(nav_w)
        lay.addWidget(nav_scroll)

        footer = QWidget()
        footer.setStyleSheet(
            "background:transparent;border:none;border-top:1px solid rgba(255,255,255,0.1);"
        )
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(18, 14, 18, 14)
        f_lay.setSpacing(8)

        so_icon = QLabel()
        so_icon.setFixedSize(20, 20)
        so_icon.setAlignment(Qt.AlignCenter)
        so_icon.setStyleSheet("background:transparent;border:none;")
        so_icon_path = os.path.join(BASE_DIR, "assets", "signout_icon.png")
        so_pixmap = QPixmap(so_icon_path)
        if not so_pixmap.isNull():
            so_icon.setPixmap(so_pixmap.scaledToWidth(18, Qt.SmoothTransformation))

        signout = QPushButton("Sign Out")
        signout.setCursor(Qt.PointingHandCursor)
        signout.setFont(inter(10))
        signout.clicked.connect(self._sign_out)
        signout.setStyleSheet(
            """
            QPushButton{color:rgba(255,255,255,0.35);background:transparent;border:none;text-align:left;padding:0;}
            QPushButton:hover{color:rgba(255,255,255,0.65);}
            """
        )
        f_lay.addWidget(so_icon)
        f_lay.addWidget(signout)
        lay.addWidget(footer)
        return sb

    def _nav_section(self, text):
        w = QWidget()
        w.setStyleSheet("background:transparent;border:none;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 18, 18, 8)
        lbl = QLabel(text.upper())
        lbl.setFont(inter(9, QFont.Medium))
        lbl.setStyleSheet(
            "color:rgba(255,255,255,0.28);letter-spacing:2px;background:transparent;border:none;"
        )
        lay.addWidget(lbl)
        return w

    def _nav_item(self, text, active=False):
        w = NavItemWidget(active=active)
        w.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 18, 0)
        row.setSpacing(10)
        row.addSpacing(16)

        icon_key = self._NAV_ICONS.get(text, "placeholder")
        icon = QLabel()
        icon.setFixedSize(30, 20)
        icon.setAlignment(Qt.AlignCenter)

        icon_path = os.path.join(BASE_DIR, "assets", f"{icon_key}.png")
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            target_width = 18
            icon.setPixmap(pixmap.scaledToWidth(target_width, Qt.SmoothTransformation))
        else:
            icon.setText("•")
            icon.setFont(inter(10, QFont.Medium))

        row.addWidget(icon)

        lbl = QLabel(text)
        row.addWidget(lbl)
        row.addStretch()

        icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        w._icon_lbl = icon
        w._text_lbl = lbl
        self._set_nav_item_style(w, active)
        return w

    def _set_nav_item_style(self, nav_item, active):
        nav_item.set_active(active)
        if hasattr(nav_item, "_icon_lbl"):
            nav_item._icon_lbl.setStyleSheet(
                "color:rgba(255,255,255,0.9);background:transparent;border:none;"
                if active
                else "color:rgba(255,255,255,0.55);background:transparent;border:none;"
            )
        if hasattr(nav_item, "_text_lbl"):
            nav_item._text_lbl.setFont(inter(10, QFont.Medium if active else QFont.Normal))
            nav_item._text_lbl.setStyleSheet(
                "color:#fff;background:transparent;border:none;"
                if active
                else "color:rgba(255,255,255,0.55);background:transparent;border:none;"
            )

    def _set_active_sidebar_item(self, active_item):
        for nav_item in [
            self.btn_dashboard,
            self.btn_products,
            self.btn_transactions,
            self.btn_reports,
            self.btn_del_logs,
            self.btn_audit_logs,
        ]:
            self._set_nav_item_style(nav_item, nav_item is active_item)

    def _create_embedded_page(self, page_key):
        factory = self._page_factories.get(page_key)
        if factory is None:
            raise RuntimeError(f"No page factory bound for '{page_key}'.")
        return factory()

    def _show_dashboard_page(self):
        self._content_stack.setCurrentWidget(self._dashboard_page)
        self._set_active_sidebar_item(self.btn_dashboard)
        self._set_topbar_title("OWNER'S DASHBOARD")
        self.reload_dashboard(silent=True)
        self._sync_dashboard_refresh_timer()

    def _show_products_page(self):
        if not hasattr(self, "_embedded_product_page") or self._embedded_product_page is None:
            self._embedded_product_page = self._create_embedded_page("products")
            self._content_stack.addWidget(self._embedded_product_page)
        self._content_stack.setCurrentWidget(self._embedded_product_page)
        self._set_active_sidebar_item(self.btn_products)
        self._set_topbar_title("LPG PRODUCTS")
        self._sync_dashboard_refresh_timer()

    def _show_transactions_page(self):
        if not hasattr(self, "_embedded_transaction_page") or self._embedded_transaction_page is None:
            self._embedded_transaction_page = self._create_embedded_page("transactions")
            self._content_stack.addWidget(self._embedded_transaction_page)
        elif getattr(self, "_owner_transaction_controller", None) is None:
            self._ensure_transaction_page_controller()
        self._content_stack.setCurrentWidget(self._embedded_transaction_page)
        self._set_active_sidebar_item(self.btn_transactions)
        self._set_topbar_title("TRANSACTIONS")
        self._sync_dashboard_refresh_timer()

    def _show_reports_page(self):
        if not hasattr(self, "_embedded_reports_page") or self._embedded_reports_page is None:
            self._embedded_reports_page = self._create_embedded_page("reports")
            self._content_stack.addWidget(self._embedded_reports_page)
        self._content_stack.setCurrentWidget(self._embedded_reports_page)
        self._set_active_sidebar_item(self.btn_reports)
        self._set_topbar_title("REPORTS")
        self._sync_dashboard_refresh_timer()

    def _show_delivery_logs_page(self):
        if not hasattr(self, "_embedded_delivery_logs_page") or self._embedded_delivery_logs_page is None:
            self._embedded_delivery_logs_page = self._create_embedded_page("delivery_logs")
            self._content_stack.addWidget(self._embedded_delivery_logs_page)
        elif getattr(self, "_owner_delivery_log_controller", None) is None:
            self._ensure_delivery_logs_page_controller()
        self._content_stack.setCurrentWidget(self._embedded_delivery_logs_page)
        self._set_active_sidebar_item(self.btn_del_logs)
        self._set_topbar_title("DELIVERY LOGS")
        self._sync_dashboard_refresh_timer()

    def _show_audit_logs_page(self):
        if not hasattr(self, "_embedded_audit_logs_page") or self._embedded_audit_logs_page is None:
            self._embedded_audit_logs_page = self._create_embedded_page("audit_logs")
            self._content_stack.addWidget(self._embedded_audit_logs_page)
        elif getattr(self, "_owner_audit_logs_controller", None) is None:
            self._ensure_audit_logs_page_controller()
        self._content_stack.setCurrentWidget(self._embedded_audit_logs_page)
        self._set_active_sidebar_item(self.btn_audit_logs)
        self._set_topbar_title("AUDIT LOGS")
        self._sync_dashboard_refresh_timer()

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_dashboard_refresh_timer()

    def _refresh_dashboard_if_visible(self):
        if (
            self._controller is not None
            and hasattr(self, "_content_stack")
            and self._content_stack.currentWidget() is self._dashboard_page
        ):
            self.reload_dashboard(silent=True)

    def _sync_dashboard_refresh_timer(self):
        if not hasattr(self, "_dashboard_refresh_timer"):
            return
        should_run = (
            self.isVisible()
            and self._controller is not None
            and hasattr(self, "_content_stack")
            and self._content_stack.currentWidget() is self._dashboard_page
        )
        if should_run and not self._dashboard_refresh_timer.isActive():
            self._dashboard_refresh_timer.start()
        elif not should_run and self._dashboard_refresh_timer.isActive():
            self._dashboard_refresh_timer.stop()

    def _build_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(84)
        bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 8, 28, 8)

        self._breadcrumb_lbl = QLabel("OWNER'S DASHBOARD")
        self._breadcrumb_lbl.setFont(inter(11, QFont.Medium))
        self._breadcrumb_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._breadcrumb_lbl.setStyleSheet(
            f"color:{GRAY_4};letter-spacing:0.5px;background:transparent;border:none;"
        )
        lay.addWidget(self._breadcrumb_lbl)
        lay.addStretch()

        clock_col = QVBoxLayout()
        clock_col.setContentsMargins(0, 0, 0, 0)
        clock_col.setSpacing(2)
        clock_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._clock_lbl = QLabel("--:--:--")
        self._clock_lbl.setFont(inter(17, QFont.Medium))
        self._clock_lbl.setMinimumHeight(30)
        self._clock_lbl.setAlignment(Qt.AlignRight)
        self._clock_lbl.setStyleSheet(
            f"color:{TEAL_DARK};letter-spacing:1px;background:transparent;border:none;"
        )

        self._date_lbl = QLabel(QDate.currentDate().toString("dddd, MMMM d, yyyy"))
        self._date_lbl.setFont(inter(11))
        self._date_lbl.setMinimumHeight(18)
        self._date_lbl.setAlignment(Qt.AlignRight)
        self._date_lbl.setStyleSheet(
            f"color:{GRAY_4};letter-spacing:0.3px;background:transparent;border:none;"
        )

        clock_col.addWidget(self._clock_lbl)
        clock_col.addWidget(self._date_lbl)
        lay.addLayout(clock_col)
        lay.addSpacing(16)

        self._message_btn = MessageIconButton()
        self._message_btn.clicked.connect(self._toggle_messages)
        lay.addWidget(self._message_btn)
        lay.addSpacing(8)

        self._notif_btn = NotificationBellButton()
        self._notif_btn.clicked.connect(self._toggle_notifications)
        lay.addWidget(self._notif_btn)

        self._message_panel = MessagingPanel(
            self._message_controller,
            on_unread_changed=self._set_message_unread_count,
        )

        self._notification_dropdown = NotificationDropdown(
            on_mark_all=self._mark_all_notifications_read,
            on_item_clicked=self._open_notification,
        )

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()
        return bar

    def _set_topbar_title(self, title):
        if hasattr(self, "_breadcrumb_lbl"):
            self._breadcrumb_lbl.setText(title)

    def _tick(self):
        self._clock_lbl.setText(QTime.currentTime().toString("hh:mm:ss"))

    def _set_message_unread_count(self, count):
        if hasattr(self, "_message_btn"):
            self._message_btn.set_unread_count(count)

    def _refresh_message_badge(self):
        if not hasattr(self, "_message_panel"):
            return
        self._message_panel.refresh_unread_badge()

    def _toggle_messages(self):
        if self._message_panel.isVisible():
            self._message_panel.hide()
            return
        if hasattr(self, "_notification_dropdown") and self._notification_dropdown.isVisible():
            self._notification_dropdown.hide()
        self._message_panel.show_for(self._message_btn)

    def _refresh_notifications(self):
        if not hasattr(self, "_notification_dropdown"):
            return

        success, result = self._notification_controller.list_notifications()
        if not success:
            self._notifications = []
            if hasattr(self, "_notif_btn"):
                self._notif_btn.set_unread_count(0)
                self._notif_btn.setToolTip(f"Notifications unavailable: {result}")
            if self._notification_dropdown.isVisible():
                self._notification_dropdown.set_notifications([])
            return

        self._notifications = result or []
        unread = sum(1 for item in self._notifications if not item.get("is_read"))
        self._notif_btn.set_unread_count(unread)
        if self._notification_dropdown.isVisible():
            self._notification_dropdown.set_notifications(self._notifications)

    def _toggle_notifications(self):
        if self._notification_dropdown.isVisible():
            self._notification_dropdown.hide()
            return

        if hasattr(self, "_message_panel") and self._message_panel.isVisible():
            self._message_panel.hide()
        self._refresh_notifications()
        self._notification_dropdown.set_notifications(self._notifications)
        self._notification_dropdown.show_for(self._notif_btn)

    def _mark_all_notifications_read(self):
        keys = self._notification_dropdown.notification_keys()
        success, _ = self._notification_controller.mark_all_read(keys)
        if success:
            self._refresh_notifications()

    def _open_notification(self, notification):
        key = (notification or {}).get("key")
        if key:
            self._notification_controller.mark_read(key)
        self._notification_dropdown.hide()
        self._refresh_notifications()
        self._navigate_notification_action((notification or {}).get("action"))

    def _navigate_notification_action(self, action):
        action = str(action or "").strip().lower()
        routes = {
            "deliveries": self._show_delivery_logs_page,
            "transactions": self._show_transactions_page,
            "customers": self._show_audit_logs_page,
            "products": self._show_products_page,
            "audit_logs": self._show_audit_logs_page,
        }
        handler = routes.get(action)
        if handler is not None:
            handler()

    def _build_dashboard_content(self):
        sales_kpis = self._dashboard_data.get("sales_kpis", {})
        delivery_counts = self._dashboard_data.get("delivery_counts", {})
        open_deliveries_today = self._open_deliveries_today()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(self._modern_scrollbar_qss())

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(28, 24, 28, 28)
        lay.setSpacing(14)

        header_row = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.setSpacing(2)

        sub = QLabel("OWNER OVERVIEW")
        sub.setFont(inter(10, QFont.DemiBold))
        sub.setStyleSheet(
            f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;"
        )

        hour = datetime.datetime.now().hour
        greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        name_part = self._greeting_name()

        title = QLabel(f"{greet}, {name_part}")
        self._greeting_title = title
        title.setFont(playfair(28, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        page_sub = QLabel("Monitor delivered sales, collections, deliveries, and customer trends in one place.")
        page_sub.setFont(inter(12))
        page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

        left_col.addWidget(sub)
        left_col.addWidget(title)
        left_col.addWidget(page_sub)

        header_row.addLayout(left_col)
        header_row.addStretch()
        lay.addLayout(header_row)

        stat_block = QWidget()
        stat_lay = QVBoxLayout(stat_block)
        stat_lay.setContentsMargins(0, 0, 0, 0)
        stat_lay.setSpacing(14)

        sales_row = QHBoxLayout()
        sales_row.setSpacing(14)
        sales_row.addWidget(
            OwnerKpiCard(
                "TOTAL SALES TODAY",
                self._to_float(sales_kpis.get("total_sales_today")),
                "Delivered sales today",
                TEAL,
                value_prefix="PHP ",
            ),
            1,
        )
        sales_row.addWidget(
            OwnerKpiCard(
                "TOTAL SALES THIS WEEK",
                self._to_float(sales_kpis.get("total_sales_this_week")),
                "Delivered sales this week",
                TEAL_MID,
                value_prefix="PHP ",
            ),
            1,
        )
        sales_row.addWidget(
            OwnerKpiCard(
                "TOTAL SALES THIS MONTH",
                self._to_float(sales_kpis.get("total_sales_this_month")),
                "Delivered sales this month",
                TEAL_LIGHT,
                value_prefix="PHP ",
            ),
            1,
        )
        stat_lay.addLayout(sales_row)

        finance_row = QHBoxLayout()
        finance_row.setSpacing(14)
        finance_row.addWidget(
            OwnerKpiCard(
                "MONTHLY REVENUE CHANGE",
                self._revenue_comparison_value(sales_kpis),
                self._revenue_comparison_desc(sales_kpis),
                TEAL_MID if self._to_float(sales_kpis.get("month_sales_change_pct")) >= 0 else AMBER,
            ),
            1,
        )
        finance_row.addWidget(
            OwnerKpiCard(
                "TOTAL RECEIVABLES",
                self._to_float(sales_kpis.get("total_receivables")),
                "All unpaid delivered sales",
                AMBER,
                value_prefix="PHP ",
            ),
            1,
        )
        finance_row.addWidget(
            OwnerKpiCard(
                "COMPLETION TODAY",
                self._percent_text(delivery_counts.get("delivery_success_rate")),
                "Delivered out of scheduled",
                TEAL_LIGHT,
            ),
            1,
        )
        stat_lay.addLayout(finance_row)

        lay.addWidget(stat_block)

        chart_ops_row = QHBoxLayout()
        chart_ops_row.setSpacing(14)

        chart_ops_row.addWidget(self._build_sales_chart_card(), stretch=3, alignment=Qt.AlignTop)

        ops_col = QVBoxLayout()
        ops_col.setSpacing(14)
        ops_col.addWidget(
            OwnerKpiCard(
                "TOTAL DELIVERIES TODAY",
                self._to_int(delivery_counts.get("total_today")),
                "All scheduled today",
                TEAL,
            ),
            0,
        )
        ops_col.addWidget(
            OwnerKpiCard(
                "OPEN DELIVERIES TODAY",
                open_deliveries_today,
                self._open_deliveries_desc(),
                AMBER if open_deliveries_today else TEAL_LIGHT,
            ),
            0,
        )
        ops_col.addWidget(self._build_top_customers_card(), 0)
        chart_ops_row.addLayout(ops_col, stretch=1)

        lay.addLayout(chart_ops_row)

        lay.addWidget(self._build_recent_transactions_card())

        scroll.setWidget(w)
        QTimer.singleShot(0, lambda: animate_fade_slide(w))
        return scroll

    def _build_sales_chart_card(self):
        weekly_sales = []
        for row in self._dashboard_data.get("weekly_chart", []):
            if isinstance(row, dict):
                weekly_sales.append(
                    (
                        self._text(row.get("day_label"), "Day"),
                        self._to_float(row.get("daily_sales")),
                    )
                )
        if not weekly_sales:
            weekly_sales = [("Mon", 0), ("Tue", 0), ("Wed", 0), ("Thu", 0), ("Fri", 0), ("Sat", 0), ("Sun", 0)]
        return SalesChartCard(weekly_sales)

    def _build_top_customers_card(self):
        card = QFrame()
        card.setObjectName("topCustomersCard")
        card.setStyleSheet(
            f"QFrame#topCustomersCard{{background:{WHITE};border:1px solid {GRAY_2};border-radius:8px;}}"
        )
        card.setFixedHeight(360)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(60)
        head.setStyleSheet(f"background:#fbfdfc;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 0, 18, 0)
        t = QLabel("Top Customers This Month")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        h_lay.addWidget(t)
        lay.addWidget(head)

        content = QWidget()
        content.setStyleSheet("background:transparent;border:none;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(12, 12, 12, 12)
        content_lay.setSpacing(10)

        top_customers = self._dashboard_data.get("top_customers", [])

        if not top_customers:
            empty_lbl = QLabel("No customer spending data available yet.")
            empty_lbl.setFont(inter(11))
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            content_lay.addStretch()
            content_lay.addWidget(empty_lbl)
            content_lay.addStretch()
            lay.addWidget(content)
            return card

        for row_idx, row in enumerate(top_customers):
            customer_name = self._text(
                row.get("customer_name") if isinstance(row, dict) else "",
                "Unknown customer",
            )
            total_spent = self._to_float(row.get("total_spent") if isinstance(row, dict) else 0)
            revenue_share = self._to_float(row.get("revenue_share_pct") if isinstance(row, dict) else 0)

            item = QWidget()
            item_lay = QHBoxLayout(item)
            item_lay.setContentsMargins(12, 8, 12, 8)
            item_lay.setSpacing(12)

            rank_badge = QFrame()
            rank_badge.setFixedSize(32, 32)
            rank_badge.setStyleSheet(
                f"QFrame{{background:{TEAL_DARK};border-radius:50%;color:{WHITE};}}"
                if row_idx == 0
                else f"QFrame{{background:{TEAL_LIGHT};border-radius:50%;color:{TEAL_DARK};}}"
            )
            badge_lay = QVBoxLayout(rank_badge)
            badge_lay.setContentsMargins(0, 0, 0, 0)
            rank_num = QLabel(str(row_idx + 1))
            rank_num.setFont(inter(12, QFont.Bold))
            rank_num.setAlignment(Qt.AlignCenter)
            rank_num.setStyleSheet(
                "background:transparent;border:none;color:" + (WHITE if row_idx == 0 else TEAL_DARK) + ";"
            )
            badge_lay.addWidget(rank_num)
            item_lay.addWidget(rank_badge)

            info_col = QVBoxLayout()
            info_col.setContentsMargins(0, 0, 0, 0)
            info_col.setSpacing(2)

            name_lbl = QLabel(customer_name)
            name_lbl.setFont(inter(11, QFont.Medium))
            name_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            info_col.addWidget(name_lbl)

            amount_lbl = QLabel(f"PHP {total_spent:,.2f}")
            amount_lbl.setFont(inter(9, QFont.Normal))
            amount_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            info_col.addWidget(amount_lbl)

            item_lay.addLayout(info_col)
            item_lay.addStretch()

            pct_lbl = QLabel(f"{revenue_share:.0f}%")
            pct_lbl.setFont(inter(10, QFont.Medium))
            pct_lbl.setStyleSheet(f"color:{TEAL};background:transparent;border:none;")
            pct_lbl.setAlignment(Qt.AlignRight)
            item_lay.addWidget(pct_lbl)

            item.setStyleSheet(
                f"QWidget{{background:{TEAL_PALE};border-radius:7px;border:1px solid {TEAL_LIGHT};}}"
                if row_idx == 0
                else "QWidget{background:#fbfdfc;border:1px solid #edf2f0;border-radius:7px;}"
            )
            item.setFixedHeight(56)

            content_lay.addWidget(item)

        content_lay.addStretch()
        lay.addWidget(content)
        return card

    def _build_recent_transactions_card(self):
        card = QFrame()
        card.setObjectName("recentTransactionsCard")
        card.setStyleSheet(
            f"QFrame#recentTransactionsCard{{background:{WHITE};border:1px solid {GRAY_2};border-radius:8px;}}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(60)
        head.setStyleSheet(f"background:#fbfdfc;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 0, 18, 0)
        t = QLabel("Recent Transactions")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        h_lay.addWidget(t)
        h_lay.addStretch()

        view_all_btn = QPushButton("View All")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setFont(inter(10, QFont.Medium))
        view_all_btn.clicked.connect(self._show_transactions_page)
        view_all_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {TEAL_DARK};
                background: {TEAL_PALE};
                border: 1px solid {TEAL_LIGHT};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background: {TEAL_LIGHT};
                color: {WHITE};
            }}
            """
        )
        h_lay.addWidget(view_all_btn)
        lay.addWidget(head)

        content = QWidget()
        content.setStyleSheet("background:transparent;border:none;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(18, 14, 18, 16)
        content_lay.setSpacing(8)

        recent_transactions = self._dashboard_data.get("recent_transactions", [])
        status_colors = {"PAID": TEAL, "UNPAID": AMBER}

        if not recent_transactions:
            empty_lbl = QLabel("No recent transactions yet.")
            empty_lbl.setFont(inter(11))
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            content_lay.addStretch()
            content_lay.addWidget(empty_lbl)
            content_lay.addStretch()
            lay.addWidget(content)
            return card

        header = QWidget()
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(12, 0, 12, 2)
        header_lay.setSpacing(12)
        header.setStyleSheet("background:transparent;border:none;")

        for text, width, alignment in [
            ("Delivery ID", 92, Qt.AlignLeft),
            ("Customer", None, Qt.AlignLeft),
            ("Delivery Date", 140, Qt.AlignLeft),
            ("Amount", 130, Qt.AlignRight),
            ("Payment", 96, Qt.AlignCenter),
        ]:
            label = QLabel(text)
            label.setFont(inter(9, QFont.DemiBold))
            label.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.8px;background:transparent;border:none;")
            label.setAlignment(alignment | Qt.AlignVCenter)
            if width is not None:
                label.setFixedWidth(width)
                header_lay.addWidget(label)
            else:
                header_lay.addWidget(label, 1)

        content_lay.addWidget(header)

        for row in recent_transactions:
            delivery_ref = self._text(
                row.get("delivery_id") if isinstance(row, dict) else "",
                "N/A",
            )
            customer_name = self._text(
                row.get("customer_name") if isinstance(row, dict) else "",
                "Unknown customer",
            )
            delivery_date = self._text(
                row.get("delivery_date_fmt") if isinstance(row, dict) else "",
                "No date",
            )
            amount = self._money(
                row.get("total_amount") if isinstance(row, dict) else 0,
                row.get("total_amount_fmt") if isinstance(row, dict) else None,
            )
            status = self._text(
                row.get("payment_status") if isinstance(row, dict) else "",
                "UNKNOWN",
            ).upper()

            item = QWidget()
            item_lay = QHBoxLayout(item)
            item_lay.setContentsMargins(12, 8, 12, 8)
            item_lay.setSpacing(12)

            ref_lbl = QLabel(delivery_ref)
            ref_lbl.setFont(inter(11, QFont.Medium))
            ref_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            ref_lbl.setFixedWidth(92)
            item_lay.addWidget(ref_lbl)

            info_col = QVBoxLayout()
            info_col.setContentsMargins(0, 0, 0, 0)
            info_col.setSpacing(2)

            cust_lbl = QLabel(customer_name)
            cust_lbl.setFont(inter(11, QFont.Medium))
            cust_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            info_col.addWidget(cust_lbl)
            item_lay.addLayout(info_col, 1)

            date_lbl = QLabel(delivery_date)
            date_lbl.setFont(inter(10))
            date_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            date_lbl.setFixedWidth(140)
            item_lay.addWidget(date_lbl)

            amount_lbl = QLabel(amount)
            amount_lbl.setFont(inter(11, QFont.Medium))
            amount_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            amount_lbl.setFixedWidth(130)
            amount_lbl.setAlignment(Qt.AlignRight)
            item_lay.addWidget(amount_lbl)

            status_badge = QFrame()
            badge_width = 65
            status_badge.setFixedSize(badge_width, 22)
            status_color = status_colors.get(status, GRAY_3)
            status_badge.setStyleSheet(
                f"QFrame{{background:{status_color};border:none;border-radius:4px;}}"
            )
            badge_lay = QVBoxLayout(status_badge)
            badge_lay.setContentsMargins(0, 0, 0, 0)
            status_text = QLabel(status)
            status_text.setFont(inter(8, QFont.Medium))
            status_text.setAlignment(Qt.AlignCenter)
            status_text.setStyleSheet(f"color:{WHITE};background:transparent;border:none;")
            badge_lay.addWidget(status_text)

            status_cell = QWidget()
            status_cell.setFixedWidth(96)
            status_cell.setStyleSheet("background:transparent;border:none;")
            status_col = QVBoxLayout(status_cell)
            status_col.setContentsMargins(0, 0, 0, 0)
            status_col.setSpacing(2)
            status_col.addWidget(status_badge, 0, Qt.AlignRight)
            item_lay.addWidget(status_cell)

            item.setObjectName("recentTransactionRow")
            item.setStyleSheet(
                f"QWidget#recentTransactionRow{{background:#fbfdfc;border:1px solid #edf2f0;border-radius:7px;}}"
            )
            item.setFixedHeight(50)

            content_lay.addWidget(item)

        content_lay.addStretch()
        lay.addWidget(content)
        return card

    def _toggle_dropdown(self, event=None):
        if self._dropdown_open:
            self._dropdown.hide()
            self._sync_dropdown_state()
            return

        self._dropdown.name_lbl.setText(self._name_display.text())
        self._dropdown.show_for(self._profile_block)
        self._sync_dropdown_state()

    def _default_update_profile(self, new_name, new_username, new_email=None):
        from controllers.account_controller import AccountController

        return AccountController().update_profile(new_name, new_username, new_email)

    def _default_change_password(self, current, new):
        from controllers.account_controller import AccountController

        return AccountController().change_password(current, new)

    def _default_logout(self):
        from controllers.login_controller import LoginController

        LoginController.logout()

    def _default_create_products_page(self):
        from controllers.owner_product_controller import OwnerProductController
        from views.owner_products_view import OwnerProductsView

        self._embedded_product_page = OwnerProductsView(show_topbar=False)
        self._owner_product_controller = OwnerProductController().attach_view(self._embedded_product_page)
        self._embedded_product_page.bind_controller(self._owner_product_controller, request_initial=True)
        return self._embedded_product_page

    def _default_create_transactions_page(self):
        from controllers.admin_transaction_controller import AdminTransactionController
        from views.owner_transactions_view import OwnerTransactionsView

        self._owner_transaction_controller = AdminTransactionController()
        self._embedded_transaction_page = OwnerTransactionsView(
            show_topbar=False,
            controller=self._owner_transaction_controller,
        )
        return self._embedded_transaction_page

    def _ensure_transaction_page_controller(self):
        from controllers.admin_transaction_controller import AdminTransactionController

        self._owner_transaction_controller = AdminTransactionController()
        self._embedded_transaction_page.bind_controller(
            self._owner_transaction_controller,
            request_initial=True,
        )

    def _default_create_reports_page(self):
        from controllers.report_controller import ReportController
        from views.report_view import ReportView

        self._report_controller = ReportController()
        self._embedded_reports_page = ReportView(
            user=self._user,
            show_topbar=False,
            controller=self._report_controller,
        )
        return self._embedded_reports_page

    def _default_create_delivery_logs_page(self):
        from controllers.delivery_logs_controller import DeliveryLogsController
        from views.delivery_logs_view import DeliveryLogsView

        self._owner_delivery_log_controller = DeliveryLogsController()
        self._embedded_delivery_logs_page = DeliveryLogsView(
            show_topbar=False,
            controller=self._owner_delivery_log_controller,
        )
        return self._embedded_delivery_logs_page

    def _ensure_delivery_logs_page_controller(self):
        from controllers.delivery_logs_controller import DeliveryLogsController

        self._owner_delivery_log_controller = DeliveryLogsController()
        self._embedded_delivery_logs_page.bind_controller(
            self._owner_delivery_log_controller,
            request_initial=True,
        )

    def _default_create_audit_logs_page(self):
        from controllers.audit_logs_controller import AuditLogsController
        from views.audit_logs_view import AuditLogsView

        self._owner_audit_logs_controller = AuditLogsController()
        self._embedded_audit_logs_page = AuditLogsView(
            show_topbar=False,
            controller=self._owner_audit_logs_controller,
        )
        return self._embedded_audit_logs_page

    def _ensure_audit_logs_page_controller(self):
        from controllers.audit_logs_controller import AuditLogsController

        self._owner_audit_logs_controller = AuditLogsController()
        self._embedded_audit_logs_page.bind_controller(
            self._owner_audit_logs_controller,
            request_initial=True,
        )

    def _sync_dropdown_state(self):
        self._dropdown_open = self._dropdown.isVisible()
        self._chevron.setText("▴" if self._dropdown_open else "▾")

    def _open_edit_name(self):
        self._dropdown.hide()
        self._sync_dropdown_state()
        self._name_modal.open(
            str(self._user.get("full_name", "") or "").strip(),
            str(self._user.get("username", "") or "").strip(),
            str(self._user.get("email", "") or "").strip(),
            self._update_name,
        )

    def _open_change_password(self):
        self._dropdown.hide()
        self._sync_dropdown_state()
        self._pass_modal.open(self._do_change_password)

    def _refresh_profile_texts(self):
        display_name = self._display_name()
        self._name_display.setText(display_name)
        self._dropdown.name_lbl.setText(display_name)
        if hasattr(self, "_greeting_title"):
            hour = datetime.datetime.now().hour
            greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
            self._greeting_title.setText(f"{greet}, {self._greeting_name()}")

    def _update_name(self, new_name, new_username, new_email=None):
        try:
            self._user = self._action_handlers["update_profile"](
                new_name, new_username, new_email
            )
            self._refresh_profile_texts()
            show_ok_success_popup(self, "Profile Updated", "Your profile has been updated.")
            return True
        except ValueError as exc:
            self._name_modal.show_error_message(str(exc))
            return False
        except Exception as exc:
            from utils.error_handler import clean_db_error

            self._name_modal.show_error_message(clean_db_error(exc))
            return False

    def _do_change_password(self, current, new):
        try:
            self._action_handlers["change_password"](current, new)
            show_ok_success_popup(self, "Password Updated", "Your password has been updated.")
            return True
        except ValueError as exc:
            self._pass_modal.show_error_message(str(exc))
            return False
        except Exception as exc:
            from utils.error_handler import clean_db_error

            self._pass_modal.show_error_message(clean_db_error(exc))
            return False

    def _sign_out(self):
        self._action_handlers["logout"]()
        from views.login_view import LoginView

        self._login_view = LoginView()
        self._login_view.show()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self._dropdown_open:
            self._dropdown.hide()
            self._sync_dropdown_state()
        if hasattr(self, "_notification_dropdown") and self._notification_dropdown.isVisible():
            self._notification_dropdown.hide()
        if hasattr(self, "_message_panel") and self._message_panel.isVisible():
            self._message_panel.hide()
        super().mousePressEvent(event)


def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setFont(inter(11))
    w = OwnerDashboardView(user={"full_name": "GNC Owner", "role": "owner"})
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
