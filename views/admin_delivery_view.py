import os
import sys
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime, QSortFilterProxyModel, QRect, QSize
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPen, QPixmap, QStandardItemModel, QStandardItem, QIcon, QTextCharFormat
from PySide6.QtWidgets import (
	QApplication,
	QMainWindow,
	QWidget,
	QHBoxLayout,
	QVBoxLayout,
	QLabel,
	QPushButton,
	QFrame,
	QScrollArea,
	QSizePolicy,
	QLineEdit,
	QDateEdit,
	QCalendarWidget,
	QComboBox,
	QTextEdit,
	QToolButton,
	QMenu,
	QTableView,
	QHeaderView,
	QAbstractItemView,
	QStyle,
	QStyledItemDelegate,
	QStackedWidget,
	QGraphicsDropShadowEffect,
	QSpinBox,
	QMessageBox,
)

from controllers.delivery_controller import DeliveryController
from controllers.login_controller import LoginController

BASE_DIR = PROJECT_ROOT
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
MODERN_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_modern.svg")
WHITE_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_white.svg")

TEAL = "#1A7A6E"
TEAL_DARK = "#145F55"
TEAL_MID = "#1d8a7c"
TEAL_LIGHT = "#2aa898"
TEAL_PALE = "#e8f5f3"
TEAL_PALE2 = "#d0ede9"
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
RED_BTN = "#c0392b"

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
	for f in fonts:
		path = os.path.join(FONTS_DIR, f)
		if os.path.exists(path):
			fid = QFontDatabase.addApplicationFont(path)
			if fid != -1:
				families = QFontDatabase.applicationFontFamilies(fid)
				if families:
					if f.startswith("PlayfairDisplay"):
						PLAYFAIR_FAMILY = families[0]
					elif f == "Inter_18pt-Regular.ttf":
						INTER_FAMILY = families[0]


def playfair(size, weight=QFont.Normal):
	f = QFont(PLAYFAIR_FAMILY, size)
	f.setWeight(weight)
	return f


def inter(size, weight=QFont.Normal):
	f = QFont(INTER_FAMILY, size)
	f.setWeight(weight)
	return f


def display_status(status):
	raw = str(status or "").strip().lower().replace("-", "_").replace(" ", "_")
	return {
		"pending": "Pending",
		"in_transit": "In Transit",
		"delivered": "Delivered",
		"cancelled": "Cancelled",
		"completed": "Delivered",
		"complete": "Delivered",
		"done": "Delivered",
		"transit": "In Transit",
		"on_delivery": "In Transit",
		"on_the_way": "In Transit",
	}.get(raw, str(status or "").strip().replace("_", " ").title())


def db_status(status):
	return str(status or "").strip().lower().replace("-", "_").replace(" ", "_")


def display_item_type(item_type):
	return str(item_type or "").strip().replace("_", " ").title()


def _qss_path(path):
	return path.replace("\\", "/")


def _combo_style(min_height=34, min_width=None):
	min_width_rule = f"min-width:{min_width}px;" if min_width else ""
	icon_path = _qss_path(MODERN_CHEVRON_ICON)
	return f"""
	QComboBox {{
		color:{GRAY_5};
		background:#fbfcfc;
		border:1px solid #d6e2df;
		border-radius:8px;
		padding:0 34px 0 12px;
		min-height:{min_height}px;
		{min_width_rule}
	}}
	QComboBox:hover {{
		border-color:#b9d4cf;
		background:{WHITE};
	}}
	QComboBox:focus {{
		border:1px solid {TEAL};
		background:{WHITE};
	}}
	QComboBox::drop-down {{
		subcontrol-origin: padding;
		subcontrol-position: top right;
		width:30px;
		border-left:1px solid #e0ece9;
		border-top-right-radius:8px;
		border-bottom-right-radius:8px;
		background:#f4faf9;
	}}
	QComboBox::down-arrow {{
		image:url({icon_path});
		width:12px;
		height:12px;
	}}
	QComboBox QAbstractItemView {{
		border:1px solid #cfe1dd;
		background:{WHITE};
		selection-background-color:{TEAL_PALE};
		selection-color:{TEAL_DARK};
		padding:4px;
		outline:none;
	}}
	"""


def _calendar_style():
	return f"""
	QCalendarWidget {{
		background:#f6f6f6;
		border:1px solid #c8c8c8;
		border-radius:18px;
	}}
	QCalendarWidget QWidget#qt_calendar_navigationbar {{
		background:#f6f6f6;
		border:none;
		padding:12px 12px 8px 12px;
		border-top-left-radius:18px;
		border-top-right-radius:18px;
	}}
	QCalendarWidget QToolButton {{
		color:#2e2e2e;
		font-family:'{INTER_FAMILY}';
		font-size:13px;
		font-weight:500;
		background:#f0f0f0;
		border:1px solid #cdcdcd;
		min-height:30px;
		border:none;
		padding:6px 12px;
		border-radius:12px;
	}}
	QCalendarWidget QToolButton:hover {{
		background:#e9e9e9;
	}}
	QCalendarWidget QToolButton#qt_calendar_prevmonth,
	QCalendarWidget QToolButton#qt_calendar_nextmonth {{
		font-size:18px;
		font-weight:500;
		background:transparent;
		border:none;
		min-width:26px;
		min-height:26px;
		padding:0px;
		border-radius:8px;
	}}
	QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
	QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {{
		background:#e9e9e9;
	}}
	QCalendarWidget QToolButton#qt_calendar_monthbutton {{
		min-width:92px;
		background:#f1f1f1;
		border:1px solid #d0d0d0;
		border-radius:14px;
		padding:6px 22px 6px 12px;
	}}
	QCalendarWidget QToolButton#qt_calendar_yearbutton {{
		min-width:82px;
		background:#f1f1f1;
		border:1px solid #d0d0d0;
		border-radius:14px;
		padding:6px 22px 6px 12px;
	}}
	QCalendarWidget QMenu {{
		background:#fdfdfd;
		border:1px solid #d2d2d2;
	}}
	QCalendarWidget QSpinBox {{
		color:#2e2e2e;
		background:#f1f1f1;
		border:1px solid #d0d0d0;
		border-radius:12px;
		padding:2px 8px;
		min-width:78px;
	}}
	QCalendarWidget QWidget#qt_calendar_calendarview {{
		border:none;
		background:#f6f6f6;
		selection-background-color:#2d2f34;
		selection-color:#ffffff;
		alternate-background-color:#f6f6f6;
	}}
	QCalendarWidget QAbstractItemView {{
		font-family:'{INTER_FAMILY}';
		font-size:13px;
		font-weight:500;
		padding:10px;
		outline:0;
		border:none;
		background:#f6f6f6;
		color:#2b2b2b;
	}}
	QCalendarWidget QAbstractItemView:item {{
		padding:10px;
		border-radius:12px;
		margin:2px;
	}}
	QCalendarWidget QAbstractItemView:item:hover {{
		background:#e8e8e8;
		color:#2b2b2b;
	}}
	QCalendarWidget QAbstractItemView:item:selected {{
		background:#2d2f34;
		color:#ffffff;
		font-weight:600;
	}}
	QCalendarWidget QTableView {{
		selection-background-color:#2d2f34;
		selection-color:#ffffff;
		background:#f7f7f7;
		border:none;
	}}
	QCalendarWidget QTableView::item:disabled {{
		color:#b5b5b5;
	}}
	QCalendarWidget QTableView::item:today {{
		border:1px solid #ababab;
		background:#ececec;
		color:#2f2f2f;
		font-weight:600;
	}}
	QCalendarWidget QHeaderView::section {{
		background:#f6f6f6;
		color:#7a7a7a;
		border:none;
		padding:6px 0 10px 0;
		font-family:'{INTER_FAMILY}';
		font-size:11px;
		font-weight:500;
		letter-spacing:0.2px;
	}}
	QCalendarWidget QAbstractItemView:enabled {{
		color:#2b2b2b;
		background:#f6f6f6;
		selection-background-color:#2d2f34;
		selection-color:#ffffff;
		outline:0;
		border:none;
	}}
	QCalendarWidget QAbstractItemView:disabled {{
		color:#b5b5b5;
	}}
	"""


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
	QCalendarWidget QSpinBox::up-arrow {{
		image:none;
		width:0px;
		height:0px;
		border-left:4px solid transparent;
		border-right:4px solid transparent;
		border-bottom:6px solid {WHITE};
	}}
	QCalendarWidget QSpinBox::down-arrow {{
		image:none;
		width:0px;
		height:0px;
		border-left:4px solid transparent;
		border-right:4px solid transparent;
		border-top:6px solid {WHITE};
	}}
	QCalendarWidget QAbstractItemView:enabled {{
		color:{GRAY_5};
	}}
	QCalendarWidget QWidget#qt_calendar_calendarview,
	QCalendarWidget QTableView {{
		background:{WHITE};
		alternate-background-color:{WHITE};
		color:{GRAY_5};
	}}
	QCalendarWidget QMenu {{
		background:{WHITE};
		color:{TEAL_DARK};
		border:1px solid {GRAY_2};
		font-family:'{INTER_FAMILY}';
		font-size:12px;
	}}
	QCalendarWidget QMenu::item {{
		color:{TEAL_DARK};
		padding:4px 14px;
	}}
	QCalendarWidget QMenu::item:selected {{
		background:{TEAL_PALE};
		color:{TEAL_DARK};
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

	# Hide the native year spin editor; use a modern dropdown like the month button.
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


def apply_modern_combo(combo, min_height=34, min_width=None):
	combo.setStyleSheet(_combo_style(min_height=min_height, min_width=min_width))


def apply_modern_date_edit(date_edit, min_height=34, min_width=None):
	date_edit.setStyleSheet(_date_edit_style(min_height=min_height, min_width=min_width))
	calendar = date_edit.calendarWidget()
	if calendar is not None:
		calendar.setFont(inter(11))
		calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
		calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
		calendar.setGridVisible(False)
		calendar.setMinimumSize(320, 260)
		# Keep native popup while forcing readable text colors for month/year controls.
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

		# Force native prev/next controls to white chevrons to avoid dark-theme black arrows.
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


class SummaryCard(QFrame):
	def __init__(self, label, top_color, parent=None):
		super().__init__(parent)
		self._top_color = QColor(top_color)
		self.setFixedHeight(108)
		self.setStyleSheet(
			f"""
			QFrame {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:6px;
			}}
			"""
		)

		lay = QVBoxLayout(self)
		lay.setContentsMargins(14, 12, 14, 10)
		lay.setSpacing(2)

		title = QLabel(label)
		title.setFont(inter(10, QFont.DemiBold))
		title.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.3px;background:transparent;border:none;")

		self._value_lbl = QLabel("0")
		self._value_lbl.setFont(playfair(26, QFont.Medium))
		self._value_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		lay.addWidget(title)
		lay.addWidget(self._value_lbl)
		lay.addStretch()

	def set_value(self, value):
		self._value_lbl.setText(str(value))

	def paintEvent(self, event):
		super().paintEvent(event)
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		p.setPen(Qt.NoPen)
		p.setBrush(self._top_color)
		p.drawRoundedRect(0, 0, self.width(), 3, 1, 1)


class DeliveryFilterProxy(QSortFilterProxyModel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._status = "All Statuses"
		self._customer_text = ""
		self._date_filter = None

	def set_status(self, status):
		self._status = status
		self.invalidate()

	def set_customer_text(self, text):
		self._customer_text = text.strip().lower()
		self.invalidate()

	def set_date_filter(self, qdate_or_none):
		self._date_filter = qdate_or_none
		self.invalidate()

	def filterAcceptsRow(self, source_row, source_parent):
		model = self.sourceModel()
		customer_item = model.item(source_row, 0)
		date_item = model.item(source_row, 1)
		status_item = model.item(source_row, 4)

		if customer_item is None or date_item is None or status_item is None:
			return False

		status = status_item.text()
		customer_blob = (customer_item.text() + " " + str(customer_item.data(Qt.UserRole + 1) or "")).lower()
		schedule_qdate = date_item.data(Qt.UserRole + 2)

		if self._status != "All Statuses" and status != self._status:
			return False
		if self._customer_text and self._customer_text not in customer_blob:
			return False
		if self._date_filter is not None and schedule_qdate != self._date_filter:
			return False
		return True


class DeliveryItemRow(QWidget):
	def __init__(self, products, parent=None):
		super().__init__(parent)
		self._products = list(products or [])
		self.setStyleSheet("background:transparent;border:none;")
		icon_path = _qss_path(MODERN_CHEVRON_ICON)

		lay = QHBoxLayout(self)
		lay.setContentsMargins(0, 5, 0, 5)
		lay.setSpacing(8)

		self.product_combo = QComboBox()
		self.product_combo.setFont(inter(11))
		self._fill_products()
		self.product_combo.setStyleSheet(
			f"""
			QComboBox {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid #d6e2df;border-radius:10px;
				padding:0 34px 0 12px;min-height:34px;
			}}
			QComboBox:hover {{ border-color:#b9d4cf; }}
			QComboBox:focus {{ border-color:{TEAL}; }}
			QComboBox::drop-down {{
				subcontrol-origin: padding;
				subcontrol-position: top right;
				width:30px;
				border:none;
				background:transparent;
			}}
			QComboBox::down-arrow {{
				image:url({icon_path});
				width:12px;
				height:12px;
			}}
			QComboBox QAbstractItemView {{
				border:1px solid #cfe1dd;
				background:{WHITE};
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
				padding:4px;
				outline:none;
			}}
			"""
		)

		self.qty_spin = QSpinBox()
		self.qty_spin.setRange(1, 99)
		self.qty_spin.setValue(1)
		self.qty_spin.setFont(inter(11))
		self.qty_spin.setStyleSheet(
			f"""
			QSpinBox {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid #d6e2df;border-radius:10px;
				padding:0 26px 0 10px;min-height:34px;min-width:86px;
			}}
			QSpinBox:hover {{ border-color:#b9d4cf; }}
			QSpinBox:focus {{ border-color:{TEAL}; }}
			QSpinBox::up-button, QSpinBox::down-button {{
				subcontrol-origin:border;
				width:20px;
				right:4px;
				border:none;
				background:transparent;
			}}
			QSpinBox::up-button {{ top:3px; height:13px; }}
			QSpinBox::down-button {{ bottom:3px; height:13px; }}
			QSpinBox::up-arrow {{
				image:none;
				width:0;height:0;
			}}
			QSpinBox::down-arrow {{
				image:none;
				width:0;height:0;
			}}
			"""
		)
		self.qty_spin.setButtonSymbols(QSpinBox.PlusMinus)

		self.type_combo = QComboBox()
		self.type_combo.setFont(inter(11))
		self.type_combo.addItems(["Refill", "New Tank"])
		self.type_combo.setStyleSheet(
			f"""
			QComboBox {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid #d6e2df;border-radius:10px;
				padding:0 34px 0 12px;min-height:34px;min-width:120px;
			}}
			QComboBox:hover {{ border-color:#b9d4cf; }}
			QComboBox:focus {{ border-color:{TEAL}; }}
			QComboBox::drop-down {{
				subcontrol-origin: padding;
				subcontrol-position: top right;
				width:30px;
				border:none;
				background:transparent;
			}}
			QComboBox::down-arrow {{
				image:url({icon_path});
				width:12px;
				height:12px;
			}}
			QComboBox QAbstractItemView {{
				border:1px solid #cfe1dd;
				background:{WHITE};
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
				padding:4px;
				outline:none;
			}}
			"""
		)

		self.remove_btn = QPushButton("Remove")
		self.remove_btn.setCursor(Qt.PointingHandCursor)
		self.remove_btn.setFont(inter(10, QFont.Medium))
		self.remove_btn.setFixedHeight(32)
		self.remove_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{RED_BTN};background:{RED_BG};
				border:1px solid #f1c0bc;border-radius:4px;padding:0 12px;
			}}
			QPushButton:hover {{ background:#f8d8d5; }}
			"""
		)

		lay.addWidget(self.product_combo, 1)
		lay.addWidget(self.qty_spin)
		lay.addWidget(self.type_combo)
		lay.addWidget(self.remove_btn)

	def item_data(self):
		return {
			"product_id": self.product_combo.currentData(),
			"quantity": self.qty_spin.value(),
			"type": self.type_combo.currentText(),
		}

	def set_products(self, products):
		self._products = list(products or [])
		self._fill_products()

	def _fill_products(self):
		current_id = self.product_combo.currentData()
		self.product_combo.blockSignals(True)
		self.product_combo.clear()
		for product in self._products:
			self.product_combo.addItem(product["name"], product["id"])
		if current_id is not None:
			idx = self.product_combo.findData(current_id)
			if idx != -1:
				self.product_combo.setCurrentIndex(idx)
		self.product_combo.blockSignals(False)


def make_field(label_text, widget, required=True):
	"""Create a labeled field wrapper matching Add Customer form style"""
	grp = QWidget()
	grp.setStyleSheet("background:transparent;border:none;")
	g_lay = QVBoxLayout(grp)
	g_lay.setContentsMargins(0, 0, 0, 0)
	g_lay.setSpacing(6)

	row = QHBoxLayout()
	row.setSpacing(4)
	lbl = QLabel(label_text.upper())
	lbl.setFont(inter(10, QFont.DemiBold))
	lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.2px;background:transparent;border:none;")
	row.addWidget(lbl)
	if required:
		req = QLabel("*")
		req.setFont(inter(11, QFont.DemiBold))
		req.setStyleSheet("color:#c0392b;background:transparent;border:none;")
		row.addWidget(req)
	row.addStretch()
	g_lay.addLayout(row)
	g_lay.addWidget(widget)
	return grp


class NewDeliveryModal(QWidget):
	def __init__(self, customers, products, parent=None):
		super().__init__(parent)
		self._customers = list(customers or [])
		self._products = list(products or [])
		self._rows = []
		self._callback = None
		self._overlay_margin = 0
		self._drag_active = False
		self._drag_offset = None
		self._header_drag_height = 74
		self.setStyleSheet(f"background:{WHITE};")
		self.hide()
		icon_path = _qss_path(MODERN_CHEVRON_ICON)

		self._card = QFrame(self)
		self._card.setObjectName("newDeliveryCard")
		self._card.setStyleSheet(
			f"""
			QFrame#newDeliveryCard {{
				background:{WHITE};
				border:1px solid {WHITE};
				border-radius:0px;
			}}
			"""
		)
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(42)
		shadow.setOffset(0, 10)
		shadow.setColor(QColor(0, 0, 0, 60))
		self._card.setGraphicsEffect(shadow)
		self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		card_lay = QVBoxLayout(self._card)
		card_lay.setContentsMargins(0, 0, 0, 0)
		card_lay.setSpacing(0)

		header = QWidget()
		header.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")
		h_lay = QHBoxLayout(header)
		h_lay.setContentsMargins(22, 16, 22, 14)

		title = QLabel("Schedule New Delivery")
		title.setFont(playfair(16, QFont.DemiBold))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
		h_lay.addWidget(title)
		h_lay.addStretch()
		card_lay.addWidget(header)

		self._form_scroll = QScrollArea()
		self._form_scroll.setWidgetResizable(True)
		self._form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._form_scroll.setStyleSheet(
			f"""
			QScrollArea {{ background:{WHITE}; border:none; }}
			QScrollBar:vertical {{ background:transparent; width:11px; margin:8px 4px 8px 0; }}
			QScrollBar::handle:vertical {{
				background:rgba(26,122,110,0.30);
				min-height:34px; border-radius:5px; border:1px solid rgba(26,122,110,0.18);
			}}
			QScrollBar::handle:vertical:hover {{
				background:rgba(26,122,110,0.48);
				border:1px solid rgba(26,122,110,0.26);
			}}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; border:none; background:transparent; }}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:transparent; }}
			"""
		)

		body = QWidget()
		body.setStyleSheet(f"background:{WHITE};border:none;")
		b_lay = QVBoxLayout(body)
		b_lay.setContentsMargins(22, 18, 22, 18)
		b_lay.setSpacing(12)

		top_fields = QHBoxLayout()
		top_fields.setSpacing(10)

		self.customer_combo = QComboBox()
		self.customer_combo.setFont(inter(12))
		self._fill_customers()
		self.customer_combo.setStyleSheet(
			f"""
			QComboBox {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid #d6e2df;border-radius:10px;
				padding:0 34px 0 12px;min-height:36px;
			}}
			QComboBox:hover {{ border-color:#b9d4cf; }}
			QComboBox:focus {{ border-color:{TEAL}; }}
			QComboBox::drop-down {{
				subcontrol-origin: padding;
				subcontrol-position: top right;
				width:30px;
				border:none;
				background:transparent;
			}}
			QComboBox::down-arrow {{
				image:url({icon_path});
				width:12px;
				height:12px;
			}}
			QComboBox QAbstractItemView {{
				border:1px solid #cfe1dd;
				background:{WHITE};
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
				padding:4px;
				outline:none;
			}}
			"""
		)

		self.schedule_date = QDateEdit()
		self.schedule_date.setCalendarPopup(True)
		self.schedule_date.setDate(QDate.currentDate())
		self.schedule_date.setFont(inter(12))
		apply_modern_date_edit(self.schedule_date, min_height=36, min_width=140)
		calendar = self.schedule_date.calendarWidget()
		if calendar is not None:
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

		top_fields.addWidget(make_field("Customer", self.customer_combo, required=True), 1)
		top_fields.addWidget(make_field("Schedule Date", self.schedule_date, required=True), 1)
		b_lay.addLayout(top_fields)

		items_header = QHBoxLayout()
		items_header.setSpacing(8)

		items_lbl = QLabel("ITEMS")
		items_lbl.setFont(inter(10, QFont.DemiBold))
		items_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.2px;background:transparent;border:none;")

		self.add_item_btn = QPushButton("+ Add Item")
		self.add_item_btn.setCursor(Qt.PointingHandCursor)
		self.add_item_btn.setFont(inter(11, QFont.Medium))
		self.add_item_btn.setFixedHeight(30)
		self.add_item_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{TEAL_DARK};background:{TEAL_PALE};
				border:1px solid {TEAL_PALE2};border-radius:4px;padding:0 12px;
			}}
			QPushButton:hover {{ background:{TEAL_PALE2}; }}
			"""
		)
		self.add_item_btn.clicked.connect(self._add_row)

		items_header.addWidget(items_lbl)
		items_header.addStretch()
		items_header.addWidget(self.add_item_btn)
		b_lay.addLayout(items_header)

		cols = QWidget()
		cols.setStyleSheet("background:transparent;border:none;")
		cols_lay = QHBoxLayout(cols)
		cols_lay.setContentsMargins(4, 0, 2, 0)
		cols_lay.setSpacing(8)

		for text, stretch in [("PRODUCT", 6), ("QTY", 1), ("TYPE", 2), ("", 1)]:
			lbl = QLabel(text)
			lbl.setFont(inter(9, QFont.DemiBold))
			lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.1px;background:transparent;border:none;")
			if text:
				cols_lay.addWidget(lbl, stretch)
			else:
				cols_lay.addSpacing(72)
		b_lay.addWidget(cols)

		self.rows_holder = QWidget()
		self.rows_holder.setStyleSheet("background:transparent;border:none;")
		self.rows_lay = QVBoxLayout(self.rows_holder)
		self.rows_lay.setContentsMargins(0, 0, 0, 2)
		self.rows_lay.setSpacing(18)
		b_lay.addWidget(self.rows_holder)

		self._est_total_lbl = QLabel("Estimated total: Php 0.00")
		self._est_total_lbl.setFont(inter(11, QFont.Medium))
		self._est_total_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
		b_lay.addWidget(self._est_total_lbl, 0, Qt.AlignRight)

		self.notes = QTextEdit()
		self.notes.setPlaceholderText("Optional notes for rider...")
		self.notes.setFont(inter(11, QFont.Normal))
		self.notes.setFixedHeight(88)
		self.notes.setStyleSheet(
			f"""
			QTextEdit {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {GRAY_2};border-radius:4px;
				padding:6px 10px;font-family:':{INTER_FAMILY}';
			}}
			QTextEdit:focus {{ border-color:{TEAL}; }}
			"""
		)
		b_lay.addWidget(make_field("Notes", self.notes, required=False))

		self.error_lbl = QLabel("")
		self.error_lbl.setFont(inter(11))
		self.error_lbl.setStyleSheet(f"color:{RED_BTN};background:transparent;border:none;")
		self.error_lbl.hide()
		b_lay.addWidget(self.error_lbl)

		self._form_scroll.setWidget(body)
		card_lay.addWidget(self._form_scroll, 1)

		footer = QWidget()
		footer.setStyleSheet(f"background:{WHITE};border:none;")
		f_lay = QHBoxLayout(footer)
		f_lay.setContentsMargins(22, 12, 22, 14)
		f_lay.setSpacing(10)
		f_lay.addStretch()

		cancel_btn = QPushButton("Cancel")
		cancel_btn.setCursor(Qt.PointingHandCursor)
		cancel_btn.setFont(inter(12, QFont.Medium))
		cancel_btn.setFixedHeight(34)
		cancel_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {TEAL_PALE2};border-radius:4px;padding:0 18px;
			}}
			QPushButton:hover {{ background:{WHITE};border-color:{TEAL}; }}
			"""
		)
		cancel_btn.clicked.connect(self._cancel)

		save_btn = QPushButton("Save Delivery")
		save_btn.setCursor(Qt.PointingHandCursor)
		save_btn.setFont(inter(12, QFont.Medium))
		save_btn.setFixedHeight(34)
		save_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{WHITE};background:{TEAL};
				border:1px solid {TEAL};border-radius:4px;padding:0 18px;
			}}
			QPushButton:hover {{ background:{TEAL_DARK};border-color:{TEAL_DARK}; }}
			"""
		)
		save_btn.clicked.connect(self._save)

		f_lay.addWidget(cancel_btn)
		f_lay.addWidget(save_btn)
		card_lay.addWidget(footer)

		self._add_row()

	def set_options(self, customers, products):
		"""Refresh dropdown options when data changes."""
		self._customers = list(customers or [])
		self._products = list(products or [])
		self._fill_customers()
		for row in self._rows:
			row.set_products(self._products)
		self._update_total_estimate()

	def _add_row(self):
		row = DeliveryItemRow(self._products)
		row.remove_btn.clicked.connect(lambda: self._remove_row(row))
		row.product_combo.currentIndexChanged.connect(self._update_total_estimate)
		row.qty_spin.valueChanged.connect(self._update_total_estimate)
		row.type_combo.currentIndexChanged.connect(self._update_total_estimate)
		self._rows.append(row)
		self.rows_lay.addWidget(row)
		self._update_remove_buttons()
		self._update_total_estimate()
		self._reflow_card()

	def _remove_row(self, row_widget):
		if len(self._rows) == 1:
			return
		self._rows.remove(row_widget)
		self.rows_lay.removeWidget(row_widget)
		row_widget.setParent(None)
		row_widget.deleteLater()
		self._update_remove_buttons()
		self._update_total_estimate()
		self._reflow_card()

	def _fill_customers(self):
		current = self.customer_combo.currentData()
		self.customer_combo.blockSignals(True)
		self.customer_combo.clear()
		for c in self._customers:
			self.customer_combo.addItem(f"{c['name']} ({c['contact']})", c["id"])
		if current is not None:
			idx = self.customer_combo.findData(current)
			if idx != -1:
				self.customer_combo.setCurrentIndex(idx)
		self.customer_combo.blockSignals(False)

	def _update_remove_buttons(self):
		removable = len(self._rows) > 1
		for row in self._rows:
			row.remove_btn.setVisible(removable)

	def _product_by_id(self, product_id):
		for p in self._products:
			if p["id"] == product_id:
				return p
		return None

	def _update_total_estimate(self):
		total = 0.0
		for row in self._rows:
			prod_id = row.product_combo.currentData()
			prod = self._product_by_id(prod_id)
			if prod:
				qty = row.qty_spin.value()
				is_refill = row.type_combo.currentText() == "Refill"
				price = prod["refill_price"] if is_refill else prod["new_tank_price"]
				try:
					price = float(price)
				except Exception:
					price = 0.0
				total += qty * price
		self._est_total_lbl.setText(f"Estimated total: Php {total:.2f}")

	def open(self, callback):
		self._callback = callback
		self._reset_form()
		self._drag_active = False
		self._drag_offset = None

		if self.parent():
			self.setGeometry(self.parent().rect())
		self._reflow_card()
		self.show()
		self.raise_()

	def _cancel(self):
		self._reset_form()
		self.hide()

	def _reset_form(self):
		self.error_lbl.hide()
		self.notes.clear()
		self.customer_combo.setCurrentIndex(0)
		self.schedule_date.setDate(QDate.currentDate())

		while len(self._rows) > 1:
			row = self._rows[-1]
			self._rows.remove(row)
			self.rows_lay.removeWidget(row)
			row.setParent(None)
			row.deleteLater()

		if self._rows:
			self._rows[0].qty_spin.setValue(1)
			self._rows[0].product_combo.setCurrentIndex(0)
			self._rows[0].type_combo.setCurrentIndex(0)

		self._update_remove_buttons()
		self._update_total_estimate()
		if hasattr(self, "_form_scroll") and self._form_scroll.verticalScrollBar() is not None:
			self._form_scroll.verticalScrollBar().setValue(0)
		self._reflow_card()

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._reflow_card()
		super().resizeEvent(event)

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self.hide()
			return

		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= self._header_drag_height:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active and self._drag_offset is not None:
			target = event.position().toPoint() - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			x = max(0, min(target.x(), max_x))
			y = max(0, min(target.y(), max_y))
			self._card.move(x, y)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self._drag_active = False
		self._drag_offset = None
		super().mouseReleaseEvent(event)

	def _reflow_card(self):
		margin = self._overlay_margin
		self._card.adjustSize()
		self._card.setGeometry(0, 0, self.width(), self.height())

	def _save(self):
		if not self._customers:
			self.error_lbl.setText("No customer records available.")
			self.error_lbl.show()
			return

		schedule_date = self.schedule_date.date()
		if schedule_date < QDate.currentDate():
			self.error_lbl.setText("Schedule date cannot be in the past.")
			self.error_lbl.show()
			return

		items = []
		for row in self._rows:
			items.append(row.item_data())

		if not items:
			self.error_lbl.setText("Add at least one delivery item.")
			self.error_lbl.show()
			return

		data = {
			"customer_id": self.customer_combo.currentData(),
			"schedule_date": schedule_date,
			"notes": self.notes.toPlainText().strip(),
			"items": items,
		}

		self.error_lbl.hide()
		if self._callback:
			self._callback(data)
		self.hide()


class DeliveryStatusModal(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet("background:rgba(0,0,0,100);")
		self._callback = None
		self._delivery_id = None
		self._drag_active = False
		self._drag_offset = None
		self._header_drag_height = 72
		self.hide()

		self._card = QFrame(self)
		self._card.setFixedWidth(420)
		self._card.setObjectName("statusCard")
		self._card.setStyleSheet(
			f"""
			QFrame#statusCard {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:8px;
			}}
			"""
		)
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(34)
		shadow.setOffset(0, 8)
		shadow.setColor(QColor(0, 0, 0, 60))
		self._card.setGraphicsEffect(shadow)

		lay = QVBoxLayout(self._card)
		lay.setContentsMargins(20, 18, 20, 18)
		lay.setSpacing(10)

		title = QLabel("Update Delivery Status")
		title.setFont(playfair(16, QFont.DemiBold))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		self.current_lbl = QLabel("Current: Pending")
		self.current_lbl.setFont(inter(11))
		self.current_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		self.status_combo = QComboBox()
		self.status_combo.setFont(inter(12))
		apply_modern_combo(self.status_combo, min_height=34)

		lay.addWidget(title)
		lay.addWidget(self.current_lbl)
		lay.addWidget(self.status_combo)

		row = QHBoxLayout()
		row.setSpacing(10)
		row.addStretch()

		cancel_btn = QPushButton("Cancel")
		cancel_btn.setCursor(Qt.PointingHandCursor)
		cancel_btn.setFont(inter(11, QFont.Medium))
		cancel_btn.setFixedHeight(32)
		cancel_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {GRAY_2};border-radius:4px;padding:0 16px;
			}}
			QPushButton:hover {{ background:{GRAY_1}; }}
			"""
		)
		cancel_btn.clicked.connect(self.hide)

		save_btn = QPushButton("Save")
		save_btn.setCursor(Qt.PointingHandCursor)
		save_btn.setFont(inter(11, QFont.Medium))
		save_btn.setFixedHeight(32)
		save_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{WHITE};background:{TEAL};
				border:1px solid {TEAL};border-radius:4px;padding:0 16px;
			}}
			QPushButton:hover {{ background:{TEAL_DARK};border-color:{TEAL_DARK}; }}
			"""
		)
		save_btn.clicked.connect(self._save)

		row.addWidget(cancel_btn)
		row.addWidget(save_btn)
		lay.addLayout(row)

	def open(self, delivery, callback):
		self._delivery_id = delivery["id"]
		self._callback = callback
		current = display_status(delivery.get("status", ""))
		self.current_lbl.setText(f"Current: {current}")

		allowed = {
			"Pending": ["Pending", "In Transit", "Delivered", "Cancelled"],
			"In Transit": ["In Transit", "Delivered", "Cancelled"],
			"Delivered": ["Delivered"],
			"Cancelled": ["Cancelled"],
		}
		default_options = ["Pending", "In Transit", "Delivered", "Cancelled"]
		self.status_combo.clear()
		for s in allowed.get(current, default_options):
			self.status_combo.addItem(s)
		if self.status_combo.findText(current) >= 0:
			self.status_combo.setCurrentText(current)
		else:
			self.status_combo.setCurrentIndex(0)

		if self.parent():
			self.setGeometry(self.parent().rect())
		self._center_card()
		self.show()
		self.raise_()

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._center_card()
		super().resizeEvent(event)

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self.hide()
			return
		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= self._header_drag_height:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active and self._drag_offset is not None:
			target = event.position().toPoint() - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			x = max(0, min(target.x(), max_x))
			y = max(0, min(target.y(), max_y))
			self._card.move(x, y)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self._drag_active = False
		self._drag_offset = None
		super().mouseReleaseEvent(event)

	def _center_card(self):
		x = (self.width() - self._card.width()) // 2
		y = (self.height() - self._card.height()) // 2
		self._card.move(max(0, x), max(0, y))

	def _save(self):
		if self._callback and self._delivery_id is not None:
			self._callback(self._delivery_id, self.status_combo.currentText())
		self.hide()


class DeliverySavedModal(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet("background:rgba(10,18,16,115);")
		self._drag_active = False
		self._drag_offset = None
		self._header_drag_height = 96
		self.hide()

		self._card = QFrame(self)
		self._card.setFixedWidth(440)
		self._card.setObjectName("deliverySavedCard")
		self._card.setStyleSheet(
			f"""
			QFrame#deliverySavedCard {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:18px;
			}}
			"""
		)
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(40)
		shadow.setOffset(0, 14)
		shadow.setColor(QColor(0, 0, 0, 70))
		self._card.setGraphicsEffect(shadow)

		lay = QVBoxLayout(self._card)
		lay.setContentsMargins(28, 26, 28, 24)
		lay.setSpacing(14)

		badge_wrap = QWidget()
		badge_lay = QHBoxLayout(badge_wrap)
		badge_lay.setContentsMargins(0, 0, 0, 0)
		badge_lay.setSpacing(0)
		badge_lay.setAlignment(Qt.AlignCenter)

		self._icon_badge = QLabel("✓")
		self._icon_badge.setAlignment(Qt.AlignCenter)
		self._icon_badge.setFixedSize(62, 62)
		self._icon_badge.setFont(inter(22, QFont.DemiBold))
		self._icon_badge.setStyleSheet(
			f"color:{WHITE};background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {TEAL}, stop:1 {TEAL_LIGHT});"
			"border-radius:31px;border:3px solid rgba(255,255,255,0.75);"
		)
		badge_lay.addWidget(self._icon_badge)

		self._title_lbl = QLabel("Delivery scheduled")
		self._title_lbl.setAlignment(Qt.AlignCenter)
		self._title_lbl.setFont(playfair(20, QFont.DemiBold))
		self._title_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		self._message_lbl = QLabel("The delivery has been scheduled successfully.")
		self._message_lbl.setWordWrap(True)
		self._message_lbl.setAlignment(Qt.AlignCenter)
		self._message_lbl.setFont(inter(12))
		self._message_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		self._hint_lbl = QLabel("You can review the details in the delivery list below.")
		self._hint_lbl.setWordWrap(True)
		self._hint_lbl.setAlignment(Qt.AlignCenter)
		self._hint_lbl.setFont(inter(11))
		self._hint_lbl.setStyleSheet(
			f"color:{GRAY_5};background:{TEAL_PALE};border:1px solid #d7ebe7;border-radius:10px;padding:10px 12px;"
		)

		self._ok_btn = QPushButton("Okay")
		self._ok_btn.setCursor(Qt.PointingHandCursor)
		self._ok_btn.setFixedHeight(40)
		self._ok_btn.setFont(inter(12, QFont.Medium))
		self._ok_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{WHITE};
				background:{TEAL_DARK};
				border:1px solid {TEAL_DARK};
				border-radius:12px;
				padding:0 18px;
			}}
			QPushButton:hover {{
				background:{TEAL};
				border-color:{TEAL};
			}}
			"""
		)
		self._ok_btn.clicked.connect(self.hide)

		lay.addWidget(badge_wrap)
		lay.addWidget(self._title_lbl)
		lay.addWidget(self._message_lbl)
		lay.addWidget(self._hint_lbl)
		lay.addSpacing(2)
		lay.addWidget(self._ok_btn, 0, Qt.AlignCenter)

	def open(self, customer_name="", schedule_date=None):
		if schedule_date and hasattr(schedule_date, "toString"):
			date_text = schedule_date.toString("MMMM d, yyyy")
			self._message_lbl.setText(
				f"{customer_name}'s delivery has been scheduled for {date_text}."
				if customer_name else
				f"The delivery has been scheduled for {date_text}."
			)
		else:
			self._message_lbl.setText(
				f"{customer_name}'s delivery has been scheduled successfully."
				if customer_name else
				"The delivery has been scheduled successfully."
			)

		if self.parent():
			self.setGeometry(self.parent().rect())
		self._center_card()
		self.show()
		self.raise_()
		self._ok_btn.setFocus()

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			event.accept()
			return
		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= self._header_drag_height:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active and self._drag_offset is not None:
			target = event.position().toPoint() - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			x = max(0, min(target.x(), max_x))
			y = max(0, min(target.y(), max_y))
			self._card.move(x, y)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self._drag_active = False
		self._drag_offset = None
		super().mouseReleaseEvent(event)

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._center_card()
		super().resizeEvent(event)

	def _center_card(self):
		x = max(0, (self.width() - self._card.width()) // 2)
		y = max(0, (self.height() - self._card.height()) // 2 - 14)
		self._card.move(x, y)


class DeliveryDetailsModal(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet(f"background:rgba(255,255,255,188);")
		self._drag_active = False
		self._drag_offset = None
		self._header_drag_height = 72
		self.hide()

		self._card = QFrame(self)
		self._card.setObjectName("detailsCard")
		self._card.setFixedWidth(700)
		self._card.setMinimumHeight(600)
		self._card.setStyleSheet(
			f"""
			QFrame#detailsCard {{
				background:{WHITE};
				border:1px solid #dde7e4;
				border-radius:12px;
			}}
			"""
		)
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(24)
		shadow.setOffset(0, 6)
		shadow.setColor(QColor(0, 0, 0, 32))
		self._card.setGraphicsEffect(shadow)

		lay = QVBoxLayout(self._card)
		lay.setContentsMargins(0, 0, 0, 0)
		lay.setSpacing(0)

		header = QWidget()
		header.setFixedHeight(72)
		header.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")
		h_lay = QHBoxLayout(header)
		h_lay.setContentsMargins(24, 16, 20, 14)

		title = QLabel("Delivery Details")
		title.setFont(playfair(16, QFont.DemiBold))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		close_btn = QPushButton("Close")
		close_btn.setCursor(Qt.PointingHandCursor)
		close_btn.setFont(inter(11, QFont.Medium))
		close_btn.setFixedHeight(30)
		close_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {TEAL_PALE2};border-radius:6px;padding:0 14px;
			}}
			QPushButton:hover {{ background:{WHITE}; border-color:{TEAL}; }}
			"""
		)
		close_btn.clicked.connect(self.hide)

		h_lay.addWidget(title)
		h_lay.addStretch()
		h_lay.addWidget(close_btn)
		lay.addWidget(header)

		body = QWidget()
		body.setStyleSheet(f"background:{WHITE};border:none;")
		self.body_lay = QVBoxLayout(body)
		self.body_lay.setContentsMargins(24, 25, 24, 12)
		self.body_lay.setSpacing(10)

		self.details_lbl = QLabel("DETAILS")
		self.details_lbl.setFixedHeight(10)
		self.details_lbl.setFont(inter(10, QFont.DemiBold))
		self.details_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.1px;background:transparent;border:none;")
		self.body_lay.addWidget(self.details_lbl)

		self.meta_lbl = QLabel("")
		self.meta_lbl.setMaximumHeight(130)
		self.meta_lbl.setFont(inter(11))
		self.meta_lbl.setTextFormat(Qt.RichText)
		self.meta_lbl.setWordWrap(True)
		self.meta_lbl.setStyleSheet(
			f"""
			QLabel {{
				color:{GRAY_5};background:transparent;
				border:none;
				padding:0;
			}}
			"""
		)
		self.body_lay.addWidget(self.meta_lbl)

		sep = QFrame()
		sep.setFrameShape(QFrame.HLine)
		sep.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin:6px 0 4px 0;")
		self.body_lay.addWidget(sep)

		orders_lbl = QLabel("LPG ORDERS")
		orders_lbl.setFixedHeight(10)
		orders_lbl.setFont(inter(10, QFont.DemiBold))
		orders_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:1.1px;background:transparent;border:none;")
		self.body_lay.addWidget(orders_lbl)

		self.items_scroll = QScrollArea()
		self.items_scroll.setWidgetResizable(True)
		self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.items_scroll.setStyleSheet(
			f"""
			QScrollArea {{ background:{WHITE}; border:none; }}
			QScrollBar:vertical {{ background:transparent; width:10px; margin:6px 2px 6px 0; }}
			QScrollBar::handle:vertical {{ background:rgba(26,122,110,0.26); min-height:26px; border-radius:5px; }}
			QScrollBar::handle:vertical:hover {{ background:rgba(26,122,110,0.40); }}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; border:none; background:transparent; }}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:transparent; }}
			"""
		)
		self.items_scroll.setMaximumHeight(900)
		self.items_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

		self.items_holder = QWidget()
		self.items_holder.setStyleSheet(f"background:{WHITE};border:none;")
		self.items_lay = QVBoxLayout(self.items_holder)
		self.items_lay.setContentsMargins(0, 0, 0, 0)
		self.items_lay.setSpacing(8)
		self.items_scroll.setWidget(self.items_holder)

		self.body_lay.addWidget(self.items_scroll)

		total_row = QFrame()
		total_row.setFixedHeight(60)
		total_row.setStyleSheet(f"background:{WHITE};border:none;border-top:1px solid {GRAY_2};")
		total_lay = QHBoxLayout(total_row)
		total_lay.setContentsMargins(0, 0, 0, 0)

		self.total_lbl = QLabel("Total: Php 0.00")
		self.total_lbl.setFont(inter(13, QFont.DemiBold))
		self.total_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
		total_lay.addStretch()
		total_lay.addWidget(self.total_lbl)
		self.body_lay.addWidget(total_row)

		lay.addWidget(body)

	def _clear_items_list(self):
		while self.items_lay.count():
			item = self.items_lay.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.setParent(None)
				widget.deleteLater()

	def _add_item_row(self, item):
		row = QWidget()
		row.setStyleSheet(f"background:{WHITE};border:none;")
		row_lay = QVBoxLayout(row)
		row_lay.setContentsMargins(0, 0, 0, 0)
		row_lay.setSpacing(2)

		top = QHBoxLayout()
		top.setContentsMargins(0, 0, 0, 0)
		top.setSpacing(8)

		product_lbl = QLabel(item["product_name"])
		product_lbl.setFont(inter(11, QFont.DemiBold))
		product_lbl.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

		amount_lbl = QLabel(f"Php {item['subtotal']:,.2f}")
		amount_lbl.setFont(inter(11, QFont.DemiBold))
		amount_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		top.addWidget(product_lbl)
		top.addStretch()
		top.addWidget(amount_lbl)
		row_lay.addLayout(top)

		bottom = QLabel(f"Qty: {item['quantity']}   Type: {item['type']}")
		bottom.setFont(inter(10))
		bottom.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
		row_lay.addWidget(bottom)

		sep = QFrame()
		sep.setFrameShape(QFrame.HLine)
		sep.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin:6px 0 0 0;")
		row_lay.addWidget(sep)

		self.items_lay.addWidget(row)

	def open(self, delivery):
		date_text = delivery["schedule_date"].toString("MMM d, yyyy")
		self.meta_lbl.setText(
			f"<div style='line-height:1.55;'>"
			f"<span style='color:{TEAL_DARK};font-weight:700;'>Customer:</span> "
			f"{delivery['customer_name']} ({delivery['contact']})<br>"
			f"<span style='color:{TEAL_DARK};font-weight:700;'>Schedule Date:</span> {date_text}<br>"
			f"<span style='color:{TEAL_DARK};font-weight:700;'>Status:</span> {delivery['status']}<br>"
			f"<span style='color:{TEAL_DARK};font-weight:700;'>Notes:</span> {delivery.get('notes') or '—'}"
			f"</div>"
		)

		self._clear_items_list()
		for item in delivery["items"]:
			self._add_item_row(item)

		self.total_lbl.setText(f"Total: Php {delivery['total_amount']:,.2f}")

		if self.parent():
			self.setGeometry(self.parent().rect())
		self._reflow_card()
		self.show()
		self.raise_()

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._reflow_card()
		super().resizeEvent(event)

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self.hide()
			return

		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= self._header_drag_height:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active and self._drag_offset is not None:
			target = event.position().toPoint() - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			x = max(0, min(target.x(), max_x))
			y = max(0, min(target.y(), max_y))
			self._card.move(x, y)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self._drag_active = False
		self._drag_offset = None
		super().mouseReleaseEvent(event)

	def _reflow_card(self):
		self._card.adjustSize()
		card_w = self._card.width()
		card_h = self._card.height()
		max_x = max(0, self.width() - card_w)
		max_y = max(0, self.height() - card_h)
		x = max(0, min((self.width() - card_w) // 2, max_x))
		y = max(0, min((self.height() - card_h) // 2, max_y))
		self._card.move(x, y)


class DeliveryActionDelegate(QStyledItemDelegate):
	def __init__(self, table, page):
		super().__init__(table)
		self._table = table
		self._page = page

	def paint(self, painter, option, index):
		painter.save()
		if option.state & QStyle.State_Selected:
			painter.fillRect(option.rect, QColor(TEAL_PALE))

		update_rect = option.rect.adjusted(10, 12, -10, -12)
		painter.setPen(QColor(AMBER))
		painter.setBrush(QColor(AMBER_BG))
		painter.drawRoundedRect(update_rect, 6, 6)
		painter.setFont(inter(9, QFont.Medium))
		painter.setPen(QColor(AMBER))
		painter.drawText(update_rect, Qt.AlignCenter, "Update")

		painter.restore()

	def sizeHint(self, option, index):
		return QSize(120, 60)

	def editorEvent(self, event, model, option, index):
		from PySide6.QtCore import QEvent

		if event.type() == QEvent.MouseButtonRelease:
			update_rect = option.rect.adjusted(10, 12, -10, -12)
			pos = event.position().toPoint()

			if update_rect.contains(pos):
				self._page.open_status(index.row())
				return True
		return False


class DeliveryView(QWidget):
	def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False, controller=None):
		super().__init__(parent)
		self._show_topbar = show_topbar
		self._topbar_controls_only = topbar_controls_only
		self._next_delivery_id = 100
		self._controller = controller

		load_fonts()
		self.setStyleSheet(f"background:{GRAY_1};")

		self._customers = []
		self._products = []
		self._deliveries = []

		self._build_ui()
		if self._controller:
			self._load_from_controller()
		self._init_modals()
		self._refresh_table()
		self._refresh_summary_cards()

	def _build_ui(self):
		root = QVBoxLayout(self)
		root.setContentsMargins(0, 0, 0, 0)
		root.setSpacing(0)

		if self._show_topbar:
			root.addWidget(self._build_topbar())

		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll.setStyleSheet(
			f"""
			QScrollArea {{ background:transparent;border:none; }}
			QScrollBar:vertical {{ background:transparent;width:11px;margin:8px 4px 8px 0; }}
			QScrollBar::handle:vertical {{
				background:rgba(26,122,110,0.30);
				min-height:34px;border-radius:5px;border:1px solid rgba(26,122,110,0.18);
			}}
			QScrollBar::handle:vertical:hover {{
				background:rgba(26,122,110,0.48);
				border:1px solid rgba(26,122,110,0.26);
			}}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0;border:none;background:transparent; }}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background:transparent; }}
			"""
		)

		content = QWidget()
		content.setStyleSheet("background:transparent;")
		c_lay = QVBoxLayout(content)
		c_lay.setContentsMargins(28, 24, 28, 28)
		c_lay.setSpacing(0)

		title_row = QHBoxLayout()
		title_row.setSpacing(0)

		left = QVBoxLayout()
		left.setSpacing(0)

		sub = QLabel("DELIVERY OPERATIONS")
		sub.setFont(inter(10, QFont.DemiBold))
		sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

		title = QLabel("Deliveries")
		title.setFont(playfair(28, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		page_sub = QLabel("Schedule, track, and update all LPG deliveries in one place.")
		page_sub.setFont(inter(12))
		page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

		left.addWidget(sub)
		left.addWidget(title)
		left.addWidget(page_sub)

		rule = QFrame()
		rule.setFrameShape(QFrame.HLine)
		rule.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin-bottom:6px;margin-left:24px;")

		self._new_btn = QPushButton("+ New Delivery")
		self._new_btn.setCursor(Qt.PointingHandCursor)
		self._new_btn.setFont(inter(12, QFont.Medium))
		self._new_btn.setFixedHeight(36)
		self._new_btn.setMinimumWidth(180)
		self._new_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{WHITE};background:{TEAL};
				border:1px solid {TEAL};border-radius:4px;padding:0 18px;
			}}
			QPushButton:hover {{ background:{TEAL_DARK};border-color:{TEAL_DARK}; }}
			"""
		)
		self._new_btn.clicked.connect(self._open_new_delivery)

		title_row.addLayout(left)
		title_row.addWidget(rule, 1, Qt.AlignBottom)
		title_row.addSpacing(10)
		title_row.addWidget(self._new_btn, 0, Qt.AlignRight | Qt.AlignTop)
		c_lay.addLayout(title_row)
		c_lay.addSpacing(20)

		stat_row = QHBoxLayout()
		stat_row.setSpacing(10)
		self._card_total_today = SummaryCard("TOTAL TODAY", TEAL)
		self._card_pending = SummaryCard("PENDING", TEAL_MID)
		self._card_in_transit = SummaryCard("IN TRANSIT", TEAL_LIGHT)
		self._card_delivered = SummaryCard("DELIVERED", GREEN)
		self._card_cancelled = SummaryCard("CANCELLED", RED)
		for card in [
			self._card_total_today,
			self._card_pending,
			self._card_in_transit,
			self._card_delivered,
			self._card_cancelled,
		]:
			stat_row.addWidget(card)
		c_lay.addLayout(stat_row)
		c_lay.addSpacing(16)

		filter_card = QFrame()
		filter_card.setStyleSheet("QFrame{background:transparent;border:none;}")
		filter_lay = QHBoxLayout(filter_card)
		filter_lay.setContentsMargins(0, 0, 0, 0)
		filter_lay.setSpacing(10)
		filter_icon_path = _qss_path(MODERN_CHEVRON_ICON)

		self._filter_date = QDateEdit()
		self._filter_date.setCalendarPopup(True)
		self._filter_date.setDate(QDate.currentDate())
		self._filter_date.setFont(inter(11))
		apply_modern_date_edit(self._filter_date, min_height=34, min_width=140)

		self._use_date_filter = QComboBox()
		self._use_date_filter.addItems(["All Dates", "Specific Date"])
		self._use_date_filter.setCurrentIndex(0)
		self._use_date_filter.setFont(inter(11))
		apply_modern_combo(self._use_date_filter, min_height=34, min_width=138)
		self._use_date_filter.setStyleSheet(
			f"""
			QComboBox {{
				color:{GRAY_5};
				background:transparent;
				border:1px solid #cfdad7;
				border-radius:8px;
				padding:0 30px 0 10px;
				min-height:34px;
				min-width:138px;
			}}
			QComboBox:hover {{ border-color:#b9d4cf; }}
			QComboBox:focus {{ border-color:{TEAL}; }}
			QComboBox::drop-down {{
				subcontrol-origin:padding;
				subcontrol-position:top right;
				width:26px;
				border:none;
				background:transparent;
			}}
			QComboBox::down-arrow {{
				image:url({filter_icon_path});
				width:12px;
				height:12px;
			}}
			QComboBox QAbstractItemView {{
				border:1px solid #cfe1dd;
				background:{WHITE};
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
				padding:4px;
				outline:none;
			}}
			"""
		)

		self._status_filter = QComboBox()
		self._status_filter.addItems(["All Statuses", "Pending", "In Transit", "Delivered", "Cancelled"])
		self._status_filter.setFont(inter(11))
		apply_modern_combo(self._status_filter, min_height=34, min_width=160)
		self._status_filter.setStyleSheet(
			f"""
			QComboBox {{
				color:{GRAY_5};
				background:transparent;
				border:1px solid #cfdad7;
				border-radius:8px;
				padding:0 30px 0 10px;
				min-height:34px;
				min-width:160px;
			}}
			QComboBox:hover {{ border-color:#b9d4cf; }}
			QComboBox:focus {{ border-color:{TEAL}; }}
			QComboBox::drop-down {{
				subcontrol-origin:padding;
				subcontrol-position:top right;
				width:26px;
				border:none;
				background:transparent;
			}}
			QComboBox::down-arrow {{
				image:url({filter_icon_path});
				width:12px;
				height:12px;
			}}
			QComboBox QAbstractItemView {{
				border:1px solid #cfe1dd;
				background:{WHITE};
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
				padding:4px;
				outline:none;
			}}
			"""
		)

		self._customer_filter = QLineEdit()
		self._customer_filter.setPlaceholderText("Filter customer name or contact...")
		self._customer_filter.setFont(inter(11))
		self._customer_filter.setStyleSheet(
			f"""
			QLineEdit {{
				color:{GRAY_5};background:transparent;
				border:1px solid #cfdad7;border-radius:8px;
				padding:0 10px;min-height:34px;min-width:260px;
			}}
			QLineEdit:hover {{ border-color:#b9d4cf; }}
			QLineEdit:focus {{ border-color:{TEAL}; }}
			"""
		)

		clear_btn = QPushButton("Clear Filters")
		clear_btn.setCursor(Qt.PointingHandCursor)
		clear_btn.setFont(inter(11, QFont.Medium))
		clear_btn.setFixedHeight(34)
		clear_btn.setStyleSheet(
			f"""
			QPushButton {{
				color:{GRAY_5};background:transparent;
				border:1px solid #cfdad7;border-radius:8px;padding:0 14px;
			}}
			QPushButton:hover {{ background:rgba(26,122,110,0.06);border-color:#b9d4cf; }}
			"""
		)
		clear_btn.clicked.connect(self._clear_filters)

		filter_lay.addWidget(self._use_date_filter)
		filter_lay.addWidget(self._filter_date)
		filter_lay.addWidget(self._status_filter)
		filter_lay.addWidget(self._customer_filter, 1)
		filter_lay.addWidget(clear_btn)
		c_lay.addWidget(filter_card)
		c_lay.addSpacing(14)

		table_card = QFrame()
		table_card.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")
		t_lay = QVBoxLayout(table_card)
		t_lay.setContentsMargins(0, 0, 0, 0)
		t_lay.setSpacing(0)

		bar = QWidget()
		bar.setFixedHeight(52)
		bar.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
		bar_lay = QHBoxLayout(bar)
		bar_lay.setContentsMargins(18, 0, 18, 0)

		table_title = QLabel("All Deliveries")
		table_title.setFont(playfair(14, QFont.Medium))
		table_title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		self._count_lbl = QLabel("0 records")
		self._count_lbl.setFont(inter(11))
		self._count_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		bar_lay.addWidget(table_title)
		bar_lay.addStretch()
		bar_lay.addWidget(self._count_lbl)
		t_lay.addWidget(bar)

		self._model = QStandardItemModel()
		self._model.setHorizontalHeaderLabels(
			["Customer", "Schedule Date", "Items", "Total Amount", "Status", "Actions"]
		)

		self._proxy = DeliveryFilterProxy(self)
		self._proxy.setSourceModel(self._model)

		self._table = QTableView()
		self._table.setModel(self._proxy)
		self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self._table.setFocusPolicy(Qt.NoFocus)
		self._table.setShowGrid(False)
		self._table.verticalHeader().setVisible(False)
		self._table.verticalHeader().setDefaultSectionSize(58)
		self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
		self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
		self._table.setStyleSheet(
			f"""
			QTableView {{
				background:transparent;border:none;
				font-family:'{INTER_FAMILY}';font-size:12px;color:{GRAY_5};outline:none;
				selection-background-color:{TEAL_PALE};
			}}
			QTableView::item {{ padding:10px 12px;border-bottom:0.5px solid {GRAY_2}; }}
			QTableView::item:selected {{ background:{TEAL_PALE};color:{TEAL_DARK}; }}
			QHeaderView::section {{
				background:{WHITE};color:{GRAY_4};
				font-size:10px;font-weight:600;letter-spacing:1.3px;
				padding:10px 12px 8px;border:none;border-bottom:1px solid {GRAY_2};
				font-family:'{INTER_FAMILY}';
			}}
			"""
		)
		self._table.setItemDelegateForColumn(5, DeliveryActionDelegate(self._table, self))
		self._table.doubleClicked.connect(lambda index: self.open_details(index.row()))

		self._empty = QWidget()
		self._empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		e_lay = QVBoxLayout(self._empty)
		e_lay.setContentsMargins(0, 0, 0, 0)
		e_lay.setSpacing(6)
		e_lay.addStretch()
		e_title = QLabel("No deliveries found")
		e_title.setFont(playfair(16, QFont.Medium))
		e_title.setAlignment(Qt.AlignCenter)
		e_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
		e_sub = QLabel("Adjust filters or click \"+ New Delivery\" to create one.")
		e_sub.setFont(inter(12))
		e_sub.setAlignment(Qt.AlignCenter)
		e_sub.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")
		e_lay.addWidget(e_title)
		e_lay.addWidget(e_sub)
		e_lay.addStretch()

		self._table_stack = QStackedWidget()
		self._table_stack.addWidget(self._table)
		self._table_stack.addWidget(self._empty)
		t_lay.addWidget(self._table_stack)
		c_lay.addWidget(table_card)

		scroll.setWidget(content)
		root.addWidget(scroll)

		self._use_date_filter.currentTextChanged.connect(self._apply_filters)
		self._filter_date.dateChanged.connect(self._apply_filters)
		self._status_filter.currentTextChanged.connect(self._apply_filters)
		self._customer_filter.textChanged.connect(self._apply_filters)

		self._apply_filters()

	def bind_controller(self, controller):
		self._controller = controller
		self.reload_data()
		return controller

	def showEvent(self, event):
		super().showEvent(event)
		if self._controller:
			self.reload_data()

	def reload_data(self):
		if not self._controller:
			return
		self._load_from_controller()
		self._refresh_table()
		self._refresh_summary_cards()

	def _build_topbar(self):
		bar = QWidget()
		bar.setFixedHeight(84)
		bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")

		lay = QHBoxLayout(bar)
		lay.setContentsMargins(28, 8, 28, 8)

		if self._topbar_controls_only:
			left_spacer = QWidget()
			left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
			left_spacer.setStyleSheet("background:transparent;border:none;")
			lay.addWidget(left_spacer)
		else:
			breadcrumb = QLabel("DELIVERY MANAGEMENT")
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
		self._clock_lbl.setMinimumHeight(30)
		self._clock_lbl.setAlignment(Qt.AlignRight)
		self._clock_lbl.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:1px;background:transparent;border:none;")

		self._date_lbl = QLabel("")
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
		notif.setStyleSheet(
			f"""
			QPushButton {{
				color:{GRAY_4};background:{WHITE};
				border:1px solid {GRAY_2};border-radius:6px;font-size:14px;
			}}
			QPushButton:hover {{ background:{GRAY_1}; }}
			"""
		)
		lay.addWidget(notif)

		self._timer = QTimer(self)
		self._timer.timeout.connect(self._tick)
		self._timer.start(1000)
		self._tick()
		return bar

	def _tick(self):
		self._clock_lbl.setText(QTime.currentTime().toString("hh:mm:ss"))
		self._date_lbl.setText(QDate.currentDate().toString("dddd, MMMM d, yyyy"))

	def _find_customer(self, customer_id):
		for c in self._customers:
			if c["id"] == customer_id:
				return c
		return {"id": customer_id, "name": "Unknown", "contact": ""}

	def _find_product(self, product_id):
		for p in self._products:
			if p["id"] == product_id:
				return p
		return {"id": product_id, "name": "Unknown", "refill_price": 0.0, "new_tank_price": 0.0}

	def _to_qdate(self, dt_obj_or_str):
		if isinstance(dt_obj_or_str, datetime.date):
			return QDate(dt_obj_or_str.year, dt_obj_or_str.month, dt_obj_or_str.day)
		try:
			return QDate.fromString(str(dt_obj_or_str), "yyyy-MM-dd")
		except Exception:
			return QDate.currentDate()

	def _qdate_to_pydate(self, qdate):
		"""Convert a QDate to a python datetime.date safely."""
		if hasattr(qdate, "toPython"):
			return qdate.toPython()
		return datetime.date(qdate.year(), qdate.month(), qdate.day())

	def _load_from_controller(self):
		if not self._controller:
			return

		# Customers
		ok, cust_res = self._controller.list_customers()
		if ok and cust_res is not None:
			self._customers = list(cust_res)
		# Products
		ok, prod_res = self._controller.list_products()
		if ok and prod_res is not None:
			self._products = list(prod_res)
		if hasattr(self, "_new_modal"):
			self._new_modal.set_options(self._customers, self._products)

		# Deliveries
		ok, res = self._controller.list_deliveries()
		if not ok:
			QMessageBox.warning(self, "Load Failed", str(res))
			return

		self._deliveries = []
		for row in res or []:
			qdate = self._to_qdate(row.get("schedule_date"))
			status = display_status(row.get("status", ""))
			# Fetch items for preview/total
			items_ok, items_res = self._controller.get_items(row.get("id"))
			items_list = items_res if (items_ok and items_res) else []
			item_rows = []
			total_amt = 0.0
			for it in items_list:
				item_rows.append(
					{
						"product_id": it.get("product_id"),
						"product_name": it.get("product_name", ""),
						"quantity": it.get("quantity", 0),
						"type": display_item_type(it.get("type", "")),
						"unit_price": float(it.get("unit_price", 0) or 0),
						"subtotal": float(it.get("subtotal", 0) or 0),
					}
				)
				try:
					total_amt += float(it.get("subtotal", 0) or 0)
				except Exception:
					pass

			record = {
				"id": row.get("id"),
				"customer_id": row.get("customer_id"),
				"customer_name": row.get("customer_name", ""),
				"contact": row.get("contact", ""),
				"schedule_date": qdate,
				"items": item_rows,
				"notes": row.get("notes", ""),
				"status": status,
				"total_amount": float(row.get("total_amount", total_amt) or total_amt or 0),
			}
			self._deliveries.append(record)

	def _init_modals(self):
		self._new_modal = NewDeliveryModal(self._customers, self._products, self)
		self._status_modal = DeliveryStatusModal(self)
		self._saved_modal = DeliverySavedModal(self)
		self._details_modal = DeliveryDetailsModal(self)

	def _build_items_with_prices(self, items_payload):
		item_rows = []
		total = 0.0
		for row in items_payload:
			product = self._find_product(row["product_id"])
			is_refill = row["type"] == "Refill"
			unit_price = product["refill_price"] if product and is_refill else product["new_tank_price"] if product else 0.0
			try:
				unit_price = float(unit_price)
			except Exception:
				unit_price = 0.0
			subtotal = unit_price * row["quantity"]
			total += subtotal
			item_rows.append(
				{
					"product_id": product["id"] if product else row.get("product_id"),
					"product_name": product["name"] if product else "",
					"quantity": row["quantity"],
					"type": row["type"],
					"unit_price": unit_price,
					"subtotal": subtotal,
				}
			)
		return item_rows, total

	def _add_delivery_record(self, payload):
		customer = self._find_customer(payload["customer_id"])
		item_rows, total = self._build_items_with_prices(payload["items"])

		record = {
			"id": self._next_delivery_id,
			"customer_id": customer["id"],
			"customer_name": customer["name"],
			"contact": customer["contact"],
			"schedule_date": payload["schedule_date"],
			"items": item_rows,
			"notes": payload.get("notes", ""),
			"status": payload.get("status", "Pending"),
			"total_amount": total,
		}
		self._next_delivery_id += 1
		self._deliveries.append(record)

	def _refresh_table(self):
		self._model.setRowCount(0)
		sorted_rows = sorted(self._deliveries, key=lambda r: r["schedule_date"].toJulianDay(), reverse=True)
		for row in sorted_rows:
			items_preview = ", ".join(
				[f"{i['product_name']} x{i['quantity']} ({i['type']})" for i in row["items"]]
			)
			if len(items_preview) > 86:
				items_preview = items_preview[:83] + "..."

			customer_text = row["customer_name"]
			date_text = row["schedule_date"].toString("MMM d, yyyy")
			total_text = f"Php {row['total_amount']:,.2f}"

			cells = [
				QStandardItem(customer_text),
				QStandardItem(date_text),
				QStandardItem(items_preview),
				QStandardItem(total_text),
				QStandardItem(row["status"]),
				QStandardItem(""),
			]

			cells[0].setData(row["id"], Qt.UserRole)
			cells[0].setData(row["contact"], Qt.UserRole + 1)
			cells[1].setData(row["schedule_date"], Qt.UserRole + 2)

			for idx, c in enumerate(cells):
				c.setFont(inter(11))
				if idx == 4:
					c.setForeground(QColor(self._status_fg(row["status"])))
				elif idx == 0:
					c.setForeground(QColor(TEAL_DARK))
				else:
					c.setForeground(QColor(GRAY_5))

			self._model.appendRow(cells)

		self._apply_filters()

	def _status_fg(self, status):
		return {
			"Pending": AMBER,
			"In Transit": TEAL_DARK,
			"Delivered": GREEN,
			"Cancelled": RED,
		}.get(status, GRAY_5)

	def _refresh_summary_cards(self):
		today = QDate.currentDate()
		total_today = sum(1 for d in self._deliveries if d["schedule_date"] == today)
		pending = sum(1 for d in self._deliveries if d["status"] == "Pending")
		in_transit = sum(1 for d in self._deliveries if d["status"] == "In Transit")
		delivered = sum(1 for d in self._deliveries if d["status"] == "Delivered")
		cancelled = sum(1 for d in self._deliveries if d["status"] == "Cancelled")

		self._card_total_today.set_value(total_today)
		self._card_pending.set_value(pending)
		self._card_in_transit.set_value(in_transit)
		self._card_delivered.set_value(delivered)
		self._card_cancelled.set_value(cancelled)

	def _apply_filters(self):
		self._proxy.set_status(self._status_filter.currentText())
		self._proxy.set_customer_text(self._customer_filter.text())
		if self._use_date_filter.currentText() == "Specific Date":
			self._proxy.set_date_filter(self._filter_date.date())
		else:
			self._proxy.set_date_filter(None)

		count = self._proxy.rowCount()
		self._count_lbl.setText(f"{count} record{'s' if count != 1 else ''}")
		self._table_stack.setCurrentWidget(self._table if count > 0 else self._empty)

	def _clear_filters(self):
		self._use_date_filter.setCurrentText("All Dates")
		self._filter_date.setDate(QDate.currentDate())
		self._status_filter.setCurrentText("All Statuses")
		self._customer_filter.clear()
		self._apply_filters()

	def _open_new_delivery(self):
		# Rebuild modal options in case data changed.
		self._new_modal._customers = self._customers
		self._new_modal._products = self._products
		self._new_modal.open(self._save_new_delivery)

	def _save_new_delivery(self, payload):
		# Prepare data for the controller/model
		items_with_prices, _ = self._build_items_with_prices(payload["items"])
		schedule_date = self._qdate_to_pydate(payload["schedule_date"])
		customer_id = payload["customer_id"]
		notes = payload.get("notes", "")
		current_user = LoginController.get_current_user()
		user_id = current_user.get("id") if current_user else 0

		ok, res = self._controller.create_delivery(
			customer_id=customer_id,
			user_id=user_id,
			schedule_date=schedule_date,
			notes=notes,
			items=items_with_prices,
		)

		if not ok:
			QMessageBox.warning(self, "Save Failed", str(res))
			return

		# Reload data from DB to keep UI in sync with persisted records
		self._load_from_controller()
		self._refresh_table()
		self._refresh_summary_cards()
		customer = self._find_customer(customer_id)
		customer_name = customer["name"] if customer else ""
		self._saved_modal.open(customer_name, payload["schedule_date"])

	def _delivery_from_proxy_row(self, proxy_row):
		idx = self._proxy.index(proxy_row, 0)
		src_idx = self._proxy.mapToSource(idx)
		if not src_idx.isValid():
			return None
		delivery_id = self._model.item(src_idx.row(), 0).data(Qt.UserRole)
		for d in self._deliveries:
			if d["id"] == delivery_id:
				return d
		return None

	def open_details(self, proxy_row):
		delivery = self._delivery_from_proxy_row(proxy_row)
		if delivery is None:
			return
		self._details_modal.open(delivery)

	def open_status(self, proxy_row):
		delivery = self._delivery_from_proxy_row(proxy_row)
		if delivery is None:
			return
		self._status_modal.open(delivery, self._save_status)

	def _save_status(self, delivery_id, new_status):
		user = LoginController.get_current_user()
		user_id = user.get("id") if user else 0

		if self._controller:
			ok, err = self._controller.update_status(delivery_id, db_status(new_status), user_id)
			if not ok:
				QMessageBox.warning(self, "Update Failed", str(err))
				return
			# Reload fresh data from DB to ensure totals/items reflect changes and triggers.
			self._load_from_controller()
		else:
			for d in self._deliveries:
				if d["id"] == delivery_id:
					d["status"] = new_status
					break

		self._refresh_table()
		self._refresh_summary_cards()


class DeliveryDashboardWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		load_fonts()
		self.setWindowTitle("G and C LPG Trading - Delivery Management")
		self._build_ui()
		self.showFullScreen()

	def _build_ui(self):
		central = QWidget()
		central.setStyleSheet(f"background:{GRAY_1};")
		self.setCentralWidget(central)

		root = QHBoxLayout(central)
		root.setContentsMargins(0, 0, 0, 0)
		root.setSpacing(0)

		root.addWidget(self._build_sidebar())

		main_col = QWidget()
		main_lay = QVBoxLayout(main_col)
		main_lay.setContentsMargins(0, 0, 0, 0)
		main_lay.setSpacing(0)

		self._page = DeliveryView(show_topbar=True, topbar_controls_only=False, controller=DeliveryController())
		main_lay.addWidget(self._page)

		root.addWidget(main_col)
		self._transaction_window = None

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
		logo.setStyleSheet("background:transparent;border:none;border-bottom:1px solid rgba(255,255,255,0.1);")
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

		profile = QWidget()
		profile.setFixedHeight(64)
		profile.setStyleSheet("background:transparent;border:none;border-bottom:1px solid rgba(255,255,255,0.1);")
		p_lay = QHBoxLayout(profile)
		p_lay.setContentsMargins(18, 10, 14, 8)
		p_lay.setSpacing(10)

		avatar = QLabel("")
		avatar.setFixedSize(36, 36)
		avatar.setAlignment(Qt.AlignCenter)
		avatar.setFont(inter(13, QFont.DemiBold))
		avatar.setStyleSheet(f"background:{TEAL};color:white;border-radius:18px;border:none;")

		info = QVBoxLayout()
		info.setContentsMargins(0, 0, 0, 0)
		info.setSpacing(0)
		nm = QLabel("")
		nm.setFont(inter(12, QFont.Medium))
		nm.setStyleSheet("color:#fff;background:transparent;border:none;")
		role = QLabel("Administrator")
		role.setFont(inter(10))
		role.setStyleSheet("color:rgba(255,255,255,0.5);background:transparent;border:none;")
		info.addWidget(nm)
		info.addWidget(role)

		p_lay.addWidget(avatar)
		p_lay.addLayout(info)
		p_lay.addStretch()
		lay.addWidget(profile)

		nav = QScrollArea()
		nav.setWidgetResizable(True)
		nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		nav.setStyleSheet("background:transparent;border:none;")

		nav_w = QWidget()
		nav_w.setStyleSheet("background:transparent;")
		nav_lay = QVBoxLayout(nav_w)
		nav_lay.setContentsMargins(0, 0, 0, 0)
		nav_lay.setSpacing(0)

		nav_lay.addWidget(self._section("Main"))
		nav_lay.addWidget(self._nav_item("Dashboard", active=False))
		nav_lay.addWidget(self._nav_item("Deliveries", active=True))
		nav_lay.addWidget(self._nav_item("Customers", active=False))

		nav_lay.addWidget(self._section("Management"))
		nav_lay.addWidget(self._nav_item("LPG Products", active=False))
		self.btn_transactions = self._nav_item("Transactions", active=False)
		self.btn_transactions.mousePressEvent = self._open_transactions
		nav_lay.addWidget(self.btn_transactions)

		nav_lay.addWidget(self._section("Records"))
		nav_lay.addWidget(self._nav_item("Delivery Logs", active=False))
		nav_lay.addWidget(self._nav_item("Audit Logs", active=False))
		nav_lay.addStretch()

		nav.setWidget(nav_w)
		lay.addWidget(nav)

		footer = QWidget()
		footer.setStyleSheet("background:transparent;border:none;border-top:1px solid rgba(255,255,255,0.1);")
		f_lay = QHBoxLayout(footer)
		f_lay.setContentsMargins(18, 14, 18, 14)
		f_lay.setSpacing(8)

		signout = QLabel("Sign Out")
		signout.setFont(inter(10))
		signout.setStyleSheet("color:rgba(255,255,255,0.4);background:transparent;border:none;")
		f_lay.addWidget(signout)
		f_lay.addStretch()
		lay.addWidget(footer)
		return sb

	def _section(self, text):
		w = QWidget()
		lay = QVBoxLayout(w)
		lay.setContentsMargins(18, 18, 18, 8)
		lbl = QLabel(text.upper())
		lbl.setFont(inter(9, QFont.Medium))
		lbl.setStyleSheet("color:rgba(255,255,255,0.28);letter-spacing:2px;background:transparent;border:none;")
		lay.addWidget(lbl)
		return w

	def _nav_item(self, text, active=False):
		w = NavItemWidget(active=active)
		row = QHBoxLayout(w)
		row.setContentsMargins(0, 0, 18, 0)
		row.setSpacing(10)
		row.addSpacing(16)

		icon = QLabel("•")
		icon.setFixedSize(30, 20)
		icon.setAlignment(Qt.AlignCenter)
		icon.setStyleSheet("color:rgba(255,255,255,0.7);background:transparent;border:none;")

		lbl = QLabel(text)
		lbl.setFont(inter(10, QFont.Medium if active else QFont.Normal))
		lbl.setStyleSheet("color:#fff;background:transparent;border:none;" if active else "color:rgba(255,255,255,0.55);background:transparent;border:none;")

		row.addWidget(icon)
		row.addWidget(lbl)
		row.addStretch()
		return w

	def _open_transactions(self, event=None):
		from controllers.admin_transaction_controller import AdminTransactionController
		from views.admin_transaction_view import TransactionView

		controller = AdminTransactionController()
		self._transaction_window = TransactionView(show_topbar=True, controller=controller)
		self._transaction_window.showFullScreen()
		self.close()


def main():
	app = QApplication(sys.argv)
	load_fonts()
	app.setFont(inter(11))

	win = DeliveryDashboardWindow()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
