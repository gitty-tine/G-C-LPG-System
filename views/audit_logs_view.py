import os
import re
import sys

from PySide6.QtCore import Qt, QTimer, QDate, QTime
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QColor, QTextCharFormat, QPixmap
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
	QDialog,
	QPushButton,
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
NO_AUDIT_LOGS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

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
CALENDAR_MONTH_YEAR_FONT_FAMILY = INTER_FAMILY
CALENDAR_MONTH_YEAR_FONT_SIZE = 14
CALENDAR_MONTH_YEAR_FONT_WEIGHT_CSS = 600
CALENDAR_MONTH_YEAR_FONT_WEIGHT_QT = QFont.DemiBold

_AUDIT_FIELD_PATTERN = re.compile(r"(?:(?<=^)|(?<=, ))([A-Za-z][A-Za-z ]{0,40}):\s*")


def _clean_audit_value(value):
	if value is None:
		return "-"
	text = " ".join(str(value).replace("\r", " ").replace("\n", " ").split())
	if not text or text.lower() in {"none", "null"}:
		return "-"
	return text


def _parse_audit_fields(value):
	text = _clean_audit_value(value)
	if text == "-":
		return []

	matches = list(_AUDIT_FIELD_PATTERN.finditer(text))
	if not matches:
		return []

	fields = []
	for index, match in enumerate(matches):
		label = match.group(1).strip()
		start = match.end()
		end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
		field_value = text[start:end].strip().rstrip(",").strip()
		fields.append((label, field_value or "-"))
	return fields


def _audit_change_rows(old_value, new_value):
	old_fields = _parse_audit_fields(old_value)
	new_fields = _parse_audit_fields(new_value)
	if not old_fields and not new_fields:
		return []

	old_map = {label: value for label, value in old_fields}
	new_map = {label: value for label, value in new_fields}
	labels = []
	for label, _ in old_fields + new_fields:
		if label not in labels:
			labels.append(label)

	rows = []
	for label in labels:
		before = old_map.get(label, "-")
		after = new_map.get(label, "-")
		rows.append((label, before, after, before != after))
	return rows


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


class AuditLogDetailsDialog(QDialog):
	def __init__(self, log_item, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setWindowTitle("Audit Log Details")
		self.setModal(True)
		self.setMinimumWidth(760)
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
				background:transparent;
				border:none;
				border-radius:0;
			}}
			QFrame#Panel {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:10px;
			}}
			QFrame#Summary {{
				background:{TEAL_PALE};
				border:1px solid #c9e4df;
				border-radius:8px;
			}}
			QFrame#ChangeTable {{
				background:#fbfcfc;
				border:1px solid {GRAY_2};
				border-radius:8px;
			}}
			QFrame#ChangedRow {{
				background:#f3faf8;
				border:1px solid #d8ebe7;
				border-radius:6px;
			}}
			QFrame#UnchangedRow {{
				background:{WHITE};
				border:1px solid {GRAY_2};
				border-radius:6px;
			}}
			QPushButton {{
				background:{TEAL};
				color:{WHITE};
				border:none;
				border-radius:7px;
				padding:9px 22px;
				font-family:'{INTER_FAMILY}';
				font-size:12px;
				font-weight:600;
			}}
			QPushButton:hover {{ background:{TEAL_DARK}; }}
			"""
		)

		root = QVBoxLayout(self)
		root.setContentsMargins(0, 0, 0, 0)
		root.setSpacing(0)

		surface = QFrame()
		surface.setObjectName("DialogSurface")
		surface_lay = QVBoxLayout(surface)
		surface_lay.setContentsMargins(22, 20, 22, 18)
		surface_lay.setSpacing(14)
		root.addWidget(surface)

		card = QFrame()
		card.setObjectName("Card")
		card_lay = QVBoxLayout(card)
		card_lay.setContentsMargins(0, 0, 0, 0)
		card_lay.setSpacing(16)

		header = QHBoxLayout()
		header.setSpacing(12)
		title_col = QVBoxLayout()
		title_col.setSpacing(4)

		title = QLabel("Audit Log Details")
		title.setFont(playfair(20, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};")

		subtitle = QLabel("Read-only record of a database change.")
		subtitle.setFont(inter(11))
		subtitle.setStyleSheet(f"color:{GRAY_4};")

		title_col.addWidget(title)
		title_col.addWidget(subtitle)

		badge = QLabel(log_item.get("activity_type", "Activity"))
		badge.setFont(inter(10, QFont.DemiBold))
		badge.setAlignment(Qt.AlignCenter)
		badge.setFixedHeight(28)
		badge.setMinimumWidth(86)
		badge.setStyleSheet(self._badge_style(log_item.get("activity_type", "")))

		header.addLayout(title_col)
		header.addStretch()
		header.addWidget(badge)
		card_lay.addLayout(header)

		summary = QFrame()
		summary.setObjectName("Summary")
		summary_lay = QHBoxLayout(summary)
		summary_lay.setContentsMargins(16, 14, 16, 14)
		summary_lay.setSpacing(18)

		summary_lay.addLayout(
			self._summary_block(
				"Affected record",
				f"{log_item.get('section_name', 'Record')} #{log_item.get('record_id', '-')}",
			)
		)
		summary_lay.addStretch()
		summary_lay.addLayout(
			self._summary_block(
				"What happened",
				log_item.get("description", "Record changed"),
				align_right=True,
			)
		)
		card_lay.addWidget(summary)

		meta = QFrame()
		meta.setObjectName("Panel")
		meta_grid = QGridLayout(meta)
		meta_grid.setContentsMargins(16, 14, 16, 14)
		meta_grid.setHorizontalSpacing(28)
		meta_grid.setVerticalSpacing(12)

		meta_items = [
			("Section", log_item.get("section_name", "-")),
			("Record ID", log_item.get("record_id", "-")),
			("Done by", log_item.get("changed_by", "-")),
			("When", log_item.get("changed_at", "-")),
		]
		for index, (label_text, value) in enumerate(meta_items):
			row = index // 2
			col = index % 2
			meta_grid.addLayout(self._meta_block(label_text, value), row, col)
		card_lay.addWidget(meta)

		changes_title = QLabel("Changed Data")
		changes_title.setFont(inter(11, QFont.DemiBold))
		changes_title.setStyleSheet(f"color:{GRAY_4};letter-spacing:1px;")
		card_lay.addWidget(changes_title)

		change_rows = _audit_change_rows(log_item.get("old_value"), log_item.get("new_value"))
		if change_rows:
			card_lay.addWidget(self._build_change_table(change_rows))
		else:
			card_lay.addWidget(
				self._build_raw_change_table(
					_clean_audit_value(log_item.get("old_value")),
					_clean_audit_value(log_item.get("new_value")),
				)
			)

		surface_lay.addWidget(card)

		btn_row = QHBoxLayout()
		btn_row.addStretch()

		close_btn = QPushButton("Close")
		close_btn.setCursor(Qt.PointingHandCursor)
		close_btn.setFont(inter(10, QFont.Medium))
		close_btn.setFixedSize(92, 34)
		close_btn.clicked.connect(self.accept)
		btn_row.addWidget(close_btn)
		surface_lay.addLayout(btn_row)

	def _summary_block(self, label_text, value, align_right=False):
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(3)
		alignment = Qt.AlignRight if align_right else Qt.AlignLeft

		label = QLabel(label_text)
		label.setFont(inter(9, QFont.DemiBold))
		label.setAlignment(alignment)
		label.setStyleSheet(f"color:{GRAY_4};letter-spacing:1px;")

		value_label = QLabel(str(value))
		value_label.setFont(inter(14, QFont.DemiBold))
		value_label.setAlignment(alignment)
		value_label.setWordWrap(True)
		value_label.setStyleSheet(f"color:{TEAL_DARK};")

		layout.addWidget(label)
		layout.addWidget(value_label)
		return layout

	def _meta_block(self, label_text, value):
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(3)

		label = QLabel(label_text)
		label.setFont(inter(9, QFont.DemiBold))
		label.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.7px;")

		value_label = QLabel(str(value))
		value_label.setFont(inter(11, QFont.Medium))
		value_label.setWordWrap(True)
		value_label.setStyleSheet(f"color:{GRAY_5};")

		layout.addWidget(label)
		layout.addWidget(value_label)
		return layout

	def _build_change_table(self, rows):
		table = QFrame()
		table.setObjectName("ChangeTable")
		layout = QGridLayout(table)
		layout.setContentsMargins(12, 12, 12, 12)
		layout.setHorizontalSpacing(10)
		layout.setVerticalSpacing(8)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 2)
		layout.setColumnStretch(2, 2)

		for column, text in enumerate(("Field", "Before", "After")):
			header = QLabel(text)
			header.setFont(inter(9, QFont.DemiBold))
			header.setStyleSheet(f"color:{GRAY_4};letter-spacing:0.7px;")
			layout.addWidget(header, 0, column)

		for row_index, (field, before, after, changed) in enumerate(rows, start=1):
			row_name = "ChangedRow" if changed else "UnchangedRow"
			for column, value in enumerate((field, before, after)):
				cell = QFrame()
				cell.setObjectName(row_name)
				cell_lay = QVBoxLayout(cell)
				cell_lay.setContentsMargins(10, 8, 10, 8)
				cell_lay.setSpacing(0)

				label = QLabel(str(value))
				label.setFont(inter(10, QFont.DemiBold if column == 0 else QFont.Normal))
				label.setWordWrap(True)
				if changed and column == 2:
					color = TEAL_DARK
				elif changed and column == 1:
					color = AMBER
				else:
					color = GRAY_5
				label.setStyleSheet(f"color:{color};")

				cell_lay.addWidget(label)
				layout.addWidget(cell, row_index, column)

		return table

	def _build_raw_change_table(self, before, after):
		return self._build_change_table([
			("Complete value", before, after, before != after),
		])

	def _badge_style(self, activity_type):
		if activity_type == "Added":
			bg, fg, border = GREEN_BG, GREEN, "#b9dcc7"
		elif activity_type == "Updated":
			bg, fg, border = AMBER_BG, AMBER, "#efd290"
		elif activity_type == "Deleted":
			bg, fg, border = RED_BG, RED, "#efb8b8"
		else:
			bg, fg, border = TEAL_PALE, TEAL_DARK, "#c9e4df"
		return f"""
			background:{bg};
			color:{fg};
			border:1px solid {border};
			border-radius:14px;
			padding:0 12px;
		"""


class AuditLogsView(QWidget):
	def __init__(self, parent=None, show_topbar=True, controller=None):
		super().__init__(parent)
		self._show_topbar = show_topbar
		self._all_logs = []
		self._filtered_logs = []
		self._controller = None
		self._last_logs_signature = None
		self._last_filter_signature = None
		self._live_refresh = QTimer(self)
		self._live_refresh.setInterval(1000)
		self._live_refresh.timeout.connect(self._refresh_live)

		load_fonts()
		self.setStyleSheet(f"background:{GRAY_1};")
		self._build_ui()
		self._populate_filters()
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

		sub = QLabel("SYSTEM ACTIVITY TRACKING")
		sub.setFont(inter(10, QFont.DemiBold))
		sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;")

		title = QLabel("Audit Logs")
		title.setFont(playfair(28, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};")

		desc = QLabel("View all system records - view-only audit trail of database changes.")
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
		sections_card, self._sections_touched_lbl = self._summary_card(
			"SECTIONS AFFECTED",
			"0",
			"Unique system areas",
			TEAL_DARK,
		)
		latest_card, self._latest_activity_lbl = self._summary_card(
			"LATEST ACTIVITY",
			"-",
			"Most recent visible log",
			GRAY_5,
		)
		summary_row.addWidget(visible_card, 1)
		summary_row.addWidget(sections_card, 1)
		summary_row.addWidget(latest_card, 2)
		content_lay.addLayout(summary_row)

		# Filter bar
		filter_row = QHBoxLayout()
		filter_row.setContentsMargins(0, 4, 0, 2)
		filter_row.setSpacing(10)

		self._filter_action_type = QComboBox()
		self._filter_action_type.setFont(inter(11))
		self._filter_action_type.setFixedHeight(34)
		self._filter_action_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._filter_action_type.currentIndexChanged.connect(self._apply_filters)

		self._filter_section = QComboBox()
		self._filter_section.setFont(inter(11))
		self._filter_section.setFixedHeight(34)
		self._filter_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._filter_section.currentIndexChanged.connect(self._apply_filters)

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

		self._filter_action_type.setStyleSheet(_combo_box_style())
		self._filter_section.setStyleSheet(_combo_box_style())
		self._configure_date_edit(self._date_from)
		self._configure_date_edit(self._date_to)

		filter_row.addWidget(self._filter_action_type)
		filter_row.addWidget(self._filter_section)
		filter_row.addWidget(from_lbl)
		filter_row.addWidget(self._date_from)
		filter_row.addWidget(to_lbl)
		filter_row.addWidget(self._date_to)
		content_lay.addLayout(filter_row)

		self._logs_card = self._build_logs_card()

		# Empty state
		self._empty = QWidget()
		empty_lay = QVBoxLayout(self._empty)
		empty_lay.setContentsMargins(0, 36, 0, 36)
		empty_lay.setAlignment(Qt.AlignCenter)

		empty_image = QLabel()
		empty_image.setAlignment(Qt.AlignCenter)
		empty_image.setStyleSheet("background:transparent;border:none;")
		empty_image.setFixedSize(230, 145)
		empty_pixmap = QPixmap(NO_AUDIT_LOGS_IMAGE)
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

		empty_title = QLabel("No audit logs found")
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
		card.setObjectName("AuditLogsCard")
		card.setMinimumHeight(540)
		card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		card.setStyleSheet(
			f"""
			QFrame#AuditLogsCard {{
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
		header_lay = QHBoxLayout(header)
		header_lay.setContentsMargins(16, 0, 16, 0)
		header_lay.setSpacing(14)

		header_lay.addWidget(self._log_header_label("ACTIVITY", 112))
		header_lay.addWidget(self._log_header_label("SECTION", 150))
		header_lay.addWidget(self._log_header_label("CHANGE", None), 1)
		header_lay.addWidget(self._log_header_label("DONE BY", 160))
		header_lay.addWidget(self._log_header_label("WHEN", 200))
		header_lay.addWidget(self._log_header_label("", 76))
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

	def _build_topbar(self):
		bar = QWidget()
		bar.setFixedHeight(84)
		bar.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")

		lay = QHBoxLayout(bar)
		lay.setContentsMargins(28, 8, 28, 8)

		breadcrumb = QLabel("AUDIT LOGS")
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
			self._live_refresh.start()

	def hideEvent(self, event):
		self._live_refresh.stop()
		self._reset_view_state(reload=False)
		super().hideEvent(event)

	def _refresh_live(self):
		if self._controller and self.isVisible():
			self.reload_data()

	def reload_data(self):
		if not self._controller:
			return
		self._controller.load(
			date_from=self._date_from.date().toString("yyyy-MM-dd"),
			date_to=self._date_to.date().toString("yyyy-MM-dd"),
		)

	def reset_view_state(self):
		self._reset_view_state(reload=True)

	def _reset_view_state(self, reload=True):
		today = QDate.currentDate()
		first_of_month = QDate(today.year(), today.month(), 1)

		self._filter_action_type.blockSignals(True)
		self._filter_section.blockSignals(True)
		self._date_from.blockSignals(True)
		self._date_to.blockSignals(True)

		self._filter_action_type.setCurrentIndex(0)
		self._filter_section.setCurrentIndex(0)
		self._date_from.setDate(first_of_month)
		self._date_to.setDate(today)

		self._filter_action_type.blockSignals(False)
		self._filter_section.blockSignals(False)
		self._date_from.blockSignals(False)
		self._date_to.blockSignals(False)

		if reload:
			self.reload_data()

	def show_error(self, title, message):
		QMessageBox.critical(self, title, str(message))

	def load_logs(self, logs):
		next_logs = list(logs)
		signature = tuple(
			(
				str(log_item.get("id", "")),
				str(log_item.get("changed_at_raw", "")),
				str(log_item.get("old_value", "")),
				str(log_item.get("new_value", "")),
			)
			for log_item in next_logs
		)
		filter_signature = self._filter_signature()
		if signature == self._last_logs_signature and filter_signature == self._last_filter_signature:
			return

		logs_changed = signature != self._last_logs_signature
		self._last_logs_signature = signature
		self._all_logs = next_logs
		if logs_changed:
			self._populate_filters()
		self._apply_filters()

	def _populate_filters(self):
		# Populate activity type filter
		current_action = self._filter_action_type.currentText()
		action_types = sorted({log.get("activity_type", "").strip() for log in self._all_logs})
		self._filter_action_type.blockSignals(True)
		self._filter_action_type.clear()
		self._filter_action_type.addItem("All activities")
		for action in action_types:
			if action:
				self._filter_action_type.addItem(action)
		if current_action and self._filter_action_type.findText(current_action) != -1:
			self._filter_action_type.setCurrentText(current_action)
		self._filter_action_type.blockSignals(False)

		# Populate section filter
		current_section = self._filter_section.currentText()
		sections = sorted({log.get("section_name", "").strip() for log in self._all_logs})
		self._filter_section.blockSignals(True)
		self._filter_section.clear()
		self._filter_section.addItem("All sections")
		for section in sections:
			if section:
				self._filter_section.addItem(section)
		if current_section and self._filter_section.findText(current_section) != -1:
			self._filter_section.setCurrentText(current_section)
		self._filter_section.blockSignals(False)

	def _on_date_from_changed(self, new_date):
		if new_date > self._date_to.date():
			self._date_to.blockSignals(True)
			self._date_to.setDate(new_date)
			self._date_to.blockSignals(False)
		if self._controller:
			self.reload_data()
		else:
			self._apply_filters()

	def _on_date_to_changed(self, new_date):
		if new_date < self._date_from.date():
			self._date_from.blockSignals(True)
			self._date_from.setDate(new_date)
			self._date_from.blockSignals(False)
		if self._controller:
			self.reload_data()
		else:
			self._apply_filters()

	def _apply_filters(self, *_):
		self._last_filter_signature = self._filter_signature()
		wanted_action = self._filter_action_type.currentText().strip().lower()
		wanted_section = self._filter_section.currentText().strip().lower()
		date_from = self._date_from.date()
		date_to = self._date_to.date()

		def matches(log_item):
			action = log_item.get("activity_type", "").strip().lower()
			section = log_item.get("section_name", "").strip().lower()
			changed_date = self._coerce_date(log_item.get("changed_at_raw")) or self._coerce_date(log_item.get("changed_at", ""))

			if wanted_action != "all activities" and wanted_action != action:
				return False
			if wanted_section != "all sections" and wanted_section != section:
				return False
			if changed_date is None:
				return False
			return date_from <= changed_date <= date_to

		self._filtered_logs = [log_item for log_item in self._all_logs if matches(log_item)]
		self._update_summary_cards()
		self._render_logs()

	def _filter_signature(self):
		if not hasattr(self, "_filter_action_type"):
			return None
		return (
			self._filter_action_type.currentText(),
			self._filter_section.currentText(),
			self._date_from.date().toString("yyyy-MM-dd"),
			self._date_to.date().toString("yyyy-MM-dd"),
		)

	def _open_details(self, row, _column=0):
		if row < 0 or row >= len(self._filtered_logs):
			return
		dialog = AuditLogDetailsDialog(self._filtered_logs[row], self)
		dialog.exec()

	def _update_summary_cards(self):
		if not hasattr(self, "_visible_logs_lbl"):
			return

		visible_count = len(self._filtered_logs)
		section_count = len(
			{
				str(log_item.get("section_name", "")).strip()
				for log_item in self._filtered_logs
				if str(log_item.get("section_name", "")).strip()
			}
		)
		latest_activity = "-"
		if self._filtered_logs:
			latest = self._filtered_logs[0]
			latest_activity = str(latest.get("changed_at", "") or "-")

		self._visible_logs_lbl.setText(f"{visible_count:,}")
		self._sections_touched_lbl.setText(f"{section_count:,}")
		self._latest_activity_lbl.setText(latest_activity)

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
		if not hasattr(self, "_logs_lay"):
			return
		while self._logs_lay.count():
			item = self._logs_lay.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()

	def _build_log_row(self, log_item, row_index):
		row = QFrame()
		row.setObjectName("AuditLogRow")
		row.setCursor(Qt.PointingHandCursor)
		row.setFixedHeight(72)
		row.setStyleSheet(
			f"""
			QFrame#AuditLogRow {{
				background:#fbfdfc;
				border:1px solid {GRAY_2};
				border-radius:6px;
			}}
			QFrame#AuditLogRow:hover {{
				background:#eef8f6;
				border-color:#c9ddd9;
			}}
			"""
		)
		row.mouseDoubleClickEvent = lambda event, index=row_index: self._open_details(index)

		lay = QHBoxLayout(row)
		lay.setContentsMargins(14, 0, 14, 0)
		lay.setSpacing(14)

		lay.addWidget(self._activity_pill(log_item.get("activity_type", "")))
		lay.addWidget(self._log_cell(log_item.get("section_name", ""), 150, TEAL_DARK, QFont.Medium))
		lay.addWidget(self._change_cell(log_item), 1)
		lay.addWidget(self._log_cell(log_item.get("changed_by", ""), 160, GRAY_5))
		lay.addWidget(self._log_cell(log_item.get("changed_at", ""), 200, GRAY_4))
		lay.addWidget(self._details_button(row_index), 76)
		return row

	def _activity_pill(self, activity_type):
		bg, fg, border = self._activity_colors(activity_type)
		pill = QLabel(str(activity_type or "Activity"))
		pill.setFont(inter(10, QFont.DemiBold))
		pill.setAlignment(Qt.AlignCenter)
		pill.setFixedSize(112, 30)
		pill.setStyleSheet(
			f"""
			background:{bg};
			color:{fg};
			border:1px solid {border};
			border-radius:15px;
			"""
		)
		return pill

	def _change_cell(self, log_item):
		widget = QWidget()
		widget.setStyleSheet("background:transparent;border:none;")
		lay = QVBoxLayout(widget)
		lay.setContentsMargins(0, 0, 0, 0)
		lay.setSpacing(3)

		title = QLabel(str(log_item.get("description", "") or "Record changed"))
		title.setFont(inter(11, QFont.DemiBold))
		title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		title.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

		preview = QLabel(self._change_preview(log_item))
		preview.setFont(inter(10))
		preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		preview.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		lay.addStretch()
		lay.addWidget(title)
		lay.addWidget(preview)
		lay.addStretch()
		return widget

	def _log_cell(self, value, width=None, color=GRAY_5, weight=QFont.Normal):
		label = QLabel(str(value or "-"))
		label.setFont(inter(11, weight))
		label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		label.setStyleSheet(f"color:{color};background:transparent;border:none;")
		label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		if width is not None:
			label.setFixedWidth(width)
		return label

	def _details_button(self, row_index):
		button = QToolButton()
		button.setText("View")
		button.setCursor(Qt.PointingHandCursor)
		button.setFixedSize(68, 32)
		button.clicked.connect(lambda _checked=False, index=row_index: self._open_details(index))
		button.setStyleSheet(
			f"""
			QToolButton {{
				background:{WHITE};
				color:{TEAL_DARK};
				border:1px solid #b9d4cf;
				border-radius:7px;
				font-family:'{INTER_FAMILY}';
				font-size:12px;
				font-weight:600;
			}}
			QToolButton:hover {{
				background:{TEAL_PALE};
				border-color:{TEAL};
			}}
			"""
		)
		return button

	def _change_preview(self, log_item):
		rows = _audit_change_rows(log_item.get("old_value"), log_item.get("new_value"))
		if rows:
			changed_rows = [row for row in rows if row[3]]
			if not changed_rows:
				changed_rows = rows
			field, before, after, _changed = changed_rows[0]
			preview = f"{field}: {before} -> {after}"
			if len(changed_rows) > 1:
				preview += f"  +{len(changed_rows) - 1} more"
			return self._trim_text(preview, 96)

		action = str(log_item.get("raw_action", "")).strip().upper()
		if action == "INSERT":
			return self._trim_text(f"Added: {_clean_audit_value(log_item.get('new_value'))}", 96)
		if action == "DELETE":
			return self._trim_text(f"Deleted: {_clean_audit_value(log_item.get('old_value'))}", 96)
		return self._trim_text(
			f"{_clean_audit_value(log_item.get('old_value'))} -> {_clean_audit_value(log_item.get('new_value'))}",
			96,
		)

	@staticmethod
	def _trim_text(value, limit):
		text = " ".join(str(value or "-").split())
		if len(text) <= limit:
			return text
		return text[: max(0, limit - 3)].rstrip() + "..."

	@staticmethod
	def _activity_colors(activity_type):
		if activity_type == "Added":
			return GREEN_BG, GREEN, "#b9dcc7"
		if activity_type == "Updated":
			return AMBER_BG, AMBER, "#efd290"
		if activity_type == "Deleted":
			return RED_BG, RED, "#efb8b8"
		return TEAL_PALE, TEAL_DARK, "#c9e4df"

	def _coerce_date(self, changed_at):
		if not changed_at:
			return None
		if isinstance(changed_at, QDate):
			return changed_at if changed_at.isValid() else None
		if hasattr(changed_at, "year") and hasattr(changed_at, "month") and hasattr(changed_at, "day"):
			return QDate(changed_at.year, changed_at.month, changed_at.day)

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

	from controllers.audit_logs_controller import AuditLogsController

	view = AuditLogsView(show_topbar=True, controller=AuditLogsController())
	view.showMaximized()
	sys.exit(app.exec())
