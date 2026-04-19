import os
import sys
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime
from PySide6.QtGui import QFont, QFontDatabase, QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
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
        self.setFixedHeight(135)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 12)
        lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setFont(inter(10, QFont.DemiBold))
        lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.3px;background:transparent;border:none;")

        self.value_lbl = QLabel(value)
        self.value_lbl.setFont(playfair(28, QFont.Medium))
        self.value_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        dsc = QLabel(detail)
        dsc.setFont(inter(11))
        dsc.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        lay.addWidget(lbl)
        lay.addWidget(self.value_lbl)
        lay.addWidget(dsc)
        lay.addStretch()


class ConfirmPaidDialog(QDialog):
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Mark as Paid")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._transaction = transaction
        self._confirmed = False

        self.setStyleSheet(
            f"""
            QDialog {{ background:{WHITE}; }}
            QLabel {{ color:{GRAY_5}; }}
            QPushButton {{
                min-height:34px;
                border-radius:4px;
                padding:0 14px;
                font-family:'{INTER_FAMILY}';
                font-size:11px;
                font-weight:600;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(14)

        title = QLabel("Mark this transaction as paid?")
        title.setFont(playfair(18, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        summary = QLabel(
            f"{transaction.get('customer_name', '')} - {transaction.get('product_summary', '')}\n"
            f"Amount: {self._format_amount(transaction.get('total_amount'))}"
        )
        summary.setFont(inter(11))
        summary.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        root.addWidget(title)
        root.addWidget(summary)

        buttons = QDialogButtonBox(QDialogButtonBox.No | QDialogButtonBox.Yes)
        no_btn = buttons.button(QDialogButtonBox.No)
        yes_btn = buttons.button(QDialogButtonBox.Yes)
        no_btn.setText("Cancel")
        yes_btn.setText("Mark as Paid")
        no_btn.setStyleSheet(f"QPushButton{{background:{WHITE};border:1px solid {GRAY_2};color:{GRAY_5};}}")
        yes_btn.setStyleSheet(f"QPushButton{{background:{TEAL};border:1px solid {TEAL};color:{WHITE};}}")
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        root.addWidget(buttons)

    def _format_amount(self, value):
        try:
            return f"₱{float(value):,.2f}"
        except (TypeError, ValueError):
            return "₱0.00"


class TransactionView(QWidget):
    AUTO_REFRESH_INTERVAL_MS = 5000
    DEFAULT_LOOKBACK_YEARS = 10

    def __init__(self, parent=None, show_topbar=True, controller=None):
        super().__init__(parent)
        self._show_topbar = show_topbar
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
        self._status_filter.setMinimumWidth(130)
        self._status_filter.setMaximumWidth(130)
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
        #self._date_from.setMinimumWidth(140)
        self._date_from.setMaximumWidth(175)
        self._date_from.dateChanged.connect(self._on_date_from_changed)

        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDisplayFormat("MMM d, yyyy")
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setFont(inter(11))
        self._date_to.setFixedHeight(34)
        #self._date_to.setMinimumWidth(140)
        self._date_to.setMaximumWidth(175)
        self._date_to.dateChanged.connect(self._on_date_to_changed)

        self._configure_date_edit(self._date_from, min_width=120)
        self._configure_date_edit(self._date_to, min_width=120)

        from_lbl = QLabel("From")
        from_lbl.setFont(inter(10, QFont.Medium))
        from_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        to_lbl = QLabel("To")
        to_lbl.setFont(inter(10, QFont.Medium))
        to_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)
        filters_row.addWidget(self._status_filter)
        filters_row.addWidget(from_lbl)
        filters_row.addWidget(self._date_from)
        filters_row.addWidget(to_lbl)
        filters_row.addWidget(self._date_to)
        filters_row.addStretch()

        right = QVBoxLayout()
        right.setSpacing(10)
        right.setContentsMargins(0, 0, 0, 0)
        right.addLayout(filters_row)

        header_row.addLayout(left)
        header_row.addStretch()
        header_row.addLayout(right)
        content_lay.addLayout(header_row)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        self._metric_paid = MetricCard("TOTAL PAID", "₱0.00", "Sum of paid transactions", TEAL)
        self._metric_unpaid = MetricCard("TOTAL UNPAID", "₱0.00", "Sum of unpaid transactions", AMBER)
        summary_row.addWidget(self._metric_paid)
        summary_row.addWidget(self._metric_unpaid)
        content_lay.addLayout(summary_row)

        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels([
            "CUSTOMER NAME",
            "DELIVERY DATE",
            "LPG PRODUCTS",
            "TOTAL AMOUNT",
            "PAYMENT STATUS",
            "PAID AT",
            "ACTIONS",
        ])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.NoSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setWordWrap(False)
        self._table.setSortingEnabled(False)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setStyleSheet(
            f"""
            QTableWidget {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
                alternate-background-color:#fbfcfc;
                selection-background-color:{TEAL_PALE};
                selection-color:{TEAL_DARK};
                gridline-color:transparent;
            }}
            QHeaderView::section {{
                background:#f7f8f8;
                color:{GRAY_4};
                border:none;
                border-bottom:1px solid {GRAY_2};
                padding:10px 12px;
                font-family:{INTER_FAMILY};
                font-size:12px;
                font-weight:600;
                letter-spacing:1px;
                text-align:center;
            }}
            QTableWidget::item {{
                padding:4px 12px;
                border:none;
                border-bottom:1px solid #f3f5f4;
                color:{GRAY_5};
            }}
            QTableWidget::item:selected {{
                background:transparent;
                color:{GRAY_5};
                border-bottom:1px solid #f3f5f4;
            }}
            QScrollBar:horizontal {{
                border:none;
                background:{GRAY_1};
                height:6px;
                margin:0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background:{TEAL};
                border-radius:3px;
                min-width:50px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background:{TEAL_DARK};
            }}
            QScrollBar::add-line:horizontal {{
                border:none;
                background:none;
            }}
            QScrollBar::sub-line:horizontal {{
                border:none;
                background:none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background:none;
            }}
            """
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self._table.horizontalHeader().setFixedHeight(42)
        content_lay.addWidget(self._table)

        self._empty_state = QWidget()
        empty_lay = QVBoxLayout(self._empty_state)
        empty_lay.setContentsMargins(0, 36, 0, 36)
        empty_lay.setAlignment(Qt.AlignCenter)

        empty_title = QLabel("No transactions found")
        empty_title.setFont(playfair(16, QFont.Medium))
        empty_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        empty_desc = QLabel("Transactions matching the selected filters will appear here.")
        empty_desc.setFont(inter(12))
        empty_desc.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

        empty_lay.addWidget(empty_title)
        empty_lay.addWidget(empty_desc)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._table)
        self._stack.addWidget(self._empty_state)
        content_lay.addWidget(self._stack)

        scroll.setWidget(self._content)
        root.addWidget(scroll)

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
                prev_btn.setText("‹")
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
                next_btn.setText("›")
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
        self._apply_filter()

    def _on_date_to_changed(self, new_date):
        if new_date < self._date_from.date():
            self._date_from.blockSignals(True)
            self._date_from.setDate(new_date)
            self._date_from.blockSignals(False)
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
        return QDate.currentDate().addYears(-self.DEFAULT_LOOKBACK_YEARS)

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
            self._set_item(row_index, 5, self._format_paid_at(transaction.get("paid_at"), transaction.get("payment_status")))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(Qt.AlignCenter)

            if str(transaction.get("payment_status", "")).lower() == "unpaid":
                button = QPushButton("Mark as Paid")
                button.setCursor(Qt.PointingHandCursor)
                button.setFont(inter(10, QFont.Medium))
                button.setFixedHeight(30)
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        color:{WHITE};
                        background:{TEAL};
                        border:1px solid {TEAL};
                        border-radius:4px;
                        padding:0 12px;
                    }}
                    QPushButton:hover {{ background:{TEAL_DARK}; border-color:{TEAL_DARK}; }}
                    """
                )
                button.clicked.connect(lambda _, index=row_index: self._prompt_mark_paid(index))
                action_layout.addWidget(button)

            self._table.setCellWidget(row_index, 6, action_widget)

        self._table.resizeRowsToContents()

    def _prompt_mark_paid(self, row_index):
        if row_index < 0 or row_index >= len(self._filtered_transactions):
            return

        transaction = self._filtered_transactions[row_index]
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

    def _set_item(self, row, column, value):
        item = QTableWidgetItem(str(value))
        item.setFont(inter(11))
        item.setTextAlignment(Qt.AlignCenter)
        self._table.setItem(row, column, item)

    def _set_status_pill(self, row, column, value):
        status = str(value).strip()
        label = QLabel(status.title() if status else "Unpaid")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(inter(10, QFont.DemiBold))
        label.setMinimumHeight(24)
        label.setStyleSheet(self._status_style(status))

        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(6, 6, 6, 6)
        wrapper_layout.setAlignment(Qt.AlignCenter)
        wrapper_layout.addWidget(label)
        self._table.setCellWidget(row, column, wrapper)

    def _status_style(self, status):
        status_key = status.lower()
        if status_key == "paid":
            return f"color:{GREEN};background:{GREEN_BG};border:1px solid #cfe6d9;border-radius:12px;padding:0 12px;"
        return f"color:{AMBER};background:{AMBER_BG};border:1px solid #f0dfb7;border-radius:12px;padding:0 12px;"

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _format_amount(self, value):
        return f"₱{self._safe_float(value):,.2f}"

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
