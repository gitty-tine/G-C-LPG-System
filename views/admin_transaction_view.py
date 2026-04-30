import os
import sys
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime, Signal
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QComboBox,
    QPushButton,
    QDialog,
    QDateEdit,
    QStackedWidget,
    QCalendarWidget,
    QToolButton,
    QMenu,
    QSpinBox,
    QMessageBox,
)
from PySide6.QtGui import QIcon, QTextCharFormat


BASE_DIR = PROJECT_ROOT
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
MODERN_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_modern.svg")
WHITE_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_white.svg")
NO_TRANSACTIONS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

TEAL = "#1A7A6E"
TEAL_DARK = "#145F55"
TEAL_PALE = "#e8f5f3"
WHITE = "#ffffff"
GRAY_1 = "#f4f5f4"
GRAY_2 = "#e6eae9"
GRAY_3 = "#c4ccc9"
GRAY_4 = "#7a8a87"
GRAY_5 = "#3a4a47"
GREEN = "#1a6b3a"
GREEN_BG = "#eaf3ee"
AMBER = "#8a5a00"
AMBER_BG = "#fef5e0"
RED = "#8a1a1a"
RED_BG = "#fdeaea"

TX_CUSTOMER_W = 190
TX_DELIVERY_W = 125
TX_PRODUCT_MIN_W = 320
TX_AMOUNT_W = 135
TX_PAYMENT_W = 170
TX_PAID_AT_W = 130
TX_ACTION_W = 104

PLAYFAIR_FAMILY = "Playfair Display"
INTER_FAMILY = "Inter"


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
    for font_file in fonts:
        path = os.path.join(FONTS_DIR, font_file)
        if os.path.exists(path):
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    if font_file.startswith("PlayfairDisplay"):
                        PLAYFAIR_FAMILY = families[0]
                    elif font_file == "Inter_18pt-Regular.ttf":
                        INTER_FAMILY = families[0]


def playfair(size, weight=QFont.Normal):
    font = QFont(PLAYFAIR_FAMILY, size)
    font.setWeight(weight)
    return font


def inter(size, weight=QFont.Normal):
    font = QFont(INTER_FAMILY, size)
    font.setWeight(weight)
    return font


def trim_text(value, limit):
    text = " ".join(str(value or "-").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def format_money(value):
    try:
        return f"PHP {float(value):,.2f}"
    except (TypeError, ValueError):
        return "PHP 0.00"


def _qss_path(path):
    return path.replace("\\", "/")


def _date_edit_style(min_height=34, min_width=None):
    min_width_rule = f"min-width:{min_width}px;" if min_width else ""
    icon_path = _qss_path(MODERN_CHEVRON_ICON)
    return f"""
    QDateEdit {{
        color:{GRAY_5};
        background:#fbfcfc;
        border:1px solid #d6e2df;
        border-radius:8px;
        padding:0 34px 0 12px;
        min-height:{min_height}px;
        {min_width_rule}
    }}
    QDateEdit:hover {{
        border-color:#b9d4cf;
        background:{WHITE};
    }}
    QDateEdit:focus {{
        border:1px solid {TEAL};
        background:{WHITE};
    }}
    QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width:30px;
        border-left:1px solid #e0ece9;
        border-top-right-radius:8px;
        border-bottom-right-radius:8px;
        background:#f4faf9;
    }}
    QDateEdit::down-arrow {{
        image:url({icon_path});
        width:12px;
        height:12px;
    }}
    """


def _calendar_native_tint_style():
    white_chevron_path = _qss_path(WHITE_CHEVRON_ICON)
    return f"""
    QCalendarWidget {{
        background:{WHITE};
        color:{GRAY_5};
        border:1px solid {GRAY_2};
        font-family:'{INTER_FAMILY}';
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background:{TEAL_DARK};
        color:{WHITE};
        border-top-left-radius:8px;
        border-top-right-radius:8px;
    }}
    QCalendarWidget QToolButton {{
        color:{WHITE};
        background:transparent;
        border:none;
        padding:4px 8px;
        border-radius:6px;
        font-family:'{INTER_FAMILY}';
        font-size:12px;
        font-weight:500;
    }}
    QCalendarWidget QToolButton#qt_calendar_monthbutton,
    QCalendarWidget QToolButton#qt_calendar_yearbutton {{
        background:transparent;
        border:none;
        padding:4px 22px 4px 6px;
        border-radius:0px;
        font-family:'{INTER_FAMILY}';
        font-size:14px;
        font-weight:600;
    }}
    QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator,
    QCalendarWidget QToolButton#qt_calendar_yearbutton::menu-indicator {{
        image:url({white_chevron_path});
        width:10px;
        height:10px;
        subcontrol-origin: padding;
        subcontrol-position: right center;
        right:6px;
    }}
    QCalendarWidget QToolButton:hover {{
        background:rgba(255,255,255,0.16);
    }}
    QCalendarWidget QToolButton:pressed {{
        background:rgba(255,255,255,0.24);
    }}
    QCalendarWidget QSpinBox {{
        color:{WHITE};
        background:rgba(255,255,255,0.12);
        border:1px solid rgba(255,255,255,0.24);
        border-radius:6px;
        padding-right:20px;
        min-height:24px;
        min-width:72px;
        font-family:'{INTER_FAMILY}';
        font-size:12px;
    }}
    QCalendarWidget QSpinBox::up-button {{
        subcontrol-origin:border;
        subcontrol-position:top right;
        width:18px;
        border-left:1px solid rgba(255,255,255,0.28);
        border-top-right-radius:6px;
        background:rgba(255,255,255,0.10);
    }}
    QCalendarWidget QSpinBox::down-button {{
        subcontrol-origin:border;
        subcontrol-position:bottom right;
        width:18px;
        border-left:1px solid rgba(255,255,255,0.28);
        border-top:1px solid rgba(255,255,255,0.22);
        border-bottom-right-radius:6px;
        background:rgba(255,255,255,0.10);
    }}
    QCalendarWidget QSpinBox::up-button:hover,
    QCalendarWidget QSpinBox::down-button:hover {{
        background:rgba(255,255,255,0.18);
    }}
    QCalendarWidget QAbstractItemView {{
        color:#000000;
        background:{WHITE};
        selection-background-color:{TEAL_PALE};
        selection-color:{TEAL_DARK};
        outline:0;
        border:none;
        font-family:'{INTER_FAMILY}';
        font-size:12px;
        font-weight:600;
    }}
    QCalendarWidget QAbstractItemView:item {{
        border:none;
        background:transparent;
        padding:2px;
        margin:0px;
    }}
    QCalendarWidget QAbstractItemView:item:hover {{
        background:rgba(26,122,110,0.06);
        color:#000000;
    }}
    QCalendarWidget QAbstractItemView:item:selected {{
        border:1px solid {TEAL};
        border-radius:6px;
        background:{TEAL_PALE};
        color:#000000;
        font-weight:600;
    }}
    QCalendarWidget QHeaderView::section {{
        color:{TEAL};
        background:{WHITE};
        border:none;
        padding:4px 0;
        font-family:'{INTER_FAMILY}';
        font-size:10px;
        font-weight:600;
    }}
    """


def _calendar_popup_menu_style():
    return f"""
    QMenu {{
        background:{WHITE};
        color:{TEAL_DARK};
        border:1px solid {GRAY_2};
        padding:4px;
        font-family:'{INTER_FAMILY}';
        font-size:12px;
    }}
    QMenu::item {{
        background:transparent;
        color:{TEAL_DARK};
        padding:6px 14px;
        border-radius:4px;
    }}
    QMenu::item:selected {{
        background:{TEAL_PALE};
        color:{TEAL_DARK};
    }}
    """


def _attach_year_dropdown(calendar):
    year_btn = calendar.findChild(QToolButton, "qt_calendar_yearbutton")
    if year_btn is None:
        return

    year_spin = calendar.findChild(QSpinBox, "qt_calendar_yearedit")
    if year_spin is not None:
        year_spin.hide()

    menu = QMenu(year_btn)
    menu.setStyleSheet(_calendar_popup_menu_style())

    def refill(target_year):
        menu.clear()
        for year in range(target_year - 15, target_year + 16):
            action = menu.addAction(str(year))
            action.setData(year)

    def on_year_picked(action):
        target_year = int(action.data())
        current_month = calendar.monthShown()
        calendar.setCurrentPage(target_year, current_month)

        selected = calendar.selectedDate()
        if selected.isValid():
            target_day = min(selected.day(), QDate(target_year, current_month, 1).daysInMonth())
            calendar.setSelectedDate(QDate(target_year, current_month, target_day))
        year_btn.setText(str(target_year))
        refill(target_year)

    def on_page_changed(year, month):
        year_btn.setText(str(year))
        refill(year)

    refill(calendar.yearShown())
    year_btn.setText(str(calendar.yearShown()))
    year_btn.setPopupMode(QToolButton.InstantPopup)
    year_btn.setMenu(menu)
    menu.triggered.connect(on_year_picked)
    calendar.currentPageChanged.connect(on_page_changed)


class MetricCard(QFrame):
    def __init__(self, label, value, detail, accent, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
                border-top:3px solid {accent};
            }}
            """
        )
        self.setFixedHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(3)

        lbl = QLabel(label)
        lbl.setFont(inter(10, QFont.DemiBold))
        lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.3px;background:transparent;border:none;")

        self.value_lbl = QLabel(value)
        self.value_lbl.setFont(inter(19, QFont.DemiBold))
        self.value_lbl.setMinimumHeight(28)
        self.value_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        dsc = QLabel(detail)
        dsc.setFont(inter(10))
        dsc.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        lay.addWidget(lbl)
        lay.addWidget(self.value_lbl)
        lay.addWidget(dsc)
        lay.addStretch()


class TransactionRow(QFrame):
    clicked = Signal(object)

    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self._transaction = transaction
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._transaction)
        super().mouseReleaseEvent(event)


class ConfirmPaidDialog(QDialog):
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Confirm Payment")
        self.setModal(True)
        self.setMinimumWidth(560)
        self._transaction = transaction

        self.setStyleSheet(
            f"""
            QDialog {{ background:transparent; }}
            QLabel {{ color:{GRAY_5}; background:transparent; border:none; }}
            QFrame#DialogSurface {{
                background:#f8faf9;
                border:1px solid #d8e2e0;
                border-radius:12px;
            }}
            QFrame#AmountBand {{
                background:{TEAL_PALE};
                border:1px solid #cfe1dd;
                border-radius:8px;
            }}
            QPushButton {{
                min-height:34px;
                border-radius:7px;
                padding:0 16px;
                font-family:'{INTER_FAMILY}';
                font-size:11px;
                font-weight:600;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        surface = QFrame()
        surface.setObjectName("DialogSurface")
        surface_lay = QVBoxLayout(surface)
        surface_lay.setContentsMargins(22, 20, 22, 18)
        surface_lay.setSpacing(14)
        root.addWidget(surface)

        title = QLabel("Confirm Payment Collection")
        title.setFont(playfair(18, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        subtitle = QLabel("This will mark the selected transaction as paid.")
        subtitle.setFont(inter(11))
        subtitle.setStyleSheet(f"color:{GRAY_4};")

        surface_lay.addWidget(title)
        surface_lay.addWidget(subtitle)

        amount_band = QFrame()
        amount_band.setObjectName("AmountBand")
        amount_lay = QHBoxLayout(amount_band)
        amount_lay.setContentsMargins(16, 12, 16, 12)

        amount_label = QLabel("AMOUNT TO COLLECT")
        amount_label.setFont(inter(10, QFont.DemiBold))
        amount_label.setStyleSheet(f"color:{GRAY_4};letter-spacing:1px;")

        amount_value = QLabel(format_money(transaction.get("total_amount")))
        amount_value.setFont(inter(18, QFont.DemiBold))
        amount_value.setStyleSheet(f"color:{TEAL_DARK};")

        amount_lay.addWidget(amount_label)
        amount_lay.addStretch()
        amount_lay.addWidget(amount_value)
        surface_lay.addWidget(amount_band)

        detail_rows = [
            ("Customer", transaction.get("customer_name", "")),
            ("Delivery ID", self._reference(transaction.get("delivery_id", ""))),
            ("Delivery date", self._date_text(transaction.get("delivery_date"), transaction.get("delivery_date_fmt"))),
            ("Products", transaction.get("product_summary", "")),
        ]
        for label_text, value_text in detail_rows:
            surface_lay.addWidget(self._detail_row(label_text, value_text))

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(92, 36)
        cancel_btn.setStyleSheet(
            f"QPushButton{{background:{WHITE};border:1px solid {GRAY_2};color:{GRAY_5};}}"
            f"QPushButton:hover{{background:#f1f5f4;}}"
        )
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("Mark as Paid")
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setFixedSize(120, 36)
        confirm_btn.setStyleSheet(
            f"QPushButton{{background:{TEAL};border:1px solid {TEAL};color:{WHITE};}}"
            f"QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}"
        )
        confirm_btn.clicked.connect(self.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(confirm_btn)
        surface_lay.addLayout(buttons)

    def _detail_row(self, label_text, value_text):
        row = QWidget()
        row.setStyleSheet("background:transparent;border:none;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        label = QLabel(label_text)
        label.setFont(inter(10, QFont.DemiBold))
        label.setFixedWidth(104)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.4px;")

        value = QLabel(str(value_text or "-"))
        value.setFont(inter(11, QFont.Medium))
        value.setWordWrap(True)
        value.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        value.setStyleSheet(f"color:{GRAY_5};")

        lay.addWidget(label)
        lay.addWidget(value, 1)
        return row

    @staticmethod
    def _reference(value):
        text = str(value or "").strip()
        return f"#{text}" if text else "-"

    @staticmethod
    def _date_text(value, fallback=""):
        if fallback:
            return fallback
        if isinstance(value, datetime.datetime):
            return value.strftime("%b %d, %Y")
        if isinstance(value, datetime.date):
            return value.strftime("%b %d, %Y")
        return str(value or "-")


class TransactionDetailsDialog(QDialog):
    def __init__(self, transaction, read_only=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Transaction Details")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.mark_paid_requested = False
        self._transaction = transaction
        self._read_only = read_only

        self.setStyleSheet(
            f"""
            QDialog {{ background:transparent; }}
            QLabel {{ color:{GRAY_5}; background:transparent; border:none; }}
            QFrame#DialogSurface {{
                background:#f8faf9;
                border:1px solid #d8e2e0;
                border-radius:12px;
            }}
            QFrame#SummaryBand {{
                background:{TEAL_PALE};
                border:1px solid #cfe1dd;
                border-radius:8px;
            }}
            QFrame#Card {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:10px;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        surface = QFrame()
        surface.setObjectName("DialogSurface")
        surface_lay = QVBoxLayout(surface)
        surface_lay.setContentsMargins(22, 20, 22, 18)
        surface_lay.setSpacing(14)
        root.addWidget(surface)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(16)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Transaction Details")
        title.setFont(playfair(22, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};")

        subtitle = QLabel("Read-only payment and delivery record.")
        subtitle.setFont(inter(11))
        subtitle.setStyleSheet(f"color:{GRAY_4};")

        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col, 1)

        status_badge = QLabel(self._payment_text(transaction.get("payment_status")))
        status_badge.setFont(inter(9, QFont.DemiBold))
        status_badge.setAlignment(Qt.AlignCenter)
        status_badge.setFixedSize(88, 28)
        status_badge.setStyleSheet(self._status_badge_style(transaction.get("payment_status")))
        header.addWidget(status_badge, 0, Qt.AlignTop)
        surface_lay.addLayout(header)

        summary = QFrame()
        summary.setObjectName("SummaryBand")
        summary_lay = QHBoxLayout(summary)
        summary_lay.setContentsMargins(16, 12, 16, 12)
        summary_lay.setSpacing(14)

        customer = QLabel(str(transaction.get("customer_name") or "-"))
        customer.setFont(inter(15, QFont.DemiBold))
        customer.setStyleSheet(f"color:{TEAL_DARK};")

        amount = QLabel(format_money(transaction.get("total_amount")))
        amount.setFont(inter(18, QFont.DemiBold))
        amount.setStyleSheet(f"color:{TEAL_DARK};")

        summary_lay.addWidget(customer, 1)
        summary_lay.addWidget(amount, 0, Qt.AlignRight)
        surface_lay.addWidget(summary)

        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(18, 16, 18, 16)
        card_lay.setSpacing(12)

        section = QLabel("Record Information")
        section.setFont(inter(10, QFont.DemiBold))
        section.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:0.8px;")
        card_lay.addWidget(section)

        details = [
            ("Transaction ID", self._reference(transaction.get("transaction_id"))),
            ("Delivery ID", self._reference(transaction.get("delivery_id"))),
            ("Customer contact", transaction.get("customer_contact", "")),
            ("Delivery address", transaction.get("customer_address", "")),
            ("Delivery date", self._date_text(transaction.get("delivery_date"), transaction.get("delivery_date_fmt"))),
            ("Delivery status", self._status_text(transaction.get("delivery_status"))),
            ("Products", transaction.get("product_summary", "")),
            ("Payment status", self._payment_text(transaction.get("payment_status"))),
            ("Paid at", self._date_text(transaction.get("paid_at"), transaction.get("paid_at_fmt"))),
            ("Recorded at", transaction.get("created_at_fmt", "")),
        ]
        for label_text, value_text in details:
            card_lay.addWidget(self._detail_row(label_text, value_text))

        surface_lay.addWidget(card)

        button_row = QHBoxLayout()
        button_row.addStretch()

        if self._can_mark_paid(transaction):
            mark_btn = QPushButton("Mark as Paid")
            mark_btn.setCursor(Qt.PointingHandCursor)
            mark_btn.setFont(inter(10, QFont.Medium))
            mark_btn.setFixedSize(120, 36)
            mark_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background:{TEAL};
                    color:{WHITE};
                    border:1px solid {TEAL};
                    border-radius:7px;
                }}
                QPushButton:hover {{
                    background:{TEAL_DARK};
                    border-color:{TEAL_DARK};
                }}
                """
            )
            mark_btn.clicked.connect(self._request_mark_paid)
            button_row.addWidget(mark_btn)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFont(inter(10, QFont.Medium))
        close_btn.setFixedSize(92, 36)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background:{WHITE};
                color:{GRAY_5};
                border:1px solid {GRAY_2};
                border-radius:7px;
            }}
            QPushButton:hover {{
                background:#f1f5f4;
            }}
            """
        )
        close_btn.clicked.connect(self.accept)
        button_row.addWidget(close_btn)
        surface_lay.addLayout(button_row)

    def _detail_row(self, label_text, value_text):
        row = QWidget()
        row.setStyleSheet("background:transparent;border:none;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        label = QLabel(label_text)
        label.setFont(inter(10, QFont.DemiBold))
        label.setFixedWidth(132)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.4px;")

        value = QLabel(str(value_text or "-"))
        value.setFont(inter(11, QFont.Medium))
        value.setWordWrap(True)
        value.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        value.setStyleSheet(f"color:{GRAY_5};")

        lay.addWidget(label)
        lay.addWidget(value, 1)
        return row

    def _can_mark_paid(self, transaction):
        return not self._read_only and str(transaction.get("payment_status", "")).lower() != "paid"

    def _request_mark_paid(self):
        self.mark_paid_requested = True
        self.accept()

    @staticmethod
    def _reference(value):
        text = str(value or "").strip()
        return f"#{text}" if text else "-"

    @staticmethod
    def _payment_text(value):
        text = str(value or "").strip()
        return text.title() if text else "Unpaid"

    @staticmethod
    def _status_text(value):
        text = str(value or "").strip()
        return text.title() if text else "-"

    @staticmethod
    def _date_text(value, fallback=""):
        if fallback:
            return fallback
        if isinstance(value, datetime.datetime):
            return value.strftime("%b %d, %Y")
        if isinstance(value, datetime.date):
            return value.strftime("%b %d, %Y")
        return str(value or "-")

    @staticmethod
    def _status_badge_style(status):
        if str(status or "").lower() == "paid":
            return f"background:{GREEN_BG};color:{GREEN};border:1px solid #cfe6d9;border-radius:6px;letter-spacing:1px;"
        return f"background:{AMBER_BG};color:{AMBER};border:1px solid #f0dfb7;border-radius:6px;letter-spacing:1px;"


class TransactionView(QWidget):
    AUTO_REFRESH_INTERVAL_MS = 5000
    DEFAULT_LOOKBACK_YEARS = 10

    def __init__(self, parent=None, show_topbar=True, controller=None, read_only=False):
        super().__init__(parent)
        self._show_topbar = show_topbar
        self._read_only = read_only
        self._all_transactions = []
        self._filtered_transactions = []
        self._controller = None
        self._is_reloading = False

        load_fonts()
        self.setStyleSheet(f"background:{GRAY_1};")
        self._build_ui()
        self._setup_refresh_timer()

        if controller:
            self.bind_controller(controller, request_initial=True)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if self._show_topbar:
            root.addWidget(self._build_topbar())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            f"""
            QScrollArea{{background:transparent;border:none;}}
            QScrollBar:vertical{{background:transparent;width:11px;margin:8px 4px 8px 0;}}
            QScrollBar::handle:vertical{{
                background:rgba(26,122,110,0.30);
                min-height:34px;
                border-radius:5px;
                border:1px solid rgba(26,122,110,0.18);
            }}
            QScrollBar::handle:vertical:hover{{
                background:rgba(26,122,110,0.48);
                border:1px solid rgba(26,122,110,0.26);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{{height:0;border:none;background:transparent;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{{background:transparent;}}
            """
        )

        self._content = QWidget()
        self._content.setStyleSheet("background:transparent;border:none;")
        self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_lay = QVBoxLayout(self._content)
        content_lay.setContentsMargins(28, 24, 28, 28)
        content_lay.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.setSpacing(0)

        left = QVBoxLayout()
        left.setSpacing(0)

        sub = QLabel("PAYMENT AND ORDER TRACKING")
        sub.setFont(inter(10, QFont.DemiBold))
        sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

        title = QLabel("Transactions")
        title.setFont(playfair(28, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        desc = QLabel("Review customer orders, payment status, and transaction history from one place.")
        desc.setFont(inter(12))
        desc.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

        left.addWidget(sub)
        left.addWidget(title)
        left.addWidget(desc)

        self._status_filter = QComboBox()
        self._status_filter.addItems(["All statuses", "Paid", "Unpaid"])
        self._status_filter.setFont(inter(11))
        self._status_filter.setFixedHeight(34)
        self._status_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._status_filter.currentIndexChanged.connect(self._apply_filter)
        self._status_filter.setStyleSheet(
            f"""
            QComboBox {{
                color:{GRAY_5};
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:4px;
                padding:0 10px;
            }}
            QComboBox::drop-down {{
                border:none;
                width:24px;
            }}
            QComboBox QAbstractItemView {{
                border:1px solid {GRAY_2};
                background:{WHITE};
                selection-background-color:{TEAL_PALE};
                selection-color:{TEAL_DARK};
            }}
            """
        )

        self._date_from = QDateEdit()
        self._date_from.setCalendarPopup(True)
        self._date_from.setDisplayFormat("MMM d, yyyy")
        self._date_from.setDate(self._default_from_date())
        self._date_from.setFont(inter(11))
        self._date_from.setFixedHeight(34)
        self._date_from.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._date_from.dateChanged.connect(self._on_date_from_changed)

        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDisplayFormat("MMM d, yyyy")
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setFont(inter(11))
        self._date_to.setFixedHeight(34)
        self._date_to.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._date_to.dateChanged.connect(self._on_date_to_changed)

        self._configure_date_edit(self._date_from)
        self._configure_date_edit(self._date_to)

        from_lbl = QLabel("From")
        from_lbl.setFont(inter(10, QFont.Medium))
        from_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        to_lbl = QLabel("To")
        to_lbl.setFont(inter(10, QFont.Medium))
        to_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        header_row.addLayout(left)
        header_row.addStretch()
        content_lay.addLayout(header_row)
        content_lay.addSpacing(8)

        filter_bar = QFrame()
        filter_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        filter_bar.setStyleSheet(
            f"QFrame{{background:transparent;border:none;border-radius:8px;}}"
        )
        fb_lay = QHBoxLayout(filter_bar)
        fb_lay.setContentsMargins(14, 10, 14, 10)
        fb_lay.setSpacing(8)

        filter_lbl = QLabel("Filter:")
        filter_lbl.setFont(inter(10, QFont.DemiBold))
        filter_lbl.setStyleSheet(
            f"color:{GRAY_4};letter-spacing:1px;background:transparent;border:none;"
        )

        fb_lay.addWidget(filter_lbl)
        fb_lay.addWidget(self._status_filter)
        fb_lay.addSpacing(4)
        fb_lay.addWidget(from_lbl)
        fb_lay.addWidget(self._date_from)
        fb_lay.addWidget(to_lbl)
        fb_lay.addWidget(self._date_to)

        content_lay.addWidget(filter_bar)
        content_lay.addSpacing(4)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        self._metric_paid = MetricCard("TOTAL PAID", "PHP 0.00", "Collected transactions", TEAL)
        self._metric_unpaid = MetricCard("TOTAL UNPAID", "PHP 0.00", "Receivables to collect", AMBER)
        summary_row.addWidget(self._metric_paid)
        summary_row.addWidget(self._metric_unpaid)
        content_lay.addLayout(summary_row)

        self._transactions_card = self._build_transactions_card()

        self._empty_state = QWidget()
        empty_lay = QVBoxLayout(self._empty_state)
        empty_lay.setContentsMargins(0, 36, 0, 36)
        empty_lay.setAlignment(Qt.AlignCenter)

        empty_image = QLabel()
        empty_image.setAlignment(Qt.AlignCenter)
        empty_image.setStyleSheet("background:transparent;border:none;")
        empty_image.setFixedSize(230, 145)
        empty_pixmap = QPixmap(NO_TRANSACTIONS_IMAGE)
        if not empty_pixmap.isNull():
            scale = self.devicePixelRatio()
            target_w = int(230 * scale)
            target_h = int(145 * scale)
            scaled = empty_pixmap.scaled(
                target_w,
                target_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            scaled.setDevicePixelRatio(scale)
            empty_image.setPixmap(scaled)

        self._empty_title = QLabel("No transactions yet")
        self._empty_title.setFont(playfair(16, QFont.Medium))
        self._empty_title.setAlignment(Qt.AlignCenter)
        self._empty_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        self._empty_desc = QLabel("Transaction records will appear here once payments or delivery transactions are added.")
        self._empty_desc.setFont(inter(12))
        self._empty_desc.setAlignment(Qt.AlignCenter)
        self._empty_desc.setWordWrap(True)
        self._empty_desc.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

        empty_lay.addWidget(empty_image, 0, Qt.AlignCenter)
        empty_lay.addWidget(self._empty_title)
        empty_lay.addWidget(self._empty_desc)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._transactions_card)
        self._stack.addWidget(self._empty_state)
        content_lay.addWidget(self._stack)

        scroll.setWidget(self._content)
        root.addWidget(scroll)

    def _build_transactions_card(self):
        card = QFrame()
        card.setObjectName("TransactionsCard")
        card.setMinimumHeight(520)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet(
            f"""
            QFrame#TransactionsCard {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
            }}
            """
        )

        root = QVBoxLayout(card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(54)
        header.setStyleSheet(f"background:#f4f8f7;border:none;border-bottom:1px solid {GRAY_2};")
        header_lay = QGridLayout(header)
        header_lay.setContentsMargins(16, 0, 16, 0)
        header_lay.setHorizontalSpacing(14)
        header_lay.setVerticalSpacing(0)
        self._configure_transaction_columns(header_lay)

        header_lay.addWidget(self._transaction_header_label("CUSTOMER"), 0, 0)
        header_lay.addWidget(self._transaction_header_label("DELIVERY"), 0, 1)
        header_lay.addWidget(self._transaction_header_label("PRODUCTS"), 0, 2)
        header_lay.addWidget(self._transaction_header_label("AMOUNT", Qt.AlignRight | Qt.AlignVCenter), 0, 3)
        header_lay.addWidget(self._transaction_header_label("PAYMENT", Qt.AlignCenter), 0, 4)
        header_lay.addWidget(self._transaction_header_label("PAID AT"), 0, 5)
        if not self._read_only:
            header_lay.addWidget(self._transaction_header_label("", Qt.AlignCenter), 0, 6)
        root.addWidget(header)

        self._transactions_scroll = QScrollArea()
        self._transactions_scroll.setWidgetResizable(True)
        self._transactions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._transactions_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._transactions_scroll.setStyleSheet(
            f"""
            QScrollArea {{ background:transparent;border:none; }}
            QScrollBar:vertical {{
                background:transparent;
                width:10px;
                margin:8px 3px 8px 0;
            }}
            QScrollBar::handle:vertical {{
                background:rgba(26,122,110,0.34);
                border-radius:5px;
                min-height:32px;
            }}
            QScrollBar::handle:vertical:hover {{ background:rgba(26,122,110,0.52); }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height:0;
                border:none;
                background:transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:transparent; }}
            """
        )

        self._transactions_list = QWidget()
        self._transactions_list.setStyleSheet("background:transparent;border:none;")
        self._transactions_lay = QVBoxLayout(self._transactions_list)
        self._transactions_lay.setContentsMargins(14, 14, 14, 14)
        self._transactions_lay.setSpacing(8)

        self._transactions_scroll.setWidget(self._transactions_list)
        root.addWidget(self._transactions_scroll)
        return card

    def _configure_transaction_columns(self, layout):
        widths = {
            0: TX_CUSTOMER_W,
            1: TX_DELIVERY_W,
            2: TX_PRODUCT_MIN_W,
            3: TX_AMOUNT_W,
            4: TX_PAYMENT_W,
            5: TX_PAID_AT_W,
        }
        if not self._read_only:
            widths[6] = TX_ACTION_W

        for column, width in widths.items():
            layout.setColumnMinimumWidth(column, width)
            layout.setColumnStretch(column, 0)
        layout.setColumnStretch(2, 1)

    def _transaction_header_label(self, text, alignment=Qt.AlignLeft | Qt.AlignVCenter):
        label = QLabel(text)
        label.setFont(inter(10, QFont.DemiBold))
        label.setAlignment(alignment)
        label.setStyleSheet(
            f"color:{GRAY_4};letter-spacing:1px;background:transparent;border:none;"
        )
        return label

    def _configure_date_edit(self, date_edit, min_height=34, min_width=140):
        date_edit.setStyleSheet(_date_edit_style(min_height=min_height, min_width=min_width))
        calendar = date_edit.calendarWidget()
        if calendar is not None:
            calendar.setFont(inter(11))
            calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
            calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
            calendar.setGridVisible(False)
            calendar.setMinimumSize(320, 260)
            calendar.setStyleSheet(_calendar_native_tint_style())

            saturday_fmt = QTextCharFormat()
            saturday_fmt.setForeground(QColor("#000000"))
            calendar.setWeekdayTextFormat(Qt.Saturday, saturday_fmt)

            sunday_fmt = QTextCharFormat()
            sunday_fmt.setForeground(QColor(TEAL))
            calendar.setWeekdayTextFormat(Qt.Sunday, sunday_fmt)

            for btn_name in ("qt_calendar_monthbutton", "qt_calendar_yearbutton"):
                btn = calendar.findChild(QToolButton, btn_name)
                if btn is not None and btn.menu() is not None:
                    btn.menu().setStyleSheet(_calendar_popup_menu_style())

            _attach_year_dropdown(calendar)

            prev_btn = calendar.findChild(QToolButton, "qt_calendar_prevmonth")
            if prev_btn is not None:
                prev_btn.setIcon(QIcon())
                prev_btn.setText("<")
                prev_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
                prev_btn.setStyleSheet(
                    f"""
                    QToolButton {{
                        color:{WHITE};
                        background:transparent;
                        border:none;
                        font-size:20px;
                        font-weight:600;
                    }}
                    QToolButton:hover {{
                        background:rgba(255,255,255,0.16);
                        border-radius:8px;
                    }}
                    """
                )

            next_btn = calendar.findChild(QToolButton, "qt_calendar_nextmonth")
            if next_btn is not None:
                next_btn.setIcon(QIcon())
                next_btn.setText(">")
                next_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
                next_btn.setStyleSheet(
                    f"""
                    QToolButton {{
                        color:{WHITE};
                        background:transparent;
                        border:none;
                        font-size:20px;
                        font-weight:600;
                    }}
                    QToolButton:hover {{
                        background:rgba(255,255,255,0.16);
                        border-radius:8px;
                    }}
                    """
                )

    def _on_date_from_changed(self, new_date):
        if new_date > self._date_to.date():
            self._date_to.blockSignals(True)
            self._date_to.setDate(new_date)
            self._date_to.blockSignals(False)
        if self._controller:
            self.reload_data()
        else:
            self._apply_filter()

    def _on_date_to_changed(self, new_date):
        if new_date < self._date_from.date():
            self._date_from.blockSignals(True)
            self._date_from.setDate(new_date)
            self._date_from.blockSignals(False)
        if self._controller:
            self.reload_data()
        else:
            self._apply_filter()

    def _build_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(84)
        bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(28, 8, 28, 8)

        breadcrumb = QLabel("TRANSACTION MANAGEMENT")
        breadcrumb.setFont(inter(11, QFont.Medium))
        breadcrumb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        breadcrumb.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.5px;background:transparent;border:none;")
        lay.addWidget(breadcrumb)
        lay.addStretch()

        clock_col = QVBoxLayout()
        clock_col.setContentsMargins(0, 0, 0, 0)
        clock_col.setSpacing(2)
        clock_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._clock_lbl = QLabel("--:--:--")
        self._clock_lbl.setFont(inter(17, QFont.Medium))
        self._clock_lbl.setAlignment(Qt.AlignRight)
        self._clock_lbl.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:1px;background:transparent;border:none;")

        self._date_lbl = QLabel("")
        self._date_lbl.setFont(inter(11))
        self._date_lbl.setAlignment(Qt.AlignRight)
        self._date_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.3px;background:transparent;border:none;")

        clock_col.addWidget(self._clock_lbl)
        clock_col.addWidget(self._date_lbl)
        lay.addLayout(clock_col)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()
        return bar

    def _tick(self):
        self._clock_lbl.setText(QTime.currentTime().toString("hh:mm:ss"))
        self._date_lbl.setText(QDate.currentDate().toString("dddd, MMMM d, yyyy"))

    def bind_controller(self, controller, request_initial=False):
        self._controller = controller
        if hasattr(controller, "attach_view"):
            controller.attach_view(self)
        if request_initial and self._controller:
            self.reload_data()

    def showEvent(self, event):
        super().showEvent(event)
        self._start_refresh_timer()
        if self._controller:
            self.reload_data()

    def hideEvent(self, event):
        self._stop_refresh_timer()
        super().hideEvent(event)

    def _setup_refresh_timer(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(self.AUTO_REFRESH_INTERVAL_MS)
        self._refresh_timer.timeout.connect(self._refresh_if_visible)

    def _default_from_date(self):
        today = QDate.currentDate()
        return QDate(today.year(), today.month(), 1)

    def _start_refresh_timer(self):
        if hasattr(self, "_refresh_timer") and not self._refresh_timer.isActive():
            self._refresh_timer.start()

    def _stop_refresh_timer(self):
        if hasattr(self, "_refresh_timer") and self._refresh_timer.isActive():
            self._refresh_timer.stop()

    def _refresh_if_visible(self):
        if not self.isVisible():
            return
        self.reload_data()

    def current_date_range(self):
        def to_pydate(qdate):
            if hasattr(qdate, "toPython"):
                return qdate.toPython()
            return qdate.toPyDate()

        return to_pydate(self._date_from.date()), to_pydate(self._date_to.date())

    def reset_view_state(self):
        today = QDate.currentDate()
        first_of_month = QDate(today.year(), today.month(), 1)

        self._status_filter.blockSignals(True)
        self._date_from.blockSignals(True)
        self._date_to.blockSignals(True)

        self._status_filter.setCurrentIndex(0)
        self._date_from.setDate(first_of_month)
        self._date_to.setDate(today)

        self._status_filter.blockSignals(False)
        self._date_from.blockSignals(False)
        self._date_to.blockSignals(False)

        self.reload_data()

    def reload_data(self):
        if not self._controller or self._is_reloading:
            return
        self._is_reloading = True
        try:
            date_from, date_to = self.current_date_range()
            self._controller.load(date_from, date_to)
        finally:
            self._is_reloading = False

    def show_error(self, title, message):
        QMessageBox.critical(self, title, str(message))

    def load_transactions(self, transactions):
        self._all_transactions = list(transactions)
        self._apply_filter()

    def _apply_filter(self, *_):
        status_filter = self._status_filter.currentText().lower()
        date_from = self._date_from.date()
        date_to = self._date_to.date()

        def matches(transaction):
            payment_status = str(transaction.get("payment_status", "")).lower()
            if status_filter != "all statuses" and status_filter != payment_status:
                return False

            delivery_date = self._coerce_date(transaction.get("delivery_date"))
            if delivery_date is None:
                return False
            return date_from <= delivery_date <= date_to

        self._filtered_transactions = [transaction for transaction in self._all_transactions if matches(transaction)]
        self._render_table()

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
        self._clear_transaction_rows()

        if not self._filtered_transactions:
            if not self._all_transactions:
                self._empty_title.setText("No transactions yet")
                self._empty_desc.setText(
                    "Transaction records will appear here once payments or delivery transactions are added."
                )
            else:
                self._empty_title.setText("No matching transactions")
                self._empty_desc.setText(
                    "No transaction records match the selected status or date range. Try adjusting the filters to see more results."
                )
            self._stack.setCurrentWidget(self._empty_state)
            return

        self._stack.setCurrentWidget(self._transactions_card)

        for row_index, transaction in enumerate(self._filtered_transactions):
            self._transactions_lay.addWidget(self._build_transaction_row(transaction, row_index))

        self._transactions_lay.addStretch()

    def _clear_transaction_rows(self):
        if not hasattr(self, "_transactions_lay"):
            return
        while self._transactions_lay.count():
            item = self._transactions_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_transaction_row(self, transaction, row_index):
        row = TransactionRow(transaction)
        row.setObjectName("TransactionRow")
        row.setFixedHeight(72)
        row.setToolTip("Click to view transaction details")
        row.clicked.connect(self._show_transaction_details)
        row.setStyleSheet(
            f"""
            QFrame#TransactionRow {{
                background:#fbfdfc;
                border:1px solid {GRAY_2};
                border-radius:6px;
            }}
            QFrame#TransactionRow:hover {{
                background:#eef8f6;
                border-color:#c9ddd9;
            }}
            """
        )

        grid = QGridLayout(row)
        grid.setContentsMargins(14, 0, 14, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(0)
        self._configure_transaction_columns(grid)

        customer_cell = self._make_transaction_widget_clickable(
            self._transaction_cell(transaction.get("customer_name", ""), TEAL_DARK, QFont.Medium),
            transaction,
        )
        delivery_cell = self._make_transaction_widget_clickable(
            self._transaction_cell(self._format_date(transaction.get("delivery_date")), GRAY_5),
            transaction,
        )
        product_cell = self._make_transaction_widget_clickable(
            self._product_cell(transaction.get("product_summary", "")),
            transaction,
        )
        amount_cell = self._make_transaction_widget_clickable(
            self._transaction_cell(
                self._format_amount(transaction.get("total_amount")),
                TEAL_DARK,
                QFont.DemiBold,
                Qt.AlignRight | Qt.AlignVCenter,
            ),
            transaction,
        )
        payment_cell = self._make_transaction_widget_clickable(
            self._status_pill(transaction.get("payment_status", "")),
            transaction,
        )
        paid_at_cell = self._make_transaction_widget_clickable(
            self._transaction_cell(
                self._format_paid_at(transaction.get("paid_at"), transaction.get("payment_status")) or "-",
                GRAY_4,
            ),
            transaction,
        )

        grid.addWidget(customer_cell, 0, 0)
        grid.addWidget(delivery_cell, 0, 1)
        grid.addWidget(product_cell, 0, 2)
        grid.addWidget(amount_cell, 0, 3)
        grid.addWidget(payment_cell, 0, 4)
        grid.addWidget(paid_at_cell, 0, 5)
        if not self._read_only:
            grid.addWidget(self._action_cell(transaction, row_index), 0, 6)
        return row

    def _make_transaction_widget_clickable(self, widget, transaction):
        widget.setCursor(Qt.PointingHandCursor)
        original_mouse_release = widget.mouseReleaseEvent

        def handle_mouse_release(event, item=transaction, original=original_mouse_release):
            if event.button() == Qt.LeftButton:
                self._show_transaction_details(item)
                event.accept()
                return
            original(event)

        widget.mouseReleaseEvent = handle_mouse_release
        return widget

    def _transaction_cell(
        self,
        value,
        color=GRAY_5,
        weight=QFont.Normal,
        alignment=Qt.AlignLeft | Qt.AlignVCenter,
    ):
        label = QLabel(str(value or "-"))
        label.setFont(inter(11, weight))
        label.setAlignment(alignment)
        label.setStyleSheet(f"color:{color};background:transparent;border:none;")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label.setToolTip(str(value or "-"))
        label.setMinimumWidth(0)
        return label

    def _product_cell(self, value):
        label = QLabel(trim_text(value, 70))
        label.setFont(inter(11))
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        label.setMinimumWidth(0)
        label.setToolTip(str(value or "-"))
        return label

    def _status_pill(self, value):
        status = str(value or "unpaid").strip().lower()
        label = QLabel(status.title())
        label.setAlignment(Qt.AlignCenter)
        label.setFont(inter(10, QFont.DemiBold))
        label.setFixedHeight(28)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        label.setMinimumWidth(0)
        label.setStyleSheet(self._status_style(status))
        return label

    def _action_cell(self, transaction, row_index):
        wrapper = QWidget()
        wrapper.setStyleSheet("background:transparent;border:none;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        if str(transaction.get("payment_status", "")).lower() == "unpaid":
            button = QPushButton("Mark Paid")
            button.setCursor(Qt.PointingHandCursor)
            button.setFont(inter(10, QFont.Medium))
            button.setFixedSize(104, 34)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    color:{WHITE};
                    background:{TEAL};
                    border:1px solid {TEAL};
                    border-radius:17px;
                    padding:0 12px;
                }}
                QPushButton:hover {{
                    background:{TEAL_DARK};
                    border-color:{TEAL_DARK};
                }}
                QPushButton:pressed {{
                    background:#0f4f47;
                    border-color:#0f4f47;
                }}
                """
            )
            button.clicked.connect(lambda _checked=False, item=transaction: self._confirm_and_mark_paid(item))
            layout.addWidget(button)
        else:
            label = QLabel("-")
            label.setFont(inter(11))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")
            layout.addWidget(label)

        return wrapper

    def _show_transaction_details(self, transaction):
        dialog = TransactionDetailsDialog(transaction, read_only=self._read_only, parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted and dialog.mark_paid_requested:
            self._confirm_and_mark_paid(transaction)

    def _prompt_mark_paid(self, row_index):
        if row_index < 0 or row_index >= len(self._filtered_transactions):
            return

        transaction = self._filtered_transactions[row_index]
        self._confirm_and_mark_paid(transaction)

    def _confirm_and_mark_paid(self, transaction):
        dialog = ConfirmPaidDialog(transaction, self)
        if dialog.exec() == QDialog.Accepted:
            self._mark_transaction_paid(transaction)

    def _mark_transaction_paid(self, transaction):
        if not self._controller:
            # TODO: call controller when bound
            return
        delivery_id = transaction.get("delivery_id")
        if delivery_id is None:
            return
        self._controller.mark_paid(delivery_id)

    def _status_style(self, status):
        status_key = status.lower()
        if status_key == "paid":
            return f"color:{GREEN};background:{GREEN_BG};border:1px solid #cfe6d9;border-radius:14px;padding:0 12px;"
        return f"color:{AMBER};background:{AMBER_BG};border:1px solid #f0dfb7;border-radius:14px;padding:0 12px;"

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _format_amount(self, value):
        return f"PHP {self._safe_float(value):,.2f}"

    def _coerce_date(self, value):
        if isinstance(value, QDate):
            return value
        if isinstance(value, datetime.datetime):
            return QDate(value.year, value.month, value.day)
        if isinstance(value, datetime.date):
            return QDate(value.year, value.month, value.day)
        if isinstance(value, str):
            for fmt in ("MMM d, yyyy", "MMMM d, yyyy", "yyyy-MM-dd"):
                parsed = QDate.fromString(value, fmt)
                if parsed.isValid():
                    return parsed
        return None

    def _format_date(self, value):
        date_value = self._coerce_date(value)
        if date_value is None:
            return ""
        return date_value.toString("MMM d, yyyy")

    def _format_paid_at(self, value, payment_status):
        if str(payment_status).lower() != "paid":
            return ""
        if not value:
            return QDate.currentDate().toString("MMM d, yyyy")
        date_value = self._coerce_date(value)
        if date_value is None:
            return str(value)
        return date_value.toString("MMM d, yyyy")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TransactionView(show_topbar=True)
    win.resize(1400, 920)
    win.show()
    sys.exit(app.exec())
