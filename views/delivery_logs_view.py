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
		self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setWindowTitle("Delivery Status Record")
		self.setModal(True)
		self.setMinimumWidth(660)
		self.setStyleSheet(
			f"""
			QDialog {{ background:transparent; }}
			QLabel {{ color:{GRAY_5}; background:transparent; border:none; }}
			QFrame#DialogSurface {{
				background:#f8faf9;
				border:1px solid #d8e2e0;
				border-radius:12px;
			}}
			QFrame#Card {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:10px;
			}}
			QFrame#StatusBand {{
				background:{TEAL_PALE};
				border:1px solid #cfe1dd;
				border-radius:8px;
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

		header_row = QHBoxLayout()
		header_row.setContentsMargins(0, 0, 0, 0)
		header_row.setSpacing(16)

		header_text = QVBoxLayout()
		header_text.setContentsMargins(0, 0, 0, 0)
		header_text.setSpacing(3)

		title = QLabel("Delivery Status Record")
		title.setFont(playfair(22, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};")

		subtitle = QLabel("Audit entry showing who updated the delivery status and when.")
		subtitle.setFont(inter(11))
		subtitle.setStyleSheet(f"color:{GRAY_4};")

		header_text.addWidget(title)
		header_text.addWidget(subtitle)

		read_only = QLabel("READ ONLY")
		read_only.setFont(inter(9, QFont.DemiBold))
		read_only.setAlignment(Qt.AlignCenter)
		read_only.setFixedSize(86, 28)
		read_only.setStyleSheet(
			f"background:{WHITE};color:{TEAL_DARK};border:1px solid {GRAY_2};border-radius:6px;letter-spacing:1px;"
		)

		header_row.addLayout(header_text, 1)
		header_row.addWidget(read_only, 0, Qt.AlignTop)
		surface_lay.addLayout(header_row)

		old_status = self._status_value(log_item.get("old_status", ""))
		new_status = self._status_value(log_item.get("new_status", ""))

		status_band = QFrame()
		status_band.setObjectName("StatusBand")
		status_lay = QHBoxLayout(status_band)
		status_lay.setContentsMargins(16, 12, 16, 12)
		status_lay.setSpacing(10)

		status_label = QLabel("STATUS UPDATE")
		status_label.setFont(inter(10, QFont.DemiBold))
		status_label.setStyleSheet(f"color:{GRAY_4};letter-spacing:1px;")

		status_value = QLabel(f"{old_status} to {new_status}")
		status_value.setFont(inter(15, QFont.DemiBold))
		status_value.setStyleSheet(f"color:{self._status_color(new_status)};")

		status_lay.addWidget(status_label)
		status_lay.addStretch()
		status_lay.addWidget(status_value)
		surface_lay.addWidget(status_band)

		card = QFrame()
		card.setObjectName("Card")
		card_lay = QVBoxLayout(card)
		card_lay.setContentsMargins(18, 16, 18, 16)
		card_lay.setSpacing(12)

		section_title = QLabel("Record Information")
		section_title.setFont(inter(10, QFont.DemiBold))
		section_title.setStyleSheet(f"color:{TEAL_DARK};letter-spacing:0.8px;")
		card_lay.addWidget(section_title)

		detail_rows = [
			("Delivery", self._delivery_reference(log_item.get("delivery_id", ""))),
			("Customer", log_item.get("customer_name", "")),
			("Updated by", log_item.get("changed_by", "")),
			("Updated at", log_item.get("changed_at", "")),
			("Scheduled for", log_item.get("scheduled_date", "")),
			("Delivery address", log_item.get("address", "")),
			("Items", log_item.get("products", "")),
			("Notes", log_item.get("notes", "")),
		]

		for label_text, value_text in detail_rows:
			card_lay.addWidget(self._detail_row(label_text, value_text))

		surface_lay.addWidget(card)

		btn_row = QHBoxLayout()
		btn_row.addStretch()

		close_btn = QPushButton("Close")
		close_btn.setCursor(Qt.PointingHandCursor)
		close_btn.setFont(inter(10, QFont.Medium))
		close_btn.setFixedSize(92, 34)
		close_btn.setStyleSheet(
			f"""
			QPushButton {{
				background:{TEAL};
				color:{WHITE};
				border:1px solid {TEAL};
				border-radius:6px;
			}}
			QPushButton:hover {{
				background:{TEAL_DARK};
			}}
			"""
		)
		close_btn.clicked.connect(self.accept)
		btn_row.addWidget(close_btn)
		surface_lay.addLayout(btn_row)

	def _detail_row(self, label_text, value_text):
		row = QWidget()
		row.setStyleSheet("background:transparent;border:none;")
		lay = QHBoxLayout(row)
		lay.setContentsMargins(0, 0, 0, 0)
		lay.setSpacing(14)

		label = QLabel(label_text)
		label.setFont(inter(10, QFont.DemiBold))
		label.setFixedWidth(126)
		label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		label.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.5px;")

		value = QLabel(str(value_text or "-"))
		value.setFont(inter(11, QFont.Medium))
		value.setWordWrap(True)
		value.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		value.setStyleSheet(f"color:{GRAY_5};")

		lay.addWidget(label)
		lay.addWidget(value, 1)
		return row

	@staticmethod
	def _delivery_reference(value):
		text = str(value or "").strip()
		return f"#{text}" if text else "-"

	@staticmethod
	def _status_value(value, fallback="-"):
		text = str(value or "").strip()
		return text or fallback

	@staticmethod
	def _status_color(status):
		status_lower = str(status or "").strip().lower()
		if status_lower == "delivered":
			return "#087443"
		if status_lower == "cancelled":
			return "#a70000"
		if status_lower == "pending":
			return "#9a5c00"
		if status_lower == "in transit":
			return TEAL_DARK
		return GRAY_5


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
		self._render_logs()
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

		summary_row = QHBoxLayout()
		summary_row.setContentsMargins(0, 4, 0, 0)
		summary_row.setSpacing(12)

		visible_card, self._visible_logs_lbl = self._summary_card(
			"VISIBLE LOGS",
			"0",
			"Matching current filters",
			TEAL,
		)
		tracked_card, self._tracked_deliveries_lbl = self._summary_card(
			"DELIVERIES TRACKED",
			"0",
			"Unique delivery records",
			TEAL_DARK,
		)
		latest_card, self._latest_change_lbl = self._summary_card(
			"LATEST CHANGE",
			"-",
			"Most recent visible log",
			GRAY_5,
		)
		summary_row.addWidget(visible_card, 1)
		summary_row.addWidget(tracked_card, 1)
		summary_row.addWidget(latest_card, 2)
		content_lay.addLayout(summary_row)

		filter_row = QHBoxLayout()
		filter_row.setContentsMargins(0, 4, 0, 2)
		filter_row.setSpacing(10)

		self._filter_delivery_id = QLineEdit()
		self._filter_delivery_id.setPlaceholderText("Search delivery ID")
		self._filter_delivery_id.setFont(inter(11))
		self._filter_delivery_id.setFixedHeight(34)
		self._filter_delivery_id.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._filter_delivery_id.textChanged.connect(self._apply_filters)

		self._filter_status_type = QComboBox()
		self._filter_status_type.setFont(inter(11))
		self._filter_status_type.setFixedHeight(34)
		self._filter_status_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._filter_status_type.currentIndexChanged.connect(self._apply_filters)

		self._date_from = QDateEdit()
		self._date_from.setCalendarPopup(True)
		self._date_from.setDisplayFormat("MMM d, yyyy")
		today = QDate.currentDate()
		first_of_month = QDate(today.year(), today.month(), 1)
		self._date_from.setDate(first_of_month)
		self._date_from.setFont(inter(11))
		self._date_from.setFixedHeight(34)
		self._date_from.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._date_from.dateChanged.connect(self._on_date_from_changed)

		self._date_to = QDateEdit()
		self._date_to.setCalendarPopup(True)
		self._date_to.setDisplayFormat("MMM d, yyyy")
		self._date_to.setDate(today)
		self._date_to.setFont(inter(11))
		self._date_to.setFixedHeight(34)
		self._date_to.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
		self._filter_status_type.setStyleSheet(_combo_box_style())
		self._configure_date_edit(self._date_from)
		self._configure_date_edit(self._date_to)

		filter_row.addWidget(self._filter_delivery_id)
		filter_row.addWidget(self._filter_status_type)
		filter_row.addWidget(from_lbl)
		filter_row.addWidget(self._date_from)
		filter_row.addWidget(to_lbl)
		filter_row.addWidget(self._date_to)
		content_lay.addLayout(filter_row)

		self._logs_card = self._build_logs_card()

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
		self._stack.addWidget(self._logs_card)
		self._stack.addWidget(self._empty)
		content_lay.addWidget(self._stack)

		scroll.setWidget(content)
		root.addWidget(scroll)

	def _summary_card(self, title, value, caption, color):
		card = QFrame()
		card.setStyleSheet(
			f"""
			QFrame {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:8px;
			}}
			"""
		)
		card.setFixedHeight(96)
		card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

		lay = QVBoxLayout(card)
		lay.setContentsMargins(18, 12, 18, 12)
		lay.setSpacing(3)

		title_lbl = QLabel(title)
		title_lbl.setFont(inter(9, QFont.DemiBold))
		title_lbl.setStyleSheet(
			f"color:{GRAY_4};letter-spacing:1.2px;background:transparent;border:none;"
		)

		value_lbl = QLabel(value)
		value_lbl.setFont(inter(19, QFont.DemiBold))
		value_lbl.setMinimumHeight(28)
		value_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		value_lbl.setStyleSheet(f"color:{color};background:transparent;border:none;")

		caption_lbl = QLabel(caption)
		caption_lbl.setFont(inter(10))
		caption_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		lay.addWidget(title_lbl)
		lay.addWidget(value_lbl)
		lay.addWidget(caption_lbl)
		lay.addStretch()
		return card, value_lbl

	def _build_logs_card(self):
		card = QFrame()
		card.setStyleSheet(
			f"""
			QFrame#LogsCard {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:8px;
			}}
			"""
		)
		card.setObjectName("LogsCard")
		card.setMinimumHeight(540)
		card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		root = QVBoxLayout(card)
		root.setContentsMargins(0, 0, 0, 0)
		root.setSpacing(0)

		header = QWidget()
		header.setFixedHeight(54)
		header.setStyleSheet(f"background:#f4f8f7;border:none;border-bottom:1px solid {GRAY_2};")
		header_lay = QHBoxLayout(header)
		header_lay.setContentsMargins(16, 0, 16, 0)
		header_lay.setSpacing(14)

		header_lay.addWidget(self._log_header_label("DELIVERY ID", 112))
		header_lay.addWidget(self._log_header_label("CUSTOMER", None), 1)
		header_lay.addWidget(self._log_header_label("STATUS CHANGE", 210))
		header_lay.addWidget(self._log_header_label("CHANGED BY", 170))
		header_lay.addWidget(self._log_header_label("DATE & TIME", 220))
		root.addWidget(header)

		self._logs_scroll = QScrollArea()
		self._logs_scroll.setWidgetResizable(True)
		self._logs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._logs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self._logs_scroll.setStyleSheet(owner_scrollbar_qss())

		self._logs_list = QWidget()
		self._logs_list.setStyleSheet("background:transparent;border:none;")
		self._logs_lay = QVBoxLayout(self._logs_list)
		self._logs_lay.setContentsMargins(14, 14, 14, 14)
		self._logs_lay.setSpacing(8)

		self._logs_scroll.setWidget(self._logs_list)
		root.addWidget(self._logs_scroll)
		return card

	def _log_header_label(self, text, width=None):
		label = QLabel(text)
		label.setFont(inter(10, QFont.DemiBold))
		label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		label.setStyleSheet(
			f"color:{GRAY_4};letter-spacing:1px;background:transparent;border:none;"
		)
		if width is not None:
			label.setFixedWidth(width)
		return label

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
		self._update_summary_cards()
		self._render_logs()

	def _update_summary_cards(self):
		if not hasattr(self, "_visible_logs_lbl"):
			return

		visible_count = len(self._filtered_logs)
		delivery_count = len(
			{
				str(log_item.get("delivery_id", "")).strip()
				for log_item in self._filtered_logs
				if str(log_item.get("delivery_id", "")).strip()
			}
		)
		latest_change = "-"
		if self._filtered_logs:
			latest_change = str(self._filtered_logs[0].get("changed_at", "") or "-")

		self._visible_logs_lbl.setText(f"{visible_count:,}")
		self._tracked_deliveries_lbl.setText(f"{delivery_count:,}")
		self._latest_change_lbl.setText(latest_change)

	def _render_logs(self):
		self._clear_log_rows()
		if not self._filtered_logs:
			self._stack.setCurrentWidget(self._empty)
			return

		self._stack.setCurrentWidget(self._logs_card)

		for row_index, log_item in enumerate(self._filtered_logs):
			self._logs_lay.addWidget(self._build_log_row(log_item, row_index))

		self._logs_lay.addStretch()

	def _clear_log_rows(self):
		while self._logs_lay.count():
			item = self._logs_lay.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()

	def _build_log_row(self, log_item, row_index):
		row = QFrame()
		row.setObjectName("DeliveryLogRow")
		row.setCursor(Qt.PointingHandCursor)
		row.setFixedHeight(58)
		row.setStyleSheet(
			f"""
			QFrame#DeliveryLogRow {{
				background:#fbfdfc;
				border:1px solid {GRAY_2};
				border-radius:6px;
			}}
			QFrame#DeliveryLogRow:hover {{
				background:#eef8f6;
				border-color:#c9ddd9;
			}}
			"""
		)
		row.mouseDoubleClickEvent = lambda event, index=row_index: self._open_log_details(index)

		lay = QHBoxLayout(row)
		lay.setContentsMargins(14, 0, 14, 0)
		lay.setSpacing(14)

		old_status = self._status_value(log_item.get("old_status", ""))
		new_status = self._status_value(log_item.get("new_status", ""))

		lay.addWidget(self._log_cell(log_item.get("delivery_id", ""), 112, TEAL_DARK, QFont.Medium))
		lay.addWidget(self._log_cell(log_item.get("customer_name", ""), None, GRAY_5), 1)
		lay.addWidget(
			self._log_cell(
				f"{old_status} to {new_status}",
				210,
				self._status_color(new_status),
				QFont.Medium,
			)
		)
		lay.addWidget(self._log_cell(log_item.get("changed_by", ""), 170, GRAY_5))
		lay.addWidget(self._log_cell(log_item.get("changed_at", ""), 220, GRAY_4))
		return row

	def _log_cell(self, value, width=None, color=GRAY_5, weight=QFont.Normal):
		label = QLabel(str(value or "-"))
		label.setFont(inter(11, weight))
		label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		label.setStyleSheet(f"color:{color};background:transparent;border:none;")
		label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		if width is not None:
			label.setFixedWidth(width)
		return label

	@staticmethod
	def _status_color(status):
		status_lower = str(status or "").strip().lower()
		if status_lower == "delivered":
			return "#087443"
		if status_lower == "cancelled":
			return "#a70000"
		if status_lower == "pending":
			return "#9a5c00"
		if status_lower == "in transit":
			return TEAL_DARK
		return GRAY_5

	@staticmethod
	def _status_value(value, fallback="-"):
		text = str(value or "").strip()
		return text or fallback

	def _open_log_details(self, row):
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
