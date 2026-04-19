import sys
import os
import datetime
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QTime, QDate, QPoint
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QPainter,
    QPixmap, QPen
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QGraphicsDropShadowEffect, QStackedWidget, QMessageBox
)
from controllers.account_controller import AccountController
from controllers.login_controller import LoginController
from controllers.delivery_controller import DeliveryController
from controllers.product_controller import ProductController

# ── Project root & asset paths ────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
PLAYFAIR_FAMILY = "Playfair Display"
INTER_FAMILY = "Inter"

# ── Colors (exact from HTML) ──────────────────────────────────────────────────
TEAL       = "#1A7A6E"
TEAL_DARK  = "#145F55"
TEAL_MID   = "#1d8a7c"
TEAL_LIGHT = "#2aa898"
TEAL_PALE  = "#e8f5f3"
TEAL_PALE2 = "#d0ede9"
WHITE      = "#ffffff"
GRAY_1     = "#f4f5f4"
GRAY_2     = "#e6eae9"
GRAY_3     = "#c4ccc9"
GRAY_4     = "#7a8a87"
GRAY_5     = "#3a4a47"
GREEN      = "#1a6b3a"
GREEN_BG   = "#eaf3ee"
AMBER      = "#8a5a00"
AMBER_BG   = "#fef5e0"
RED        = "#8a1a1a"
RED_BG     = "#fdeaea"


def load_fonts():
    global PLAYFAIR_FAMILY, INTER_FAMILY

    fonts = [
        "PlayfairDisplay-Medium.ttf",
        "PlayfairDisplay-SemiBold.ttf",
        "Inter_18pt-Regular.ttf",
        "Inter_18pt-Medium.ttf",
        "Inter_18pt-SemiBold.ttf",
        "Inter_24pt-Bold.ttf",
    ]
    for f in fonts:
        path = os.path.join(FONTS_DIR, f)
        if os.path.exists(path):
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1 and f.startswith("PlayfairDisplay"):
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    PLAYFAIR_FAMILY = families[0]
            if font_id != -1 and f == "Inter_18pt-Regular.ttf":
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    INTER_FAMILY = families[0]


def font(family, size, weight=QFont.Normal):
    try:
        safe_size = max(1, int(size))
    except (TypeError, ValueError):
        safe_size = 11
    f = QFont(family, safe_size)
    f.setWeight(weight)
    return f


def playfair(size, weight=QFont.Normal):
    return font(PLAYFAIR_FAMILY, size, weight)


def inter(size, weight=QFont.Normal):
    return font(INTER_FAMILY, size, weight)


def owner_scrollbar_qss():
    return f"""
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px 4px 0;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {TEAL};
        min-height: 28px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEAL_MID};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 0 2px 2px 2px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {TEAL};
        min-width: 28px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {TEAL_MID};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: transparent;
    }}
    """


# ── Thin horizontal divider ───────────────────────────────────────────────────
class HDivider(QFrame):
    def __init__(self, color=GRAY_2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{color};border:none;")


# ── KPI card with colored top border ─────────────────────────────────────────
class KpiCard(QFrame):
    def __init__(self, label, value, desc, top_color, parent=None):
        super().__init__(parent)
        self._top_color = QColor(top_color)
        self.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {GRAY_2};
                border-radius: 6px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(126)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 12)
        lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setFont(inter(10, QFont.DemiBold))
        lbl.setMinimumHeight(16)
        lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.5px;background:transparent;border:none;")

        val = QLabel(value)
        val.setFont(playfair(30, QFont.Medium))
        val.setMinimumHeight(42)
        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        dsc = QLabel(desc)
        dsc.setFont(inter(11))
        dsc.setMinimumHeight(18)
        dsc.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addWidget(dsc)
        lay.addStretch()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(self._top_color)
        p.drawRoundedRect(0, 0, self.width(), 3, 1, 1)


# ── Profile dropdown ──────────────────────────────────────────────────────────
class ProfileDropdown(QFrame):
    def __init__(self, parent=None):
        super().__init__(None)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setObjectName("profileDropdown")

        self.setStyleSheet("""
            QFrame#profileDropdown {
                background: #e9e9e9;
                border: 1px solid #cfcfcf;
                border-radius: 8px;
            }
        """)
        self.setFixedWidth(220)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background:transparent; border:none; border-bottom:1px solid #d3d3d3;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(16, 12, 16, 12)
        h_lay.setSpacing(3)

        signed = QLabel("SIGNED IN AS")
        signed.setFont(inter(8, QFont.DemiBold))
        signed.setStyleSheet("color:#7f7f7f; letter-spacing:2px; background:transparent; border:none;")

        self.name_lbl = QLabel("")
        self.name_lbl.setFont(inter(13, QFont.Medium))
        self.name_lbl.setStyleSheet(f"color:{TEAL_DARK}; background:transparent; border:none;")

        h_lay.addWidget(signed)
        h_lay.addWidget(self.name_lbl)
        lay.addWidget(header)

        self.edit_name_btn = self._item("Edit profile")
        self.change_pass_btn = self._item("Change password")

        lay.addWidget(self.edit_name_btn)
        lay.addWidget(HDivider("#d3d3d3"))
        lay.addWidget(self.change_pass_btn)

    def _item(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(inter(12))
        btn.setFixedHeight(46)
        btn.setStyleSheet(f"""
            QPushButton {{
                color:#3f4a48;
                background:transparent;
                border:none;
                text-align:left;
                padding:0 16px;
            }}
            QPushButton:hover {{
                background:#dddddd;
                color:{TEAL_DARK};
            }}
        """)
        return btn


# ── Modal base ────────────────────────────────────────────────────────────────
class ModalOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(0,0,0,120);")
        self.hide()

    def mousePressEvent(self, event):
        event.accept()

    def _center_modal(self):
        if not hasattr(self, "_modal"):
            return
        x = max(0, (self.width() - self._modal.width()) // 2)
        y = max(0, (self.height() - self._modal.height()) // 2)
        self._modal.move(x, y)

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)


class Modal(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._drag_active = False
        self._drag_offset = QPoint()
        self.setObjectName("modal")
        self.setFixedWidth(340)
        self.setStyleSheet(f"""
            QFrame#modal {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(18, 16, 14, 14)

        title_lbl = QLabel(title)
        title_lbl.setFont(playfair(15))
        title_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        self._lay.addWidget(header)

        self.body = QWidget()
        self.body.setStyleSheet("background:transparent;border:none;")
        self.body_lay = QVBoxLayout(self.body)
        self.body_lay.setContentsMargins(18, 18, 18, 18)
        self.body_lay.setSpacing(14)
        self._lay.addWidget(self.body)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(f"background:transparent;border:none;border-top:1px solid {GRAY_2};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(18, 12, 18, 12)
        f_lay.setSpacing(8)
        f_lay.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFont(inter(12, QFont.Medium))
        self.cancel_btn.setFixedHeight(30)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton{{color:{GRAY_5};background:{WHITE};border:1px solid {GRAY_2};border-radius:4px;padding:0 16px;}}
            QPushButton:hover{{background:{GRAY_1};}}
        """)
        self.cancel_btn.clicked.connect(self._on_close)

        self.save_btn = QPushButton("Save changes")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFont(inter(12, QFont.Medium))
        self.save_btn.setFixedHeight(30)
        self.save_btn.setStyleSheet(f"""
            QPushButton{{color:{WHITE};background:{TEAL};border:1px solid {TEAL};border-radius:4px;padding:0 16px;}}
            QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
        """)

        f_lay.addWidget(self.cancel_btn)
        f_lay.addWidget(self.save_btn)
        self._lay.addWidget(footer)

    def _on_close(self):
        self.parent().hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 52:
            self._drag_active = True
            self._drag_offset = event.position().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and self.parent() is not None:
            new_pos = self.mapToParent(event.position().toPoint() - self._drag_offset)
            max_x = max(0, self.parent().width() - self.width())
            max_y = max(0, self.parent().height() - self.height())
            clamped_x = min(max(0, new_pos.x()), max_x)
            clamped_y = min(max(0, new_pos.y()), max_y)
            self.move(clamped_x, clamped_y)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)

    def _field(self, label_text, placeholder, echo=QLineEdit.Normal):
        grp = QWidget()
        grp.setStyleSheet("background:transparent;border:none;")
        g_lay = QVBoxLayout(grp)
        g_lay.setContentsMargins(0, 0, 0, 0)
        g_lay.setSpacing(6)

        lbl = QLabel(label_text)
        lbl.setFont(inter(10, QFont.DemiBold))
        lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.2px;background:transparent;border:none;")

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setEchoMode(echo)
        inp.setFont(inter(12))
        inp.setFixedHeight(32)
        inp.setStyleSheet(f"""
            QLineEdit{{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:4px;
                padding:0 10px;
            }}
            QLineEdit:focus{{border-color:{TEAL};}}
        """)
        g_lay.addWidget(lbl)
        g_lay.addWidget(inp)
        return grp, inp


# ── Edit name modal ───────────────────────────────────────────────────────────
class EditNameModal(ModalOverlay):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._modal = Modal("Edit Profile", self)
        grp1, self.name_input = self._modal._field("FULL NAME", "Enter your full name")
        grp2, self.username_input = self._modal._field("USERNAME", "Enter your username")
        self._modal.body_lay.addWidget(grp1)
        self._modal.body_lay.addWidget(grp2)

        self.err_lbl = QLabel("")
        self.err_lbl.setFont(inter(11))
        self.err_lbl.setStyleSheet(f"color:{RED};background:transparent;border:none;")
        self.err_lbl.hide()
        self._modal.body_lay.addWidget(self.err_lbl)

        self._modal.save_btn.setText("Save changes")
        self._modal.save_btn.clicked.connect(self._save)

    def open(self, current_name, current_username, callback):
        self._callback = callback
        self.name_input.setText(current_name)
        self.username_input.setText(current_username)
        self.err_lbl.hide()
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._center_modal()
        self.show()
        self.raise_()

    def _save(self):
        full_name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        if not full_name:
            self.err_lbl.setText("Full name cannot be empty.")
            self.err_lbl.show()
            return
        if not username:
            self.err_lbl.setText("Username cannot be empty.")
            self.err_lbl.show()
            return
        if hasattr(self, "_callback"):
            if self._callback(full_name, username) is False:
                return
        self.hide()


# ── Change password modal ─────────────────────────────────────────────────────
class ChangePasswordModal(ModalOverlay):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._modal = Modal("Change Password", self)
        self._modal.save_btn.setText("Update password")

        grp1, self.current_pass = self._modal._field("CURRENT PASSWORD",  "Enter current password",  QLineEdit.Password)
        grp2, self.new_pass     = self._modal._field("NEW PASSWORD",       "Enter new password",       QLineEdit.Password)
        grp3, self.confirm_pass = self._modal._field("CONFIRM NEW PASSWORD","Confirm new password",    QLineEdit.Password)

        for g in [grp1, grp2, grp3]:
            self._modal.body_lay.addWidget(g)

        self.err_lbl = QLabel("")
        self.err_lbl.setFont(inter(11))
        self.err_lbl.setStyleSheet(f"color:{RED};background:transparent;border:none;")
        self.err_lbl.hide()
        self._modal.body_lay.addWidget(self.err_lbl)

        self._modal.save_btn.clicked.connect(self._save)

    def open(self, callback):
        self._callback = callback
        self.current_pass.clear()
        self.new_pass.clear()
        self.confirm_pass.clear()
        self.err_lbl.hide()
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._center_modal()
        self.show()
        self.raise_()

    def _save(self):
        np = self.new_pass.text()
        cp = self.confirm_pass.text()
        if not np or np != cp:
            self.err_lbl.setText("Passwords do not match.")
            self.err_lbl.show()
            return
        if hasattr(self, "_callback"):
            if self._callback(self.current_pass.text(), np) is False:
                return
        self.hide()


# ── Person Icon Widget ───────────────────────────────────────────────────────
class PersonIconWidget(QWidget):
    def __init__(self, bg_color, icon_path, parent=None):
        super().__init__(parent)
        self.bg_color = QColor(bg_color)
        self.setFixedSize(40, 40)
        
        # Load icon image
        self.icon_pixmap = QPixmap(icon_path)
        if not self.icon_pixmap.isNull():
            self.icon_pixmap = self.icon_pixmap.scaledToWidth(26, Qt.SmoothTransformation)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Draw background circle
        p.setBrush(self.bg_color)
        p.setPen(QPen(QColor(255, 255, 255, 76), 1))
        p.drawEllipse(0, 0, self.width(), self.height())

        # Draw icon centered
        if not self.icon_pixmap.isNull():
            x = (self.width() - self.icon_pixmap.width()) / 2
            y = (self.height() - self.icon_pixmap.height()) / 2
            p.drawPixmap(int(x), int(y), self.icon_pixmap)


class NavItemWidget(QWidget):
    def __init__(self, active=False, parent=None):
        super().__init__(parent)
        self.active = active
        self.hovered = False
        self.setFixedHeight(36)
        self.setStyleSheet("background:transparent;border:none;")

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        if self.active:
            p.fillRect(self.rect(), QColor(255, 255, 255, 26))
            p.fillRect(0, 0, 2, self.height(), QColor("#a8e6df"))
        elif self.hovered:
            p.fillRect(self.rect(), QColor(255, 255, 255, 16))

    def set_active(self, active):
        self.active = active
        self.update()


# ── Dashboard window ──────────────────────────────────────────────────────────
class DashboardView(QMainWindow):
    def __init__(self, user=None, controller=None):
        super().__init__()
        load_fonts()  # Ensure custom fonts are loaded
        self._user    = user or {"full_name": "", "role": "admin"}
        self._controller = None
        self._dashboard_data = self._empty_dashboard_data()
        self._dashboard_refresh_interval_ms = 15000
        self._account_controller = AccountController()
        self._dropdown_open = False
        self.setWindowTitle("G and C LPG Trading — Delivery Scheduling & Tracking System")
        self._build_ui()
        if controller is not None:
            self.bind_controller(controller, request_initial=True)
        self.showFullScreen()

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

        new_page = self._build_content()
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
            "kpi_counts": {
                "total_today": 0,
                "pending_today": 0,
                "in_transit_today": 0,
                "unpaid_count": 0,
            },
            "todays_deliveries": [],
            "unpaid_deliveries": [],
        }

    def _normalize_dashboard_data(self, data):
        normalized = self._empty_dashboard_data()
        if not isinstance(data, dict):
            return normalized

        kpis = data.get("kpi_counts")
        if isinstance(kpis, dict):
            normalized["kpi_counts"].update(kpis)

        todays = data.get("todays_deliveries")
        if isinstance(todays, list):
            normalized["todays_deliveries"] = todays

        unpaid = data.get("unpaid_deliveries")
        if isinstance(unpaid, list):
            normalized["unpaid_deliveries"] = unpaid

        return normalized

    @staticmethod
    def _to_int(value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _text(value, fallback=""):
        text = str(value or "").strip()
        return text if text else fallback

    @staticmethod
    def _money(value, formatted=None):
        if formatted not in (None, ""):
            return f"PHP {formatted}"
        try:
            return f"PHP {float(value or 0):,.2f}"
        except (TypeError, ValueError):
            return "PHP 0.00"

    def _display_name(self):
        full_name = str(self._user.get("full_name", "") or "").strip()
        if full_name:
            return full_name
        username = str(self._user.get("username", "") or "").strip()
        if username:
            return username
        return "User"

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
        self._dashboard_page = self._build_content()
        self._content_stack.addWidget(self._dashboard_page)
        main_lay.addWidget(self._content_stack)
        root.addWidget(main_col)

        self._dashboard_refresh_timer = QTimer(self)
        self._dashboard_refresh_timer.setInterval(self._dashboard_refresh_interval_ms)
        self._dashboard_refresh_timer.timeout.connect(self._refresh_dashboard_if_visible)

        # Modals — children of central so they cover everything
        self._name_modal = EditNameModal(central)
        self._pass_modal = ChangePasswordModal(central)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = QWidget()
        sb.setFixedWidth(280)
        sb.setStyleSheet(f"""
            QWidget {{
                background:{TEAL_DARK};
                border-right:1px solid {TEAL};
            }}
        """)
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo block
        logo = QWidget()
        logo.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid rgba(255,255,255,0.1);")
        l_lay = QVBoxLayout(logo)
        l_lay.setContentsMargins(18, 20, 18, 20)
        l_lay.setSpacing(2)

        name_lbl = QLabel("G and C LPG Trading")
        name_lbl.setFont(playfair(13, QFont.DemiBold))
        name_lbl.setStyleSheet("color:#a8e6df;letter-spacing:0.5px;background:transparent;border:none;")

        sub_lbl = QLabel("DELIVERY & TRACKING SYSTEM")
        sub_lbl.setFont(inter(9, QFont.Normal))
        sub_lbl.setStyleSheet("color:rgba(255,255,255,0.4);letter-spacing:1.5px;background:transparent;border:none;")

        l_lay.addWidget(name_lbl)
        l_lay.addWidget(sub_lbl)
        lay.addWidget(logo)

        # Profile block
        self._profile_block = QWidget()
        self._profile_block.setStyleSheet(f"""
            QWidget {{
                background:transparent;
                border:none;
                border-bottom:1px solid rgba(255,255,255,0.1);
            }}
            QWidget:hover {{ background:rgba(255,255,255,0.07); }}
        """)
        self._profile_block.setCursor(Qt.PointingHandCursor)
        self._profile_block.setFixedHeight(64)
        self._profile_block.mousePressEvent = self._toggle_dropdown

        p_lay = QHBoxLayout(self._profile_block)
        p_lay.setContentsMargins(18, 10, 14, 8)
        p_lay.setSpacing(10)

        icon_path = os.path.join(FONTS_DIR, "..", "icon.png")
        avatar = PersonIconWidget(TEAL, icon_path)

        info = QVBoxLayout()
        info.setSpacing(0)
        info.setContentsMargins(0, 0, 0, 0)
        self._name_display = QLabel(self._display_name())
        self._name_display.setFont(inter(12, QFont.Medium))
        self._name_display.setStyleSheet("color:#fff;background:transparent;border:none;")

        role_lbl = QLabel("Administrator")
        role_lbl.setFont(inter(10, QFont.Normal))
        role_lbl.setStyleSheet("color:rgba(255,255,255,0.5);letter-spacing:0.3px;background:transparent;border:none;")
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

        # Dropdown (absolute positioned later)
        self._dropdown = ProfileDropdown()
        self._dropdown.edit_name_btn.clicked.connect(self._open_edit_name)
        self._dropdown.change_pass_btn.clicked.connect(self._open_change_password)

        # Nav scroll
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("background:transparent;border:none;")

        nav_w = QWidget()
        nav_w.setStyleSheet("background:transparent;")
        nav_lay = QVBoxLayout(nav_w)
        nav_lay.setContentsMargins(0, 0, 0, 0)
        nav_lay.setSpacing(0)

        # Main section
        nav_lay.addWidget(self._nav_section("Main"))
        self.btn_dashboard    = self._nav_item("Dashboard", active=True)
        self.btn_deliveries   = self._nav_item("Deliveries")
        self.btn_customers    = self._nav_item("Customers")
        for b in [self.btn_dashboard, self.btn_deliveries, self.btn_customers]:
            nav_lay.addWidget(b)

        self.btn_dashboard.mousePressEvent = lambda event: self._show_dashboard_page()
        self.btn_deliveries.mousePressEvent = lambda event: self._show_deliveries_page()
        self.btn_customers.mousePressEvent = lambda event: self._show_customers_page()

        nav_lay.addWidget(self._nav_section("Management"))
        self.btn_products     = self._nav_item("LPG Products")
        self.btn_transactions = self._nav_item("Transactions")
        for b in [self.btn_products, self.btn_transactions]:
            nav_lay.addWidget(b)

        self.btn_products.mousePressEvent = lambda event: self._show_products_page()
        self.btn_transactions.mousePressEvent = lambda event: self._show_transactions_page()

        nav_lay.addWidget(self._nav_section("Records"))
        self.btn_del_logs     = self._nav_item("Delivery Logs")
        self.btn_audit_logs   = self._nav_item("Audit Logs")
        for b in [self.btn_del_logs, self.btn_audit_logs]:
            nav_lay.addWidget(b)

        self.btn_del_logs.mousePressEvent = lambda event: self._show_delivery_logs_page()
        self.btn_audit_logs.mousePressEvent = lambda event: self._show_audit_logs_page()

        nav_lay.addStretch()
        nav_scroll.setWidget(nav_w)
        lay.addWidget(nav_scroll)

        # Footer sign out
        footer = QWidget()
        footer.setStyleSheet(f"background:transparent;border:none;border-top:1px solid rgba(255,255,255,0.1);")
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
        signout.setStyleSheet(f"""
            QPushButton{{color:rgba(255,255,255,0.35);background:transparent;border:none;text-align:left;padding:0;}}
            QPushButton:hover{{color:rgba(255,255,255,0.65);}}
        """)
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
        lbl.setStyleSheet("color:rgba(255,255,255,0.28);letter-spacing:2px;background:transparent;border:none;")
        lay.addWidget(lbl)
        return w

    # SVG icons as unicode approximations matching HTML icons
    _NAV_ICONS = {
        "Dashboard":     "dashboard_icon",  # Image icon
        "Deliveries":    "deliveries_icon",  # Image icon
        "Customers":     "customers_icon",  # Image icon
        "LPG Products":  "products_icon",  # Image icon
        "Transactions":  "transactions_icon",
        "Delivery Logs": "logs_icon",
        "Audit Logs":    "logs_icon",
    }

    def _nav_item(self, text, active=False, badge=None):
        w = NavItemWidget(active=active)
        w.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 18, 0)
        row.setSpacing(10)

        # Left border indicator — painted by NavItemWidget
        # Spacer to account for left border width
        row.addSpacing(16)

        # Icon
        icon_key = self._NAV_ICONS.get(text, "placeholder")
        icon = QLabel()
        icon.setFixedSize(30, 20)
        icon.setAlignment(Qt.AlignCenter)
        
        # Image-only icons; if missing, show a tiny placeholder dot.
        icon_path = os.path.join(BASE_DIR, "assets", f"{icon_key}.png")
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            image_icon_sizes = {
                "dashboard_icon": 18,
                "deliveries_icon": 18,
                "customers_icon": 18,
                "products_icon": 18,
                "audit_icon": 18,
                "transactions_icon": 18,
                "delivery_logs_icon": 18,
            }
            target_width = image_icon_sizes.get(icon_key, 18)
            pixmap = pixmap.scaledToWidth(target_width, Qt.SmoothTransformation)
            icon.setPixmap(pixmap)
        else:
            icon.setText("•")
            icon.setFont(inter(10, QFont.Medium))
        
        if active:
            icon.setStyleSheet("color:rgba(255,255,255,0.9);background:transparent;border:none;")
        else:
            icon.setStyleSheet("color:rgba(255,255,255,0.55);background:transparent;border:none;")
        row.addWidget(icon)

        lbl = QLabel(text)
        lbl.setFont(inter(10, QFont.Medium if active else QFont.Normal))
        if active:
            lbl.setStyleSheet("color:#fff;background:transparent;border:none;")
        else:
            lbl.setStyleSheet("color:rgba(255,255,255,0.55);background:transparent;border:none;")
        row.addWidget(lbl)
        row.addStretch()

        if badge:
            b = QLabel(badge)
            b.setFont(inter(10, QFont.DemiBold))
            b.setFixedHeight(18)
            b.setAlignment(Qt.AlignCenter)
            b.setStyleSheet(f"background:#a8e6df;color:{TEAL_DARK};border-radius:9px;padding:0 6px;min-width:18px;border:none;")
            row.addWidget(b)

        icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        if badge:
            b.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        w._icon_lbl = icon
        w._text_lbl = lbl
        w._default_text = text
        self._set_nav_item_style(w, active)

        return w

    def _set_nav_item_style(self, nav_item, active):
        nav_item.set_active(active)
        if hasattr(nav_item, "_icon_lbl"):
            nav_item._icon_lbl.setStyleSheet(
                "color:rgba(255,255,255,0.9);background:transparent;border:none;"
                if active else
                "color:rgba(255,255,255,0.55);background:transparent;border:none;"
            )
        if hasattr(nav_item, "_text_lbl"):
            nav_item._text_lbl.setFont(inter(10, QFont.Medium if active else QFont.Normal))
            nav_item._text_lbl.setStyleSheet(
                "color:#fff;background:transparent;border:none;"
                if active else
                "color:rgba(255,255,255,0.55);background:transparent;border:none;"
            )

    def _set_active_sidebar_item(self, active_item):
        for nav_item in [
            self.btn_dashboard,
            self.btn_deliveries,
            self.btn_customers,
            self.btn_products,
            self.btn_transactions,
            self.btn_del_logs,
            self.btn_audit_logs,
        ]:
            self._set_nav_item_style(nav_item, nav_item is active_item)

    def _show_dashboard_page(self):
        self._content_stack.setCurrentWidget(self._dashboard_page)
        self._set_active_sidebar_item(self.btn_dashboard)
        self._set_topbar_title("DASHBOARD")
        self.reload_dashboard(silent=True)
        self._sync_dashboard_refresh_timer()

    def _show_deliveries_page(self):
        if not hasattr(self, "_embedded_delivery_page") or self._embedded_delivery_page is None:
            from views.admin_delivery_view import DeliveryView
            self._embedded_delivery_page = DeliveryView(show_topbar=False, controller=DeliveryController())
            self._content_stack.addWidget(self._embedded_delivery_page)
        elif getattr(self._embedded_delivery_page, "_controller", None) is None:
            self._embedded_delivery_page.bind_controller(DeliveryController())
        elif hasattr(self._embedded_delivery_page, "reload_data"):
            self._embedded_delivery_page.reload_data()

        self._content_stack.setCurrentWidget(self._embedded_delivery_page)
        self._set_active_sidebar_item(self.btn_deliveries)
        self._set_topbar_title("DELIVERIES")
        self._sync_dashboard_refresh_timer()

    def _show_customers_page(self):
        if not hasattr(self, "_embedded_customer_page") or self._embedded_customer_page is None:
            from views.customer_view import CustomerView
            self._embedded_customer_page = CustomerView(show_topbar=False)
            self._content_stack.addWidget(self._embedded_customer_page)

        self._content_stack.setCurrentWidget(self._embedded_customer_page)
        self._set_active_sidebar_item(self.btn_customers)
        self._set_topbar_title("CUSTOMERS")
        self._sync_dashboard_refresh_timer()

    def _show_products_page(self):
        if not hasattr(self, "_embedded_product_page") or self._embedded_product_page is None:
            from views.admin_product_view import ProductView
            self._embedded_product_page = ProductView(show_topbar=False)
            self._content_stack.addWidget(self._embedded_product_page)
            # Wire controller to keep MVC boundaries clean and load data.
            self._product_controller = ProductController().attach_view(self._embedded_product_page)
            self._embedded_product_page.bind_controller(self._product_controller, request_initial=True)

        self._content_stack.setCurrentWidget(self._embedded_product_page)
        self._set_active_sidebar_item(self.btn_products)
        self._set_topbar_title("LPG PRODUCTS")
        self._sync_dashboard_refresh_timer()

    def _show_transactions_page(self):
        if not hasattr(self, "_embedded_transaction_page") or self._embedded_transaction_page is None:
            from controllers.admin_transaction_controller import AdminTransactionController
            from views.admin_transaction_view import TransactionView
            self._transaction_controller = AdminTransactionController()
            self._embedded_transaction_page = TransactionView(
                show_topbar=False, controller=self._transaction_controller
            )
            self._content_stack.addWidget(self._embedded_transaction_page)
        elif getattr(self, "_transaction_controller", None) is None:
            from controllers.admin_transaction_controller import AdminTransactionController
            self._transaction_controller = AdminTransactionController()
            self._embedded_transaction_page.bind_controller(self._transaction_controller, request_initial=True)

        self._content_stack.setCurrentWidget(self._embedded_transaction_page)
        self._set_active_sidebar_item(self.btn_transactions)
        self._set_topbar_title("TRANSACTIONS")
        self._sync_dashboard_refresh_timer()

    def _show_delivery_logs_page(self):
        if not hasattr(self, "_embedded_delivery_logs_page") or self._embedded_delivery_logs_page is None:
            from controllers.delivery_logs_controller import DeliveryLogsController
            from views.delivery_logs_view import DeliveryLogsView
            self._delivery_log_controller = DeliveryLogsController()
            self._embedded_delivery_logs_page = DeliveryLogsView(
                show_topbar=False,
                controller=self._delivery_log_controller,
            )
            self._content_stack.addWidget(self._embedded_delivery_logs_page)
        elif getattr(self, "_delivery_log_controller", None) is None:
            from controllers.delivery_logs_controller import DeliveryLogsController
            self._delivery_log_controller = DeliveryLogsController()
            self._embedded_delivery_logs_page.bind_controller(
                self._delivery_log_controller,
                request_initial=True,
            )

        self._content_stack.setCurrentWidget(self._embedded_delivery_logs_page)
        self._set_active_sidebar_item(self.btn_del_logs)
        self._set_topbar_title("DELIVERY LOGS")
        self._sync_dashboard_refresh_timer()

    def _show_audit_logs_page(self):
        if not hasattr(self, "_embedded_audit_logs_page") or self._embedded_audit_logs_page is None:
            from controllers.audit_logs_controller import AuditLogsController
            from views.audit_logs_view import AuditLogsView
            self._audit_logs_controller = AuditLogsController()
            self._embedded_audit_logs_page = AuditLogsView(
                show_topbar=False,
                controller=self._audit_logs_controller,
            )
            self._content_stack.addWidget(self._embedded_audit_logs_page)
        elif getattr(self, "_audit_logs_controller", None) is None:
            from controllers.audit_logs_controller import AuditLogsController
            self._audit_logs_controller = AuditLogsController()
            self._embedded_audit_logs_page.bind_controller(
                self._audit_logs_controller,
                request_initial=True,
            )

        self._content_stack.setCurrentWidget(self._embedded_audit_logs_page)
        self._set_active_sidebar_item(self.btn_audit_logs)
        self._set_topbar_title("AUDIT LOGS")
        self._sync_dashboard_refresh_timer()

    def _set_topbar_title(self, title):
        if hasattr(self, "_breadcrumb_lbl") and self._breadcrumb_lbl is not None:
            self._breadcrumb_lbl.setText(title)

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

    # ── Dropdown toggle ───────────────────────────────────────────────────────
    def _toggle_dropdown(self, event=None):
        if self._dropdown_open:
            self._dropdown.hide()
            self._dropdown_open = False
            self._chevron.setText("▾")
        else:
            self._dropdown.name_lbl.setText(self._name_display.text())

            global_pos = self._profile_block.mapToGlobal(
                QPoint(
                    self._profile_block.width() - self._dropdown.width() - 8,
                    self._profile_block.height() + 2
                )
            )

            self._dropdown.move(global_pos)
            self._dropdown.show()
            self._sync_dropdown_state()
            self._dropdown.raise_()

            self._dropdown_open = True
            self._chevron.setText("▴")
    
    def _sync_dropdown_state(self):
        self._dropdown_open = self._dropdown.isVisible()
        self._chevron.setText("▴" if self._dropdown_open else "▾")

    def _open_edit_name(self):
        self._dropdown.hide()
        self._dropdown_open = False
        self._chevron.setText("▾")
        self._name_modal.open(
            str(self._user.get("full_name", "") or "").strip(),
            str(self._user.get("username", "") or "").strip(),
            self._update_name,
        )

    def _open_change_password(self):
        self._dropdown.hide()
        self._dropdown_open = False
        self._chevron.setText("▾")
        self._pass_modal.open(self._do_change_password)

    def _refresh_profile_texts(self):
        display_name = self._display_name()
        self._name_display.setText(display_name)
        self._dropdown.name_lbl.setText(display_name)
        if hasattr(self, "_greeting_title"):
            hour = datetime.datetime.now().hour
            greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
            self._greeting_title.setText(f"{greet}, {self._greeting_name()}")

    def _update_name(self, new_name, new_username):
        try:
            self._user = self._account_controller.update_profile(new_name, new_username)
            self._refresh_profile_texts()
            QMessageBox.information(self, "Profile Updated", "Your profile has been updated.")
            return True
        except Exception as exc:
            QMessageBox.warning(self, "Update Failed", str(exc))
            return False

    def _do_change_password(self, current, new):
        try:
            self._account_controller.change_password(current, new)
            QMessageBox.information(self, "Password Updated", "Your password has been updated.")
            return True
        except Exception as exc:
            QMessageBox.warning(self, "Update Failed", str(exc))
            return False

    def _open_customer_view(self):
        from views.customer_view import CustomerView

        if not hasattr(self, "_customer_window") or self._customer_window is None:
            self._customer_window = QMainWindow()
            self._customer_window.setWindowTitle("G and C LPG Trading - Customer Management")
            page = CustomerView(show_topbar=True)
            self._customer_window.setCentralWidget(page)
            self._customer_window.showMaximized()
        else:
            self._customer_window.showMaximized()
            self._customer_window.raise_()
            self._customer_window.activateWindow()

        return self._customer_window.centralWidget()

    def _open_delivery_view(self):
        from views.admin_delivery_view import DeliveryView

        if not hasattr(self, "_delivery_window") or self._delivery_window is None:
            self._delivery_window = QMainWindow()
            self._delivery_window.setWindowTitle("G and C LPG Trading - Delivery Management")
            page = DeliveryView(show_topbar=True, controller=DeliveryController())
            self._delivery_window.setCentralWidget(page)
            self._delivery_window.showMaximized()
        else:
            self._delivery_window.showMaximized()
            self._delivery_window.raise_()
            self._delivery_window.activateWindow()

        return self._delivery_window.centralWidget()

    def _quick_action_add_customer(self, event=None):
        self._show_customers_page()
        page = getattr(self, "_embedded_customer_page", None)
        if page is not None and hasattr(page, "_open_add"):
            page._open_add()

    def _quick_action_new_delivery(self, event=None):
        self._show_deliveries_page()
        page = getattr(self, "_embedded_delivery_page", None)
        if page is not None and hasattr(page, "_open_new_delivery"):
            page._open_new_delivery()

    def _quick_action_update_status(self, event=None):
        self._show_deliveries_page()
        page = getattr(self, "_embedded_delivery_page", None)
        if page is None:
            return

        if hasattr(page, "_proxy") and page._proxy.rowCount() > 0 and hasattr(page, "open_status"):
            page.open_status(0)

    def _sign_out(self):
        LoginController.logout()

        from views.login_view import LoginView

        self._login_view = LoginView()
        self._login_view.show()
        self.close()

    # ── Top bar ───────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(84)
        bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 8, 28, 8)

        self._breadcrumb_lbl = QLabel("DASHBOARD")
        self._breadcrumb_lbl.setFont(inter(11, QFont.Medium))
        self._breadcrumb_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._breadcrumb_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.5px;background:transparent;border:none;")
        lay.addWidget(self._breadcrumb_lbl)
        lay.addStretch()

        # Clock
        clock_col = QVBoxLayout()
        clock_col.setContentsMargins(0, 0, 0, 0)
        clock_col.setSpacing(2)
        clock_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._clock_lbl = QLabel("--:--:--")
        self._clock_lbl.setFont(inter(17, QFont.Medium))
        self._clock_lbl.setMinimumHeight(30)
        self._clock_lbl.setAlignment(Qt.AlignRight)
        self._clock_lbl.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:1px;background:transparent;border:none;")

        self._date_lbl = QLabel(QDate.currentDate().toString("dddd, MMMM d, yyyy"))
        self._date_lbl.setFont(inter(11))
        self._date_lbl.setMinimumHeight(18)
        self._date_lbl.setAlignment(Qt.AlignRight)
        self._date_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.3px;background:transparent;border:none;")

        clock_col.addWidget(self._clock_lbl)
        clock_col.addWidget(self._date_lbl)
        lay.addLayout(clock_col)
        lay.addSpacing(16)

        notif = QPushButton()
        notif.setFixedSize(36, 36)
        notif.setCursor(Qt.PointingHandCursor)
        notif.setText("🔔")
        notif.setStyleSheet(f"""
            QPushButton{{
                color:{GRAY_4};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:6px;font-size:14px;
            }}
            QPushButton:hover{{background:{GRAY_1};}}
        """)
        lay.addWidget(notif)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()
        return bar

    def _tick(self):
        self._clock_lbl.setText(QTime.currentTime().toString("hh:mm:ss"))

    # ── Main content ──────────────────────────────────────────────────────────
    def _build_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(owner_scrollbar_qss())

        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(28, 24, 28, 28)
        lay.setSpacing(0)

        # Page header
        header_row = QHBoxLayout()
        header_row.setSpacing(0)

        left_col = QVBoxLayout()
        left_col.setSpacing(0)

        sub = QLabel("OPERATIONS OVERVIEW")
        sub.setFont(inter(10, QFont.DemiBold))
        sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

        hour = datetime.datetime.now().hour
        greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        name_part = self._greeting_name()

        title = QLabel(f"{greet}, {name_part}")
        self._greeting_title = title
        title.setFont(playfair(28, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        page_sub = QLabel("Here's what's happening with your deliveries today.")
        page_sub.setFont(inter(12))
        page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

        left_col.addWidget(sub)
        left_col.addWidget(title)
        left_col.addWidget(page_sub)

        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin-bottom:6px;margin-left:24px;")

        header_row.addLayout(left_col)
        header_row.addWidget(rule, 1, Qt.AlignBottom)
        lay.addLayout(header_row)
        lay.addSpacing(22)

        kpi_counts = self._dashboard_data.get("kpi_counts", {})

        # KPI row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        kpi_row.addWidget(
            KpiCard("TODAY'S DELIVERIES", str(self._to_int(kpi_counts.get("total_today"))), "Scheduled for today", TEAL)
        )
        kpi_row.addWidget(
            KpiCard("PENDING", str(self._to_int(kpi_counts.get("pending_today"))), "Awaiting dispatch", TEAL_MID)
        )
        kpi_row.addWidget(
            KpiCard("IN TRANSIT", str(self._to_int(kpi_counts.get("in_transit_today"))), "Currently on the way", TEAL_LIGHT)
        )
        kpi_row.addWidget(
            KpiCard("UNPAID", str(self._to_int(kpi_counts.get("unpaid_count"))), "Pending payment", "#a83232")
        )
        lay.addLayout(kpi_row)
        lay.addSpacing(22)

        # Bottom grid
        bottom = QHBoxLayout()
        bottom.setSpacing(14)
        bottom.addWidget(self._build_delivery_table(), stretch=1)

        right_panel = QWidget()
        right_panel.setStyleSheet("background:transparent;border:none;")
        right_panel.setMinimumWidth(300)
        right_panel.setMaximumWidth(340)
        right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        right = QVBoxLayout(right_panel)
        right.setSpacing(14)
        right.setContentsMargins(0, 0, 0, 0)
        right.addWidget(self._build_quick_actions())
        right.addWidget(self._build_unpaid())
        bottom.addWidget(right_panel, stretch=0)
        lay.addLayout(bottom)

        scroll.setWidget(w)
        return scroll
    
    def owner_scrollbar_qss():
        return f"""
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 4px 2px 4px 0;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {TEAL};
            min-height: 28px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {TEAL_MID};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
            border: none;
            background: transparent;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            margin: 0 2px 2px 2px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background: {TEAL};
            min-width: 28px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {TEAL_MID};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
            border: none;
            background: transparent;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
        """

    # ── Delivery table ────────────────────────────────────────────────────────
    def _build_delivery_table(self):
        card = QFrame()
        card.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(65)
        head.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 14, 18, 12)

        t = QLabel("Today's Deliveries")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        va = QPushButton("View all →")
        va.setCursor(Qt.PointingHandCursor)
        va.setFont(inter(11, QFont.Medium))
        va.setStyleSheet(f"color:{TEAL};background:transparent;border:none;")
        va.clicked.connect(self._show_deliveries_page)

        h_lay.addWidget(t)
        h_lay.addStretch()
        h_lay.addWidget(va)
        lay.addWidget(head)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["CUSTOMER", "ADDRESS", "PRODUCT", "STATUS"])
        table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setFocusPolicy(Qt.NoFocus)
        table.setShowGrid(False)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setWordWrap(True)
        table.setTextElideMode(Qt.ElideNone)
        table.setStyleSheet(f"""
            QTableWidget{{
                background:transparent;border:none;
                font-family:'{INTER_FAMILY}';font-size:12px;color:{GRAY_5};outline:none;
            }}
            QTableWidget::item{{padding:11px 18px;border-bottom:0.5px solid {GRAY_2};}}
            QTableWidget::item:selected{{background:{TEAL_PALE};color:{TEAL_DARK};}}
            QHeaderView::section{{
                background:{WHITE};color:{GRAY_4};
                font-size:12px;font-weight:600;letter-spacing:1.5px;
                padding:10px 18px 8px;border:none;
                border-bottom:1px solid {GRAY_2};
                text-align:center;
                font-family:'{INTER_FAMILY}';
            }}
        """)
        table.setStyleSheet(table.styleSheet() + owner_scrollbar_qss())

        rows = self._dashboard_data.get("todays_deliveries", [])
        table.setColumnWidth(0, 235)
        table.setColumnWidth(1, 280)
        table.setColumnWidth(2, 330)
        table.setColumnWidth(3, 150)

        status_style = {
            "DELIVERED":  (GREEN_BG,   GREEN),
            "IN TRANSIT": (TEAL_PALE2, TEAL_DARK),
            "PENDING":    (AMBER_BG,   AMBER),
            "CANCELLED":  (RED_BG,     RED),
        }

        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            name = self._text(row.get("customer_name"))
            phone = self._text(row.get("contact"))
            addr = self._text(row.get("address"))
            prod = self._text(row.get("product_summary"), fallback="-")
            status = self._text(row.get("status"), fallback="PENDING").upper()

            # Customer cell — name + phone
            cust_w = QWidget()
            cust_w.setStyleSheet("background:transparent;border:none;")
            cw_lay = QVBoxLayout(cust_w)
            cw_lay.setContentsMargins(12, 8, 12, 8)
            cw_lay.setSpacing(1)
            cw_lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            n = QLabel(name)
            n.setFont(inter(12, QFont.Medium))
            n.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            n.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            p = QLabel(phone)
            p.setFont(inter(11))
            p.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            p.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            cw_lay.addWidget(n)
            cw_lay.addWidget(p)
            cw_lay.addStretch()
            table.setCellWidget(i, 0, cust_w)

            for col, text in [(1, addr), (2, prod)]:
                text_host = QWidget()
                text_host.setStyleSheet("background:transparent;border:none;")
                text_lay = QVBoxLayout(text_host)
                text_lay.setContentsMargins(12, 10, 12, 10)
                text_lay.setSpacing(0)
                text_lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

                text_lbl = QLabel(text)
                text_lbl.setFont(inter(12))
                text_lbl.setWordWrap(True)
                text_lbl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                text_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                text_lbl.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

                text_lay.addWidget(text_lbl)
                text_lay.addStretch()
                table.setCellWidget(i, col, text_host)

            # Status pill
            bg, fg = status_style.get(status, (GRAY_2, GRAY_5))
            pill = QLabel(status)
            pill.setFont(inter(10, QFont.DemiBold))
            pill.setAlignment(Qt.AlignCenter)
            pill.setFixedHeight(22)
            pill.setStyleSheet(f"""
                background:{bg};color:{fg};
                border-radius:11px;padding:3 12px;
                letter-spacing:0.5px;border:none;
            """)
            cell = QWidget()
            cell.setStyleSheet("background:transparent;border:none;")
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(12, 0, 12, 0)
            cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(pill, alignment=Qt.AlignCenter)
            table.setCellWidget(i, 3, cell)

        for i in range(len(rows)):
            table.resizeRowToContents(i)
            table.setRowHeight(i, max(88, table.rowHeight(i)))

        table.setMinimumHeight(max(320, 58 + sum(table.rowHeight(i) for i in range(len(rows)))))

        if not rows:
            table.setRowCount(1)
            table.setSpan(0, 0, 1, 4)
            empty_item = QTableWidgetItem("No deliveries scheduled today")
            empty_item.setFont(inter(12))
            empty_item.setForeground(QColor(GRAY_4))
            empty_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(0, 0, empty_item)

        lay.addWidget(table)
        return card

    # ── Quick actions ─────────────────────────────────────────────────────────
    def _build_quick_actions(self):
        card = QFrame()
        card.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(65)
        head.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 14, 18, 12)
        t = QLabel("Quick Actions")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        h_lay.addWidget(t)
        lay.addWidget(head)

        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(18, 14, 18, 14)
        b_lay.setSpacing(0)

        actions = [
            ("New delivery",  "Schedule a delivery",   "new_delivery_icon"),
            ("Add customer",  "Register new customer", "add_customer_icon"),
            ("Update status", "Change delivery status", "update_status_icon"),
        ]

        action_handlers = {
            "New delivery": self._quick_action_new_delivery,
            "Add customer": self._quick_action_add_customer,
            "Update status": self._quick_action_update_status,
        }

        for i, (lbl, desc, icon_key) in enumerate(actions):
            row = QWidget()
            row.setFixedHeight(50)
            row.setCursor(Qt.PointingHandCursor)
            row.setStyleSheet("background:transparent;border:none;")
            r_lay = QHBoxLayout(row)
            r_lay.setContentsMargins(0, 0, 0, 0)
            r_lay.setSpacing(10)

            ico = QLabel()
            ico.setFixedSize(32, 32)
            ico.setAlignment(Qt.AlignCenter)
            ico.setStyleSheet(f"background:{WHITE};border:1px solid {GRAY_2};border-radius:4px;color:{TEAL};")
            action_icon_path = os.path.join(BASE_DIR, "assets", f"{icon_key}.png")
            action_icon_pm = QPixmap(action_icon_path)
            if not action_icon_pm.isNull():
                ico.setPixmap(action_icon_pm.scaledToWidth(18, Qt.SmoothTransformation))

            col = QVBoxLayout()
            col.setSpacing(0)
            l1 = QLabel(lbl)
            l1.setFont(inter(12, QFont.Medium))
            l1.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            l2 = QLabel(desc)
            l2.setFont(inter(11))
            l2.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            col.addWidget(l1)
            col.addWidget(l2)

            arr = QLabel("›")
            arr.setFont(inter(14))
            arr.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

            for widget in (ico, l1, l2, arr):
                widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            r_lay.addWidget(ico)
            r_lay.addLayout(col)
            r_lay.addStretch()
            r_lay.addWidget(arr)

            handler = action_handlers.get(lbl)
            if handler is not None:
                row.mousePressEvent = lambda event, cb=handler: cb(event)

            b_lay.addWidget(row)

            if i < len(actions) - 1:
                b_lay.addWidget(HDivider(GRAY_2))

        lay.addWidget(body)
        return card

    # ── Unpaid deliveries ─────────────────────────────────────────────────────
    def _build_unpaid(self):
        card = QFrame()
        card.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        head = QWidget()
        head.setFixedHeight(65) 
        head.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(head)
        h_lay.setContentsMargins(18, 14, 18, 12)
        t = QLabel("Unpaid Deliveries")
        t.setFont(playfair(15, QFont.Medium))
        t.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        va = QPushButton("View all →")
        va.setCursor(Qt.PointingHandCursor)
        va.setFont(inter(11, QFont.Medium))
        va.setStyleSheet(f"color:{TEAL};background:transparent;border:none;")
        va.clicked.connect(self._show_transactions_page)
        h_lay.addWidget(t)
        h_lay.addStretch()
        h_lay.addWidget(va)
        lay.addWidget(head)

        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(18, 14, 18, 14)
        b_lay.setSpacing(0)

        items = self._dashboard_data.get("unpaid_deliveries", [])

        if not items:
            empty = QLabel("No unpaid deliveries")
            empty.setFont(inter(12))
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;padding:28px 0;")
            b_lay.addWidget(empty)

        for i, item in enumerate(items):
            name = self._text(item.get("customer_name"))
            prod = self._text(item.get("product_summary"), fallback="-")
            amt = self._money(item.get("total_amount"), item.get("total_amount_fmt"))
            row = QWidget()
            row.setFixedHeight(50)
            row.setStyleSheet("background:transparent;border:none;")
            r_lay = QHBoxLayout(row)
            r_lay.setContentsMargins(0, 0, 0, 0)
            r_lay.setSpacing(10)

            dot = QLabel()
            dot.setFixedSize(6, 6)
            dot.setStyleSheet("background:#c0392b;border-radius:3px;border:none;")

            col = QVBoxLayout()
            col.setSpacing(1)
            n = QLabel(name)
            n.setFont(inter(12, QFont.Medium))
            n.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
            p = QLabel(prod)
            p.setFont(inter(11))
            p.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            col.addWidget(n)
            col.addWidget(p)

            amount = QLabel(amt)
            amount.setFont(inter(10, QFont.Medium))
            amount.setStyleSheet(f"color:#a32d2d;background:transparent;border:none;")

            r_lay.addWidget(dot, alignment=Qt.AlignVCenter)
            r_lay.addLayout(col)
            r_lay.addStretch()
            r_lay.addWidget(amount)
            b_lay.addWidget(row)

            if i < len(items) - 1:
                b_lay.addWidget(HDivider(GRAY_2))

        lay.addWidget(body)
        return card

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self._dropdown_open:
            self._dropdown.hide()
            self._dropdown_open = False
            self._chevron.setText("▾")
        super().mousePressEvent(event)
    
    def mousePressEvent(self, event):
        if self._dropdown_open:
            self._dropdown.hide()
            self._sync_dropdown_state()
        super().mousePressEvent(event)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setFont(inter(11))
    w = DashboardView(user={"full_name": "GNC Admin", "role": "admin"})
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
