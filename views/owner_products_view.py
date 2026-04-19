import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from views.admin_dashboard_view import owner_scrollbar_qss
from controllers.owner_product_controller import OwnerProductController

from PySide6.QtCore import QDate, QEvent, QTime, QTimer, Qt, QSize
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
from PySide6.QtWidgets import (
	QApplication,
	QDialog,
	QFrame,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QMessageBox,
	QPushButton,
	QScrollArea,
	QSizePolicy,
	QStackedWidget,
	QFormLayout,
	QVBoxLayout,
	QWidget,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
PRODUCT_ICON_PATH = os.path.join(BASE_DIR, "assets", "lpg_product_icon.png")

TEAL = "#1A7A6E"
TEAL_DARK = "#145F55"
TEAL_MID = "#2A8C80"
TEAL_LIGHT = "#7FC7BE"
TEAL_PALE = "#e8f5f3"
WHITE = "#ffffff"
GRAY_1 = "#f4f5f4"
GRAY_2 = "#e6eae9"
GRAY_3 = "#c4ccc9"
GRAY_4 = "#7a8a87"
GRAY_5 = "#3a4a47"

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
	for font_name in fonts:
		path = os.path.join(FONTS_DIR, font_name)
		if os.path.exists(path):
			font_id = QFontDatabase.addApplicationFont(path)
			if font_id != -1:
				families = QFontDatabase.applicationFontFamilies(font_id)
				if families:
					if font_name.startswith("PlayfairDisplay"):
						PLAYFAIR_FAMILY = families[0]
					elif font_name == "Inter_18pt-Regular.ttf":
						INTER_FAMILY = families[0]


def playfair(size, weight=QFont.Normal):
	font = QFont(PLAYFAIR_FAMILY, size)
	font.setWeight(weight)
	return font


def inter(size, weight=QFont.Normal):
	font = QFont(INTER_FAMILY, size)
	font.setWeight(weight)
	return font


class ProductEditorDialog(QDialog):
	def __init__(self, parent=None, product=None):
		super().__init__(parent)
		self._product = product or {}
		self._drag_active = False
		self._drag_offset = None
		self.setWindowTitle("Product Form")
		self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
		self.setModal(True)
		self.setFixedWidth(500)
		self.setStyleSheet(
			f"""
			QDialog {{
				background: {WHITE};
			}}
			QLineEdit {{
				background: {WHITE};
				border: 1px solid #d6e2df;
				border-radius: 8px;
				padding: 9px 11px;
				color: {GRAY_5};
			}}
			QLineEdit:focus {{
				border-color: {TEAL};
				background: {WHITE};
			}}
			QLabel {{
				color: {GRAY_5};
				background: transparent;
			}}
			QPushButton#PrimaryBtn {{
				color: {WHITE};
				background: {TEAL_DARK};
				border: 1px solid {TEAL_DARK};
				border-radius: 8px;
				padding: 9px 16px;
			}}
			QPushButton#PrimaryBtn:hover {{
				background: {TEAL};
				border-color: {TEAL};
			}}
			QPushButton#GhostBtn {{
				color: {GRAY_5};
				background: {WHITE};
				border: 1px solid #d6dddb;
				border-radius: 8px;
				padding: 9px 16px;
			}}
			QPushButton#GhostBtn:hover {{
				background: #f3f6f5;
			}}
		"""
		)

		root = QVBoxLayout(self)
		root.setContentsMargins(24, 22, 24, 20)
		root.setSpacing(14)

		header = QWidget()
		header.setStyleSheet("background:transparent;border:none;")
		header.setCursor(Qt.SizeAllCursor)
		header.installEventFilter(self)
		header_lay = QVBoxLayout(header)
		header_lay.setContentsMargins(0, 0, 0, 0)
		header_lay.setSpacing(4)

		title = QLabel("{0} Product".format("Edit" if self._product else "Add"))
		title.setFont(playfair(20, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
		title.installEventFilter(self)

		subtitle = QLabel("Fill out the product profile and pricing details.")
		subtitle.setWordWrap(True)
		subtitle.setFont(inter(10))
		subtitle.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
		subtitle.installEventFilter(self)

		header_lay.addWidget(title)
		header_lay.addWidget(subtitle)
		self._drag_widgets = (header, title, subtitle)
		root.addWidget(header)

		form = QFormLayout()
		form.setVerticalSpacing(10)
		form.setHorizontalSpacing(12)
		form.setContentsMargins(0, 8, 0, 4)
		form.setLabelAlignment(Qt.AlignLeft)

		self.name_edit = QLineEdit(self._product.get("name", ""))
		self.name_edit.setPlaceholderText("Product name")
		self.name_edit.setFont(inter(11))

		self.size_edit = QLineEdit(self._product.get("cylinder_size", self._infer_size(self._product.get("name", ""))))
		self.size_edit.setPlaceholderText("e.g. 11kg, 22kg, 50kg")
		self.size_edit.setFont(inter(11))

		self.refill_edit = QLineEdit(f"{float(self._product.get('refill_price', 0) or 0):.2f}")
		self.refill_edit.setPlaceholderText("e.g. 950.00")
		self.refill_edit.setFont(inter(11))

		self.new_tank_edit = QLineEdit(f"{float(self._product.get('new_tank_price', 0) or 0):.2f}")
		self.new_tank_edit.setPlaceholderText("e.g. 3200.00")
		self.new_tank_edit.setFont(inter(11))

		name_lbl = QLabel("Product Name")
		name_lbl.setFont(inter(10, QFont.DemiBold))
		size_lbl = QLabel("Cylinder Size")
		size_lbl.setFont(inter(10, QFont.DemiBold))
		refill_lbl = QLabel("Refill Price")
		refill_lbl.setFont(inter(10, QFont.DemiBold))
		new_tank_lbl = QLabel("New Tank Price")
		new_tank_lbl.setFont(inter(10, QFont.DemiBold))

		form.addRow(name_lbl, self.name_edit)
		form.addRow(size_lbl, self.size_edit)
		form.addRow(refill_lbl, self.refill_edit)
		form.addRow(new_tank_lbl, self.new_tank_edit)
		root.addLayout(form)

		actions = QHBoxLayout()
		actions.setContentsMargins(0, 2, 0, 0)
		actions.setSpacing(10)
		actions.addStretch()

		cancel_btn = QPushButton("Cancel")
		cancel_btn.setObjectName("GhostBtn")
		cancel_btn.setFont(inter(10, QFont.Medium))
		cancel_btn.clicked.connect(self.reject)

		save_btn = QPushButton("Save Product")
		save_btn.setObjectName("PrimaryBtn")
		save_btn.setFont(inter(10, QFont.Medium))
		save_btn.clicked.connect(self.accept)

		actions.addWidget(cancel_btn)
		actions.addWidget(save_btn)
		root.addLayout(actions)

	def product_data(self):
		refill_price = self._parse_price(self.refill_edit.text())
		new_tank_price = self._parse_price(self.new_tank_edit.text())
		return {
			"id": self._product.get("id"),
			"name": self.name_edit.text().strip(),
			"cylinder_size": self.size_edit.text().strip(),
			"refill_price": refill_price,
			"new_tank_price": new_tank_price,
		}

	def accept(self):
		if not self.name_edit.text().strip():
			QMessageBox.warning(self, "Missing Data", "Product name is required.")
			return
		if not self.size_edit.text().strip():
			QMessageBox.warning(self, "Missing Data", "Cylinder size is required.")
			return
		try:
			self._parse_price(self.refill_edit.text())
		except ValueError:
			QMessageBox.warning(self, "Invalid Data", "Refill price must be a valid number.")
			return
		try:
			self._parse_price(self.new_tank_edit.text())
		except ValueError:
			QMessageBox.warning(self, "Invalid Data", "New tank price must be a valid number.")
			return
		super().accept()

	def _parse_price(self, text):
		value = str(text).strip().replace("PHP", "").replace("Php", "").replace(",", "")
		if not value:
			raise ValueError("empty price")
		return float(value)

	def _infer_size(self, name):
		lowered = str(name).lower()
		for kg in ["50kg", "22kg", "11kg"]:
			if kg in lowered:
				return kg.upper()
		return ""

	def eventFilter(self, obj, event):
		if obj is not None and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
			if obj in self._drag_widgets:
				self._drag_active = True
				self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
				return True
		if obj is not None and event.type() == QEvent.MouseMove and self._drag_active:
			if event.buttons() & Qt.LeftButton:
				self.move(event.globalPosition().toPoint() - self._drag_offset)
				return True
		if obj is not None and event.type() == QEvent.MouseButtonRelease and self._drag_active:
			self._drag_active = False
			self._drag_offset = None
			return True
		return super().eventFilter(obj, event)


class OwnerProductCard(QFrame):
	def __init__(self, product, on_edit, on_delete=None, parent=None):
		super().__init__(parent)
		self._product = product
		self._on_edit = on_edit
		self._on_delete = on_delete
		self.setMinimumHeight(350)
		self.setFixedWidth(290)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.setStyleSheet(
			f"""
			QFrame {{
				background: {WHITE};
				border: 1px solid {GRAY_2};
				border-radius: 10px;
			}}
		"""
		)

		lay = QVBoxLayout(self)
		lay.setContentsMargins(14, 14, 14, 14)
		lay.setSpacing(10)

		top_row = QHBoxLayout()
		top_row.setContentsMargins(0, 0, 0, 0)
		top_row.setSpacing(8)

		kg_source = product.get("cylinder_size") or product.get("name", "")
		kg_chip = QLabel(self._kg_badge_text(str(kg_source)))
		kg_chip.setFont(inter(9, QFont.DemiBold))
		kg_chip.setStyleSheet(
			f"color:{TEAL_DARK};background:{TEAL_PALE};border:1px solid #cde6e1;border-radius:11px;padding:3px 8px;"
		)

		top_row.addWidget(kg_chip)
		top_row.addStretch()
		lay.addLayout(top_row)

		icon_box = QFrame()
		icon_box.setFixedHeight(150)
		icon_box.setStyleSheet(
			f"""
			QFrame {{
				background: #f6f8f7;
				border: 1px solid #d7dedd;
				border-radius: 8px;
			}}
			"""
		)
		icon_lay = QVBoxLayout(icon_box)
		icon_lay.setContentsMargins(0, 0, 0, 0)
		icon_lay.setSpacing(0)

		icon_lbl = QLabel()
		icon_lbl.setAlignment(Qt.AlignCenter)
		icon_lbl.setStyleSheet("background:transparent;border:none;")

		icon_pixmap = QPixmap(PRODUCT_ICON_PATH)
		if not icon_pixmap.isNull():
			icon_lbl.setPixmap(icon_pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
		else:
			icon_lbl.setText("LPG")
			icon_lbl.setFont(inter(30, QFont.Bold))
			icon_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;letter-spacing:2px;")
		icon_lay.addWidget(icon_lbl)

		name_lbl = QLabel(str(product.get("name", "")))
		name_lbl.setAlignment(Qt.AlignCenter)
		name_lbl.setWordWrap(True)
		name_lbl.setFont(inter(16, QFont.Bold))
		name_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		price_row = QHBoxLayout()
		price_row.setContentsMargins(0, 0, 0, 0)
		price_row.setSpacing(8)

		refill_box = self._price_box("Refill", self._format_price(product.get("refill_price")))
		new_tank_box = self._price_box("New Tank", self._format_price(product.get("new_tank_price")))

		price_row.addWidget(refill_box)
		price_row.addWidget(new_tank_box)

		# Actions row (edit + delete)
		btn_row = QHBoxLayout()
		btn_row.setContentsMargins(0, 0, 0, 0)
		btn_row.setSpacing(10)

		edit_btn = QPushButton("Edit")
		edit_btn.setCursor(Qt.PointingHandCursor)
		edit_btn.setFont(inter(10, QFont.Medium))
		edit_btn.clicked.connect(lambda: self._on_edit(self._product))
		edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		edit_btn.setStyleSheet(
			f"""
			QPushButton {{
				color: {TEAL_DARK};
				background: {TEAL_PALE};
				border: 1px solid {TEAL_LIGHT};
				border-radius: 6px;
				padding: 9px 14px;
			}}
			QPushButton:hover {{
				background: {TEAL_LIGHT};
				color: {WHITE};
			}}
		"""
		)

		delete_btn = QPushButton("Delete")
		delete_btn.setCursor(Qt.PointingHandCursor)
		delete_btn.setFont(inter(10, QFont.Medium))
		delete_btn.clicked.connect(lambda: self._on_delete(self._product) if self._on_delete else None)
		delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		delete_btn.setStyleSheet(
			"""
			QPushButton {
				color: #8a1a1a;
				background: #fdeaea;
				border: 1px solid #f2c7c7;
				border-radius: 6px;
				padding: 9px 14px;
			}
			QPushButton:hover {
				background: #f6cfcf;
				color: #ffffff;
				border-color: #e3a5a5;
			}
			"""
		)

		btn_row.addWidget(edit_btn, 1)
		btn_row.addWidget(delete_btn, 1)

		lay.addWidget(icon_box)
		lay.addWidget(name_lbl)
		lay.addLayout(price_row)
		lay.addLayout(btn_row)
		lay.addStretch(1)

	def _price_box(self, label, value):
		box = QFrame()
		box.setStyleSheet(
			f"""
			QFrame {{
				background:{WHITE};
				border:1px solid #d9dfdd;
				border-radius:7px;
			}}
			"""
		)
		lay = QVBoxLayout(box)
		lay.setContentsMargins(8, 6, 8, 6)
		lay.setSpacing(2)

		lbl = QLabel(label.upper())
		lbl.setFont(inter(8, QFont.DemiBold))
		lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;letter-spacing:1px;")

		val = QLabel(value)
		val.setFont(inter(10, QFont.DemiBold))
		val.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

		lay.addWidget(lbl)
		lay.addWidget(val)
		return box

	def _kg_badge_text(self, text):
		lowered = str(text or "").lower()
		for kg in ["50kg", "22kg", "11kg"]:
			if kg in lowered:
				return kg.upper()
		# Fall back to exact cylinder_size if provided (e.g., "Superkalan", "5kg mini")
		if lowered:
			return str(text).upper()
		return "LPG"

	def _format_price(self, value):
		try:
			return f"Php {float(value):,.2f}"
		except (TypeError, ValueError):
			return "Php 0.00"


class OwnerProductsView(QWidget):
	def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False, controller=None):
		super().__init__(parent)
		self._show_topbar = show_topbar
		self._topbar_controls_only = topbar_controls_only
		self._all_products = []
		self._filtered_products = []
		self._controller = None

		load_fonts()
		self.setStyleSheet(f"background:{GRAY_1};")
		self._build_ui()

		if controller is not None:
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
		scroll.setStyleSheet(owner_scrollbar_qss())

		self._content = QWidget()
		self._content.setStyleSheet("background:transparent;")
		c_lay = QVBoxLayout(self._content)
		c_lay.setContentsMargins(28, 24, 28, 28)
		c_lay.setSpacing(0)

		title_row = QHBoxLayout()
		title_row.setSpacing(0)

		left = QVBoxLayout()
		left.setSpacing(0)

		sub = QLabel("PRODUCT CATALOG")
		sub.setFont(inter(10, QFont.DemiBold))
		sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

		title = QLabel("LPG Products")
		title.setFont(playfair(28, QFont.Medium))
		title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		page_sub = QLabel("Manage the owner product catalog with add and edit controls.")
		page_sub.setFont(inter(12))
		page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

		left.addWidget(sub)
		left.addWidget(title)
		left.addWidget(page_sub)

		self._add_btn = QPushButton("+ Add Product")
		self._add_btn.setCursor(Qt.PointingHandCursor)
		self._add_btn.setFont(inter(11, QFont.Medium))
		self._add_btn.clicked.connect(self._add_product)
		self._add_btn.setStyleSheet(
			f"""
			QPushButton {{
				color: {WHITE};
				background: {TEAL_DARK};
				border: 1px solid {TEAL_DARK};
				border-radius: 6px;
				padding: 10px 25px;
			}}
			QPushButton:hover {{
				background: {TEAL};
				border-color: {TEAL};
			}}
			"""
		)

		self._search = QLineEdit()
		self._search.setPlaceholderText("Search products...")
		self._search.setFont(inter(12))
		self._search.setFixedHeight(36)
		self._search.setMinimumWidth(280)
		self._search.setMaximumWidth(460)
		self._search.setStyleSheet(
			f"""
			QLineEdit{{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {GRAY_2};border-radius:4px;
				padding:0 10px;
			}}
			QLineEdit:focus{{border-color:{TEAL};}}
			"""
		)
		self._search.textChanged.connect(self._on_search)

		rule = QFrame()
		rule.setFrameShape(QFrame.HLine)
		rule.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin-bottom:6px;margin-left:24px;")

		title_row.addLayout(left)
		title_row.addWidget(rule, 1, Qt.AlignBottom)
		title_row.addWidget(self._search, 0, Qt.AlignRight | Qt.AlignTop)

		controls_row = QHBoxLayout()
		controls_row.setContentsMargins(0, 14, 0, 0)
		controls_row.setSpacing(17)
		controls_row.addWidget(self._add_btn, 10, Qt.AlignLeft)
		controls_row.addStretch()

		self._count_lbl = QLabel("0 products")
		self._count_lbl.setFont(inter(11))
		self._count_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
		self._count_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		self._count_lbl.setMinimumWidth(140)
		controls_row.addWidget(self._count_lbl, 0, Qt.AlignRight)

		c_lay.addLayout(title_row)
		c_lay.addLayout(controls_row)
		c_lay.addSpacing(18)

		self._grid_wrap = QWidget()
		self._grid_wrap.setStyleSheet("background:transparent;border:none;")
		self._grid = QGridLayout(self._grid_wrap)
		self._grid.setContentsMargins(0, 0, 0, 0)
		self._grid.setHorizontalSpacing(14)
		self._grid.setVerticalSpacing(14)
		self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

		self._empty_state = QWidget()
		es_lay = QVBoxLayout(self._empty_state)
		es_lay.setContentsMargins(0, 40, 0, 40)
		es_lay.setAlignment(Qt.AlignCenter)

		es_title = QLabel("No products available")
		es_title.setFont(playfair(16, QFont.Medium))
		es_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		es_sub = QLabel("Products created by the owner will appear here.")
		es_sub.setFont(inter(12))
		es_sub.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

		es_lay.addWidget(es_title)
		es_lay.addWidget(es_sub)

		self._list_stack = QStackedWidget()
		self._list_stack.addWidget(self._grid_wrap)
		self._list_stack.addWidget(self._empty_state)
		c_lay.addWidget(self._list_stack)

		scroll.setWidget(self._content)
		root.addWidget(scroll)

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
			breadcrumb = QLabel("PRODUCT MANAGEMENT")
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

	def load_products(self, products):
		self._all_products = [dict(product) for product in products]
		self._apply_filter(self._search.text() if hasattr(self, "_search") else "")

	def _on_search(self, text):
		if self._controller:
			self._controller.search_products((text or "").strip())
		else:
			self._apply_filter(text)

	def _apply_filter(self, text):
		query = (text or "").strip().lower()
		if not query:
			self._filtered_products = list(self._all_products)
		else:
			self._filtered_products = [
				product for product in self._all_products if query in str(product.get("name", "")).lower()
			]

		self._render_grid()
		self._count_lbl.setText(f"{len(self._filtered_products)} products")
		self._list_stack.setCurrentWidget(self._grid_wrap if self._filtered_products else self._empty_state)

	def _render_grid(self):
		self._clear_layout(self._grid)

		if not self._filtered_products:
			return

		columns = 4
		for index, product in enumerate(self._filtered_products):
			row = index // columns
			col = index % columns
			self._grid.addWidget(OwnerProductCard(product, self._edit_product, self._delete_product), row, col)

		self._grid.setColumnStretch(columns, 1)

	def resizeEvent(self, event):
		super().resizeEvent(event)
		self._render_grid()

	def _clear_layout(self, layout):
		while layout.count():
			item = layout.takeAt(0)
			widget = item.widget()
			child_layout = item.layout()
			if widget is not None:
				widget.deleteLater()
			elif child_layout is not None:
				self._clear_layout(child_layout)

	def show_error(self, title, message):
		QMessageBox.warning(self, title, str(message))

	def bind_controller(self, controller, request_initial=False):
		self._controller = controller
		if hasattr(controller, "attach_view"):
			controller.attach_view(self)
		if request_initial and hasattr(controller, "refresh_products"):
			controller.refresh_products()
		return controller

	def _add_product(self):
		dialog = ProductEditorDialog(self)
		if dialog.exec() == QDialog.Accepted:
			new_product = dialog.product_data()
			if self._controller:
				self._controller.add_product(new_product)
			else:
				return new_product

	def _edit_product(self, product):
		current = next((item for item in self._all_products if item.get("id") == product.get("id")), None)
		if current is None:
			return

		dialog = ProductEditorDialog(self, current)
		if dialog.exec() == QDialog.Accepted:
			updated = dialog.product_data()
			if self._controller:
				self._controller.update_product(updated)
			else:
				return updated

	def _delete_product(self, product):
		# Custom, draggable, frameless confirmation dialog with explicit sizing and hovers.
		class _DeleteDialog(QDialog):
			def __init__(self, parent=None):
				super().__init__(parent)
				self._drag_pos = None
				self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
				self.setFixedSize(360, 160)  # sized just to fit the content
				self.setStyleSheet(
					f"""
					QDialog {{
						background: {WHITE};
						border: 1px solid {GRAY_2};
						border-radius: 12px;
					}}
					QLabel#Title {{
						color: {TEAL_DARK};
						font: 13pt "{INTER_FAMILY}";
						background: transparent;
					}}
					QLabel#Body {{
						color: {GRAY_5};
						font: 11pt "{INTER_FAMILY}";
						background: transparent;
					}}
					QPushButton {{
						min-width: 120px;
						padding: 9px 16px;
						border-radius: 7px;
						font: 10.5pt "{INTER_FAMILY}";
						border: none;
					}}
					QPushButton#CancelBtn {{
						color: {TEAL_DARK};
						background: {TEAL_PALE};
					}}
					QPushButton#CancelBtn:hover {{
						background: {TEAL_LIGHT};
						color: {WHITE};
					}}
					QPushButton#CancelBtn:pressed {{
						background: {TEAL_DARK};
						color: {WHITE};
					}}
					QPushButton#DeleteBtn {{
						color: #8a1a1a;
						background: #fdeaea;
					}}
					QPushButton#DeleteBtn:hover {{
						background: #f6cfcf;
						color: #8a1a1a;
					}}
					QPushButton#DeleteBtn:pressed {{
						background: #e3a5a5;
						color: #ffffff;
					}}
					"""
				)

				root = QVBoxLayout(self)
				root.setContentsMargins(20, 18, 20, 16)
				root.setSpacing(14)

				self.title_lbl = QLabel(f"⚠️  Delete '{product.get('name', 'this product')}'?")
				self.title_lbl.setObjectName("Title")

				self.body_lbl = QLabel("This action cannot be undone. Related delivery data will remain.")
				self.body_lbl.setWordWrap(True)
				self.body_lbl.setObjectName("Body")

				root.addWidget(self.title_lbl)
				root.addWidget(self.body_lbl)
				root.addStretch()

				btn_row = QHBoxLayout()
				btn_row.setContentsMargins(0, 0, 0, 0)
				btn_row.setSpacing(10)

				cancel_btn = QPushButton("Cancel")
				cancel_btn.setObjectName("CancelBtn")
				cancel_btn.clicked.connect(self.reject)

				delete_btn = QPushButton("Delete")
				delete_btn.setObjectName("DeleteBtn")
				delete_btn.clicked.connect(self.accept)

				btn_row.addWidget(cancel_btn, 1, Qt.AlignLeft)
				btn_row.addStretch()
				btn_row.addWidget(delete_btn, 1, Qt.AlignRight)

				root.addLayout(btn_row)

			def mousePressEvent(self, event):
				if event.button() == Qt.LeftButton:
					self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
				super().mousePressEvent(event)

			def mouseMoveEvent(self, event):
				if self._drag_pos and event.buttons() & Qt.LeftButton:
					self.move(event.globalPosition().toPoint() - self._drag_pos)
				super().mouseMoveEvent(event)

		box = _DeleteDialog(self)
		if box.exec() == QDialog.Accepted:
			if self._controller:
				self._controller.delete_product(product)
			else:
				# fallback local removal
				self._all_products = [p for p in self._all_products if p.get("id") != product.get("id")]
				self._apply_filter(self._search.text())


def main():
	app = QApplication(sys.argv)
	load_fonts()
	app.setFont(inter(11))
	win = OwnerProductsView(show_topbar=True)
	ctrl = OwnerProductController().attach_view(win)
	win.bind_controller(ctrl, request_initial=True)
	win.resize(1320, 840)
	win.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
