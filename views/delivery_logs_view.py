import os
import sys

from PySide6.QtCore import Qt, QTimer, QDate, QTime
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QColor, QTextCharFormat, QPixmap
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


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from views.admin_dashboard_view import owner_scrollbar_qss

BASE_DIR = PROJECT_ROOT
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
MODERN_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_modern.svg")
WHITE_CHEVRON_ICON = os.path.join(BASE_DIR, "assets", "chevron_down_white.svg")
NO_DELIVERY_LOGS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

TEAL = "#1A7A6E"
TEAL_DARK = "#145F55"
TEAL_PALE = "#e8f5f3"
WHITE = "#ffffff"
GRAY_1 = "#f4f5f4"
GRAY_2 = "#e6eae9"
GRAY_3 = "#c4ccc9"
GRAY_4 = "#7a8a87"
GRAY_5 = "#3a4a47"

PLAYFAIR_FAMILY = "Playfair Display"
INTER_FAMILY = "Inter"
CALENDAR_MONTH_YEAR_FONT_FAMILY = INTER_FAMILY
CALENDAR_MONTH_YEAR_FONT_SIZE = 14
CALENDAR_MONTH_YEAR_FONT_WEIGHT_CSS = 600
CALENDAR_MONTH_YEAR_FONT_WEIGHT_QT = QFont.DemiBold


def load_fonts():
	global PLAYFAIR_FAMILY, INTER_FAMILY, CALENDAR_MONTH_YEAR_FONT_FAMILY
	fonts = [
		"PlayfairDisplay-Medium.ttf",
		"PlayfairDisplay-SemiBold.ttf",
		"Inter_18pt-Regular.ttf",
		"Inter_18pt-Medium.ttf",
		"Inter_18pt-SemiBold.ttf",
		"Inter_24pt-Bold.ttf",
	]
	inter_family_set = False
	for font_file in fonts:
		path = os.path.join(FONTS_DIR, font_file)
		if os.path.exists(path):
			font_id = QFontDatabase.addApplicationFont(path)
			if font_id != -1:
				families = QFontDatabase.applicationFontFamilies(font_id)
				if families:
					if font_file.startswith("PlayfairDisplay"):
						PLAYFAIR_FAMILY = families[0]
					elif font_file.startswith("Inter") and not inter_family_set:
						INTER_FAMILY = families[0]
						inter_family_set = True

	if not inter_family_set:
		for family_name in QFontDatabase().families():
			if family_name.lower().startswith("inter"):
				INTER_FAMILY = family_name
				inter_family_set = True
				break

	# Keep month/year selectors in sync with the resolved Inter family.
	CALENDAR_MONTH_YEAR_FONT_FAMILY = INTER_FAMILY


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


def _combo_box_style(min_height=34, min_width=None):
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
		font-family:'{CALENDAR_MONTH_YEAR_FONT_FAMILY}';
		font-size:{CALENDAR_MONTH_YEAR_FONT_SIZE}px;
		font-weight:{CALENDAR_MONTH_YEAR_FONT_WEIGHT_CSS};
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
	QCalendarWidget QWidget#qt_calendar_calendarview {{
		outline:none;
		border:none;
	}}
	QCalendarWidget QHeaderView::section {{
		background:{WHITE};
		color:{TEAL};
		border:none;
		padding:6px 0;
		font-family:'{INTER_FAMILY}';
		font-size:10px;
		font-weight:600;
	}}
	QCalendarWidget QAbstractItemView {{
		color:#000000;
		background:{WHITE};
		selection-background-color:{TEAL_PALE};
		selection-color:{TEAL_DARK};
		outline:none;
		font-family:'{INTER_FAMILY}';
		font-size:12px;
		font-weight:600;
	}}
	QCalendarWidget QAbstractItemView:item {{
		background:transparent;
		border:none;
		padding:2px;
		margin:0px;
	}}
	QCalendarWidget QAbstractItemView:item:hover {{
		background:rgba(26,122,110,0.06);
		border:none;
		color:#000000;
	}}
	QCalendarWidget QAbstractItemView:item:selected {{
		background:{TEAL_PALE};
		border:1px solid {TEAL};
		border-radius:6px;
		color:#000000;
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


class DeliveryLogDetailsDialog(QDialog):
	def __init__(self, log_item, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Delivery Details")
		self.setModal(True)
		self.setMinimumWidth(520)
		self.setStyleSheet(
			f"""
			QDialog {{ background:{WHITE}; }}
			QLabel {{ color:{GRAY_5}; background:transparent; border:none; }}
			QFrame#Card {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:8px;
			}}
			"""
		)

		root = QVBoxLayout(self)
		root.setContentsMargins(18, 18, 18, 14)
		root.setSpacing(12)

		title = QLabel("Delivery Log Details")
		title.setFont(playfair(18, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};")
		root.addWidget(title)

		subtitle = QLabel("Read-only delivery information from the selected status-change entry.")
		subtitle.setFont(inter(11))
		subtitle.setStyleSheet(f"color:{GRAY_4};")
		root.addWidget(subtitle)

		card = QFrame()
		card.setObjectName("Card")
		card_lay = QVBoxLayout(card)
		card_lay.setContentsMargins(14, 14, 14, 14)
		card_lay.setSpacing(8)

		detail_rows = [
			("Delivery ID", log_item.get("delivery_id", "")),
			("Customer name", log_item.get("customer_name", "")),
			("Old status", self._status_value(log_item.get("old_status", ""))),
			("New status", self._status_value(log_item.get("new_status", ""))),
			("Changed by", log_item.get("changed_by", "")),
			("Date and time", log_item.get("changed_at", "")),
			("Address", log_item.get("address", "")),
			("Scheduled date", log_item.get("scheduled_date", "")),
			("Products", log_item.get("products", "")),
			("Notes", log_item.get("notes", "")),
		]

		for label_text, value_text in detail_rows:
			row = QLabel(f"{label_text}: {value_text}")
			row.setFont(inter(11))
			row.setWordWrap(True)
			card_lay.addWidget(row)

		root.addWidget(card)

		buttons = QDialogButtonBox(QDialogButtonBox.Close)
		close_btn = buttons.button(QDialogButtonBox.Close)
		close_btn.setText("Close")
		close_btn.setStyleSheet(
			f"QPushButton{{background:{WHITE};border:1px solid {GRAY_2};color:{GRAY_5};padding:6px 14px;border-radius:5px;}}"
		)
		buttons.rejected.connect(self.reject)
		buttons.accepted.connect(self.accept)
		root.addWidget(buttons)

	@staticmethod
	def _status_value(value, fallback="-"):
		text = str(value or "").strip()
		return text or fallback


class DeliveryLogsView(QWidget):
	def __init__(self, parent=None, show_topbar=True, controller=None):
		super().__init__(parent)
		self._show_topbar = show_topbar
		self._all_logs = []
		self._filtered_logs = []
		self._controller = None

		load_fonts()
		self.setStyleSheet(f"background:{GRAY_1};")
		self._build_ui()
		self._populate_status_type_filter()
		self._render_table()
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
		scroll.setStyleSheet(owner_scrollbar_qss())

		content = QWidget()
		content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		content_lay = QVBoxLayout(content)
		content_lay.setContentsMargins(28, 24, 28, 28)
		content_lay.setSpacing(14)

		top = QVBoxLayout()
		top.setSpacing(2)

		sub = QLabel("READ-ONLY STATUS CHANGE HISTORY")
		sub.setFont(inter(10, QFont.DemiBold))
		sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;")

		title = QLabel("Delivery Logs")
		title.setFont(playfair(28, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};")

		desc = QLabel("Review delivery status changes without editing records.")
		desc.setFont(inter(12))
		desc.setStyleSheet(f"color:{GRAY_4};")

		top.addWidget(sub)
		top.addWidget(title)
		top.addWidget(desc)
		content_lay.addLayout(top)

		filter_row = QHBoxLayout()
		filter_row.setSpacing(10)

		self._filter_delivery_id = QLineEdit()
		self._filter_delivery_id.setPlaceholderText("Filter by Delivery ID")
		self._filter_delivery_id.setFont(inter(11))
		self._filter_delivery_id.setFixedHeight(34)
		self._filter_delivery_id.setMinimumWidth(180)
		self._filter_delivery_id.textChanged.connect(self._apply_filters)

		self._filter_status_type = QComboBox()
		self._filter_status_type.setFont(inter(11))
		self._filter_status_type.setFixedHeight(34)
		self._filter_status_type.setMinimumWidth(220)
		self._filter_status_type.setMaximumWidth(280)
		self._filter_status_type.currentIndexChanged.connect(self._apply_filters)

		self._date_from = QDateEdit()
		self._date_from.setCalendarPopup(True)
		self._date_from.setDisplayFormat("MMM d, yyyy")
		today = QDate.currentDate()
		first_of_month = QDate(today.year(), today.month(), 1)
		self._date_from.setDate(first_of_month)
		self._date_from.setFont(inter(11))
		self._date_from.setFixedHeight(34)
		self._date_from.setMinimumWidth(170)
		self._date_from.setMaximumWidth(170)
		self._date_from.dateChanged.connect(self._on_date_from_changed)

		self._date_to = QDateEdit()
		self._date_to.setCalendarPopup(True)
		self._date_to.setDisplayFormat("MMM d, yyyy")
		self._date_to.setDate(today)
		self._date_to.setFont(inter(11))
		self._date_to.setFixedHeight(34)
		self._date_to.setMinimumWidth(170)
		self._date_to.setMaximumWidth(170)
		self._date_to.dateChanged.connect(self._on_date_to_changed)

		from_lbl = QLabel("From")
		from_lbl.setFont(inter(10, QFont.Medium))
		from_lbl.setStyleSheet(f"color:{GRAY_4};")

		to_lbl = QLabel("To")
		to_lbl.setFont(inter(10, QFont.Medium))
		to_lbl.setStyleSheet(f"color:{GRAY_4};")

		self._filter_delivery_id.setStyleSheet(
			f"""
			QLineEdit {{
				color:{GRAY_5};
				background:#fbfcfc;
				border:1px solid #d6e2df;
				border-radius:8px;
				padding:0 12px;
			}}
			QLineEdit:hover {{
				border-color:#b9d4cf;
				background:{WHITE};
			}}
			QLineEdit:focus {{
				border-color:{TEAL};
				background:{WHITE};
			}}
			"""
		)
		self._filter_status_type.setStyleSheet(_combo_box_style(min_width=220))
		self._configure_date_edit(self._date_from, min_width=170)
		self._configure_date_edit(self._date_to, min_width=170)

		filter_row.addWidget(self._filter_delivery_id)
		filter_row.addWidget(self._filter_status_type)
		filter_row.addWidget(from_lbl)
		filter_row.addWidget(self._date_from)
		filter_row.addWidget(to_lbl)
		filter_row.addWidget(self._date_to)
		filter_row.addStretch()
		content_lay.addLayout(filter_row)

		self._table = QTableWidget(0, 6)
		self._table.setHorizontalHeaderLabels([
			"DELIVERY ID",
			"CUSTOMER NAME",
			"OLD STATUS",
			"NEW STATUS",
			"CHANGED BY",
			"DATE AND TIME OF CHANGE",
		])
		self._table.verticalHeader().setVisible(False)
		self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self._table.setSelectionMode(QAbstractItemView.SingleSelection)
		self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self._table.setFocusPolicy(Qt.NoFocus)
		self._table.setWordWrap(False)
		self._table.setShowGrid(False)
		self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self._table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self._table.setStyleSheet(
			f"""
			QTableWidget {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:8px;
				gridline-color:transparent;
				selection-background-color:{TEAL_PALE};
				selection-color:{TEAL_DARK};
			}}
			QHeaderView::section {{
				background:#f7f8f8;
				color:{GRAY_4};
				border:none;
				border-bottom:1px solid {GRAY_2};
				padding:10px 8px;
				font-family:'{INTER_FAMILY}';
				font-size:12px;
				font-weight:600;
				letter-spacing:1px;
			}}
			QTableWidget::item {{
				padding:6px 8px;
				border:none;
				border-bottom:1px solid #f3f5f4;
				color:{GRAY_5};
			}}
			QTableWidget::item:selected {{
				background:{TEAL_PALE};
				color:{TEAL_DARK};
				border-bottom:1px solid #f3f5f4;
			}}
			"""
		)
		self._table.setStyleSheet(self._table.styleSheet() + owner_scrollbar_qss())
		self._table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
		self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
		self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
		self._table.setColumnWidth(5, 280)
		self._table.horizontalHeader().setFixedHeight(55)
		self._table.cellDoubleClicked.connect(self._on_row_clicked)

		self._empty = QWidget()
		empty_lay = QVBoxLayout(self._empty)
		empty_lay.setContentsMargins(0, 36, 0, 36)
		empty_lay.setAlignment(Qt.AlignCenter)

		empty_image = QLabel()
		empty_image.setAlignment(Qt.AlignCenter)
		empty_image.setStyleSheet("background:transparent;border:none;")
		empty_image.setFixedSize(230, 145)
		empty_pixmap = QPixmap(NO_DELIVERY_LOGS_IMAGE)
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

		empty_title = QLabel("No delivery logs found")
		empty_title.setFont(playfair(16, QFont.Medium))
		empty_title.setAlignment(Qt.AlignCenter)
		empty_title.setStyleSheet(f"color:{GRAY_4};")

		empty_desc = QLabel("Logs matching the selected filters will appear here.")
		empty_desc.setFont(inter(12))
		empty_desc.setAlignment(Qt.AlignCenter)
		empty_desc.setWordWrap(True)
		empty_desc.setStyleSheet(f"color:{GRAY_3};")

		empty_lay.addWidget(empty_image, 0, Qt.AlignCenter)
		empty_lay.addWidget(empty_title)
		empty_lay.addWidget(empty_desc)

		self._stack = QStackedWidget()
		self._stack.addWidget(self._table)
		self._stack.addWidget(self._empty)
		content_lay.addWidget(self._stack)

		scroll.setWidget(content)
		root.addWidget(scroll)

	def _configure_date_edit(self, date_edit, min_height=34, min_width=130):
		date_edit.setStyleSheet(_date_edit_style(min_height=min_height, min_width=min_width))
		calendar = date_edit.calendarWidget()
		if calendar is None:
			return

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

	def _build_topbar(self):
		bar = QWidget()
		bar.setFixedHeight(84)
		bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")

		lay = QHBoxLayout(bar)
		lay.setContentsMargins(28, 8, 28, 8)

		breadcrumb = QLabel("DELIVERY LOGS")
		breadcrumb.setFont(inter(11, QFont.Medium))
		breadcrumb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		breadcrumb.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.5px;")
		lay.addWidget(breadcrumb)
		lay.addStretch()

		clock_col = QVBoxLayout()
		clock_col.setContentsMargins(0, 0, 0, 0)
		clock_col.setSpacing(2)
		clock_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

		self._clock_lbl = QLabel("--:--:--")
		self._clock_lbl.setFont(inter(17, QFont.Medium))
		self._clock_lbl.setAlignment(Qt.AlignRight)
		self._clock_lbl.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:1px;")

		self._date_lbl = QLabel("")
		self._date_lbl.setFont(inter(11))
		self._date_lbl.setAlignment(Qt.AlignRight)
		self._date_lbl.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.3px;")

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
		if self._controller:
			self.reload_data()

	def hideEvent(self, event):
		self._reset_view_state(reload=False)
		super().hideEvent(event)

	def reload_data(self):
		if not self._controller:
			return
		self._controller.load()

	def reset_view_state(self):
		self._reset_view_state(reload=True)

	def _reset_view_state(self, reload=True):
		today = QDate.currentDate()
		first_of_month = QDate(today.year(), today.month(), 1)

		self._filter_delivery_id.blockSignals(True)
		self._filter_status_type.blockSignals(True)
		self._date_from.blockSignals(True)
		self._date_to.blockSignals(True)

		self._filter_delivery_id.clear()
		self._filter_status_type.setCurrentIndex(0)
		self._date_from.setDate(first_of_month)
		self._date_to.setDate(today)

		self._filter_delivery_id.blockSignals(False)
		self._filter_status_type.blockSignals(False)
		self._date_from.blockSignals(False)
		self._date_to.blockSignals(False)

		if reload:
			self.reload_data()

	def show_error(self, title, message):
		QMessageBox.critical(self, title, str(message))

	def load_logs(self, logs):
		self._all_logs = list(logs)
		self._populate_status_type_filter()
		self._apply_filters()

	def _status_change_label(self, log_item):
		old_status = str(log_item.get("old_status", "")).strip()
		new_status = str(log_item.get("new_status", "")).strip()
		if old_status and new_status:
			return f"{old_status} -> {new_status}"
		if old_status:
			return old_status
		if new_status:
			return new_status
		return ""

	def _populate_status_type_filter(self):
		current = self._filter_status_type.currentText()
		status_types = sorted(
			{
				self._status_change_label(log)
				for log in self._all_logs
			}
		)
		self._filter_status_type.blockSignals(True)
		self._filter_status_type.clear()
		self._filter_status_type.addItem("All status records")
		for status in status_types:
			if status:
				self._filter_status_type.addItem(status)
		if current and self._filter_status_type.findText(current) != -1:
			self._filter_status_type.setCurrentText(current)
		self._filter_status_type.blockSignals(False)

	def _on_date_from_changed(self, new_date):
		if new_date > self._date_to.date():
			self._date_to.blockSignals(True)
			self._date_to.setDate(new_date)
			self._date_to.blockSignals(False)
		self._apply_filters()

	def _on_date_to_changed(self, new_date):
		if new_date < self._date_from.date():
			self._date_from.blockSignals(True)
			self._date_from.setDate(new_date)
			self._date_from.blockSignals(False)
		self._apply_filters()

	def _apply_filters(self, *_):
		wanted_id = self._filter_delivery_id.text().strip().lower()
		wanted_status_change = self._filter_status_type.currentText().strip().lower()
		date_from = self._date_from.date()
		date_to = self._date_to.date()

		def matches(log_item):
			delivery_id = str(log_item.get("delivery_id", "")).lower()
			status_change = self._status_change_label(log_item).strip().lower()
			changed_date = self._coerce_date(log_item.get("changed_on")) or self._coerce_date(log_item.get("changed_at", ""))

			if wanted_id and wanted_id not in delivery_id:
				return False
			if wanted_status_change != "all status records" and wanted_status_change != status_change:
				return False
			if changed_date is None:
				return False
			return date_from <= changed_date <= date_to

		self._filtered_logs = [log_item for log_item in self._all_logs if matches(log_item)]
		self._render_table()

	def _render_table(self):
		if not self._filtered_logs:
			self._table.setRowCount(0)
			self._stack.setCurrentWidget(self._empty)
			return

		self._stack.setCurrentWidget(self._table)
		self._table.setRowCount(len(self._filtered_logs))

		for row_index, log_item in enumerate(self._filtered_logs):
			self._set_item(row_index, 0, log_item.get("delivery_id", ""), Qt.AlignCenter)
			self._set_item(row_index, 1, log_item.get("customer_name", ""), Qt.AlignCenter)
			self._set_item(row_index, 2, self._status_value(log_item.get("old_status", "")), Qt.AlignCenter)
			self._set_item(row_index, 3, self._status_value(log_item.get("new_status", "")), Qt.AlignCenter)
			self._set_item(row_index, 4, log_item.get("changed_by", ""), Qt.AlignCenter)
			self._set_item(row_index, 5, log_item.get("changed_at", ""), Qt.AlignCenter)

		self._table.resizeRowsToContents()

	def _set_item(self, row, column, value, alignment):
		item = QTableWidgetItem(str(value))
		item.setFont(inter(11))
		item.setTextAlignment(alignment)
		self._table.setItem(row, column, item)

	@staticmethod
	def _status_value(value, fallback="-"):
		text = str(value or "").strip()
		return text or fallback

	def _on_row_clicked(self, row, _column):
		if row < 0 or row >= len(self._filtered_logs):
			return
		dialog = DeliveryLogDetailsDialog(self._filtered_logs[row], self)
		dialog.exec()

	def _coerce_date(self, changed_at):
		if not changed_at:
			return None
		if isinstance(changed_at, QDate):
			return changed_at if changed_at.isValid() else None

		text = " ".join(str(changed_at).split())
		for fmt in ("yyyy-MM-dd", "yyyy-M-d", "MMM d, yyyy", "MMMM d, yyyy", "MMM d, yyyy h:mm AP", "MMMM d, yyyy h:mm AP"):
			parsed = QDate.fromString(text, fmt)
			if parsed.isValid():
				return parsed

		date_text = " ".join(text.split()[:3])
		for fmt in ("MMM d, yyyy", "MMMM d, yyyy"):
			parsed = QDate.fromString(date_text, fmt)
			if parsed.isValid():
				return parsed
		return None

if __name__ == "__main__":
	app = QApplication(sys.argv)
	load_fonts()
	app.setFont(inter(11))

	from controllers.delivery_logs_controller import DeliveryLogsController

	view = DeliveryLogsView(show_topbar=True, controller=DeliveryLogsController())
	view.showMaximized()
	sys.exit(app.exec())
