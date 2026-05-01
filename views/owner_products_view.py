import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from views.admin_dashboard_view import owner_scrollbar_qss

from PySide6.QtCore import QDate, QEvent, QTime, QTimer, Qt, QSize, QPoint
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPixmap
from PySide6.QtWidgets import (
	QApplication,
	QFrame,
	QGraphicsDropShadowEffect,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QPushButton,
	QScrollArea,
	QSizePolicy,
	QStackedWidget,
	QVBoxLayout,
	QWidget,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
PRODUCT_ICON_PATH = os.path.join(BASE_DIR, "assets", "lpg_product_icon.png")
NO_PRODUCTS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

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
INK = "#173c37"
CARD_SURFACE = "#fbfefd"
CARD_BORDER = "#d5e4e1"
SURFACE_SOFT = "#f6fbfa"
MINT_SOFT = "#dff3ef"
AMBER = "#b87913"
AMBER_SOFT = "#fff4dc"
DANGER = "#b64040"
DANGER_SOFT = "#fdecec"
PRODUCT_CARD_WIDTH = 300

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


# ── Reusable field builder (mirrors customer_view.make_field) ─────────────────
def _make_field(label_text, placeholder, required=True):
	grp = QWidget()
	grp.setStyleSheet("background:transparent;border:none;")
	g_lay = QVBoxLayout(grp)
	g_lay.setContentsMargins(0, 0, 0, 0)
	g_lay.setSpacing(8)

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

	inp = QLineEdit()
	inp.setPlaceholderText(placeholder)
	inp.setFont(inter(12))
	inp.setFixedHeight(36)
	inp.setStyleSheet(f"""
		QLineEdit{{
			color:{GRAY_5};background:{WHITE};
			border:1px solid {CARD_BORDER};border-radius:7px;
			padding:0 11px;
		}}
		QLineEdit:focus{{border-color:{TEAL};}}
		QLineEdit[error="true"]{{
			border-color:{DANGER};background:#fff7f7;
		}}
		QLineEdit[error="true"]:focus{{border-color:{DANGER};}}
	""")

	err = QLabel("")
	err.setFont(inter(9))
	err.setStyleSheet("color:#cf4d4d;background:transparent;border:none;")
	err.setContentsMargins(2, 2, 0, 0)
	err.setWordWrap(True)
	err.hide()

	g_lay.addWidget(inp)
	g_lay.addWidget(err)
	return grp, inp, err


# ── Product form modal overlay ────────────────────────────────────────────────
class ProductFormModal(QWidget):
	"""
	Drop-in overlay modal for Add / Edit product.
	Mirrors CustomerFormModal's overlay pattern exactly.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet("background:rgba(10,35,32,130);")
		self._mode = "add"
		self._submit_callback = None
		self._product = {}
		self._drag_active = False
		self._drag_offset = QPoint()
		self.hide()

		# ── Card ──────────────────────────────────────────────────────────────
		self._card = QFrame(self)
		self._card.setObjectName("productFormCard")
		self._card.setFixedWidth(540)
		self._card.setStyleSheet(f"""
			QFrame#productFormCard{{
				background:{CARD_SURFACE};
				border:1px solid {CARD_BORDER};
				border-radius:10px;
			}}
		""")
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(46)
		shadow.setOffset(0, 14)
		shadow.setColor(QColor(0, 0, 0, 70))
		self._card.setGraphicsEffect(shadow)

		card_lay = QVBoxLayout(self._card)
		card_lay.setContentsMargins(0, 0, 0, 0)
		card_lay.setSpacing(0)

		# ── Header ────────────────────────────────────────────────────────────
		header = QWidget()
		header.setStyleSheet(
			f"background:{TEAL_DARK};border:none;"
			"border-top-left-radius:10px;border-top-right-radius:10px;"
		)
		h_lay = QVBoxLayout(header)
		h_lay.setContentsMargins(24, 18, 24, 16)
		h_lay.setSpacing(3)

		self._modal_title = QLabel("Add Product")
		self._modal_title.setFont(playfair(16, QFont.DemiBold))
		self._modal_title.setStyleSheet(f"color:{WHITE};background:transparent;border:none;")

		self._modal_subtitle = QLabel("Fill in the product details and pricing information.")
		self._modal_subtitle.setFont(inter(11))
		self._modal_subtitle.setStyleSheet("color:#bfe7e1;background:transparent;border:none;")

		h_lay.addWidget(self._modal_title)
		h_lay.addWidget(self._modal_subtitle)
		card_lay.addWidget(header)

		# ── Body ──────────────────────────────────────────────────────────────
		body = QWidget()
		body.setStyleSheet("background:transparent;border:none;")
		b_lay = QVBoxLayout(body)
		b_lay.setContentsMargins(24, 22, 24, 22)
		b_lay.setSpacing(14)

		f1, self.inp_name, self.err_name = _make_field("Product Name", "e.g. Petron Gasul 11kg")
		f2, self.inp_size, self.err_size = _make_field("Cylinder Size", "e.g. 11kg, 22kg, 50kg")
		f3, self.inp_refill, self.err_refill = _make_field("Refill Price", "e.g. 950.00")
		f4, self.inp_new_tank, self.err_new_tank = _make_field("New Tank Price", "e.g. 3200.00")

		# Clear error on typing
		self.inp_name.textChanged.connect(lambda _: self._clear_field_error(self.inp_name, self.err_name))
		self.inp_size.textChanged.connect(lambda _: self._clear_field_error(self.inp_size, self.err_size))
		self.inp_refill.textChanged.connect(lambda _: self._clear_field_error(self.inp_refill, self.err_refill))
		self.inp_new_tank.textChanged.connect(lambda _: self._clear_field_error(self.inp_new_tank, self.err_new_tank))

		for f in [f1, f2, f3, f4]:
			b_lay.addWidget(f)

		self._form_err = QLabel("")
		self._form_err.setFont(inter(10))
		self._form_err.setStyleSheet(f"color:{DANGER};background:transparent;border:none;")
		self._form_err.setWordWrap(True)
		self._form_err.hide()
		b_lay.addWidget(self._form_err)

		card_lay.addWidget(body)

		# ── Footer ────────────────────────────────────────────────────────────
		footer = QWidget()
		footer.setStyleSheet(f"background:{SURFACE_SOFT};border:none;border-top:1px solid {CARD_BORDER};")
		f_lay = QHBoxLayout(footer)
		f_lay.setContentsMargins(24, 14, 24, 18)
		f_lay.setSpacing(10)
		f_lay.addStretch()

		self._cancel_btn = QPushButton("Cancel")
		self._cancel_btn.setCursor(Qt.PointingHandCursor)
		self._cancel_btn.setFont(inter(12, QFont.Medium))
		self._cancel_btn.setFixedHeight(36)
		self._cancel_btn.setStyleSheet(f"""
			QPushButton{{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {CARD_BORDER};border-radius:7px;padding:0 18px;
			}}
			QPushButton:hover{{border-color:{TEAL};color:{TEAL_DARK};background:{TEAL_PALE};}}
		""")
		self._cancel_btn.clicked.connect(self.hide)

		self._save_btn = QPushButton("Save Product")
		self._save_btn.setCursor(Qt.PointingHandCursor)
		self._save_btn.setFont(inter(12, QFont.Medium))
		self._save_btn.setFixedHeight(36)
		self._save_btn.setStyleSheet(f"""
			QPushButton{{
				color:{WHITE};background:{TEAL};
				border:1px solid {TEAL};border-radius:7px;padding:0 18px;
			}}
			QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
		""")
		self._save_btn.clicked.connect(self._on_save)

		f_lay.addWidget(self._cancel_btn)
		f_lay.addWidget(self._save_btn)
		card_lay.addWidget(footer)

	# ── Public API ────────────────────────────────────────────────────────────
	def open_add(self, callback=None):
		self._mode = "add"
		self._submit_callback = callback
		self._product = {}
		self._modal_title.setText("Add Product")
		self._modal_subtitle.setText("Fill in the product details and pricing information.")
		self._save_btn.setText("Save Product")
		self._clear_fields()
		self._clear_all_errors()
		self._show_centered()

	def open_edit(self, product, callback=None):
		self._mode = "edit"
		self._submit_callback = callback
		self._product = dict(product)
		self._modal_title.setText("Edit Product")
		self._modal_subtitle.setText("Update the product details and pricing information.")
		self._save_btn.setText("Save Changes")
		self._clear_all_errors()

		self.inp_name.setText(product.get("name", ""))
		self.inp_size.setText(product.get("cylinder_size", self._infer_size(product.get("name", ""))))
		self.inp_refill.setText(f"{float(product.get('refill_price', 0) or 0):.2f}")
		self.inp_new_tank.setText(f"{float(product.get('new_tank_price', 0) or 0):.2f}")
		self._show_centered()

	def set_submit_callback(self, callback):
		"""Legacy compat — prefer passing callback to open_add / open_edit."""
		self._submit_callback = callback

	# ── Layout helpers ────────────────────────────────────────────────────────
	def _show_centered(self):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._refresh_card_geometry()
		self.show()
		self.raise_()

	def _refresh_card_geometry(self):
		if not self._card:
			return
		self._card.layout().activate()
		self._card.adjustSize()
		x = max(0, (self.width() - self._card.width()) // 2)
		y = max(0, (self.height() - self._card.height()) // 2)
		self._card.move(x, y)

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		if self._card:
			self._refresh_card_geometry()
		super().resizeEvent(event)

	# ── Drag support (header area) ────────────────────────────────────────────
	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self.hide()
			return
		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= 72:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active:
			pos = event.position().toPoint()
			new_pos = pos - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			self._card.move(
				max(0, min(new_pos.x(), max_x)),
				max(0, min(new_pos.y(), max_y)),
			)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self._drag_active = False
		super().mouseReleaseEvent(event)

	# ── Validation & submit ───────────────────────────────────────────────────
	def _on_save(self):
		self._clear_all_errors()
		errors = {}

		if not self.inp_name.text().strip():
			errors["name"] = "Product name is required."
		if not self.inp_size.text().strip():
			errors["cylinder_size"] = "Cylinder size is required."
		try:
			self._parse_price(self.inp_refill.text())
		except ValueError:
			errors["refill_price"] = "Refill price must be a valid number."
		try:
			self._parse_price(self.inp_new_tank.text())
		except ValueError:
			errors["new_tank_price"] = "New tank price must be a valid number."

		if errors:
			self._show_errors(errors)
			return

		data = {
			"id": self._product.get("id"),
			"name": self.inp_name.text().strip(),
			"cylinder_size": self.inp_size.text().strip(),
			"refill_price": self._parse_price(self.inp_refill.text()),
			"new_tank_price": self._parse_price(self.inp_new_tank.text()),
		}

		if self._submit_callback is not None:
			ok, response = self._submit_callback(data)
			if not ok:
				self._show_errors(response or {})
				return

		self.hide()

	def _show_errors(self, errors):
		errors = errors or {}
		self._set_field_error(self.inp_name, self.err_name, errors.get("name"))
		self._set_field_error(self.inp_size, self.err_size, errors.get("cylinder_size"))
		self._set_field_error(self.inp_refill, self.err_refill, errors.get("refill_price"))
		self._set_field_error(self.inp_new_tank, self.err_new_tank, errors.get("new_tank_price"))
		form_err = errors.get("form")
		if form_err:
			self._form_err.setText(str(form_err))
			self._form_err.show()
		else:
			self._form_err.clear()
			self._form_err.hide()
		self._refresh_card_geometry()

	def _set_field_error(self, editor, error_label, message):
		has_error = bool(message)
		editor.setProperty("error", has_error)
		editor.style().unpolish(editor)
		editor.style().polish(editor)
		if has_error:
			error_label.setText(str(message))
			error_label.show()
		else:
			error_label.clear()
			error_label.hide()
		self._refresh_card_geometry()

	def _clear_field_error(self, editor, error_label):
		self._set_field_error(editor, error_label, "")

	def _clear_all_errors(self):
		for editor, err in [
			(self.inp_name, self.err_name),
			(self.inp_size, self.err_size),
			(self.inp_refill, self.err_refill),
			(self.inp_new_tank, self.err_new_tank),
		]:
			self._clear_field_error(editor, err)
		self._form_err.clear()
		self._form_err.hide()
		self._refresh_card_geometry()

	def _clear_fields(self):
		self.inp_name.clear()
		self.inp_size.clear()
		self.inp_refill.setText("0.00")
		self.inp_new_tank.setText("0.00")

	def reset_state(self):
		self._mode = "add"
		self._submit_callback = None
		self._product = {}
		self._drag_active = False
		self._drag_offset = QPoint()
		self._modal_title.setText("Add Product")
		self._modal_subtitle.setText("Fill in the product details and pricing information.")
		self._save_btn.setText("Save Product")
		self._clear_fields()
		self._clear_all_errors()
		self.hide()

	# ── Helpers ───────────────────────────────────────────────────────────────
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


# ── Product card ──────────────────────────────────────────────────────────────
class OwnerProductCard(QFrame):
	def __init__(
		self,
		product,
		on_edit=None,
		on_archive=None,
		on_delete=None,
		on_restore=None,
		archived=False,
		parent=None,
	):
		super().__init__(parent)
		self._product = product
		self._on_edit = on_edit
		self._on_archive = on_archive
		self._on_delete = on_delete
		self._on_restore = on_restore
		self._archived = archived
		self.setMinimumHeight(386)
		self.setFixedWidth(PRODUCT_CARD_WIDTH)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.setStyleSheet(
			f"""
			QFrame {{
				background: {CARD_SURFACE};
				border: 1px solid {CARD_BORDER};
				border-radius: 8px;
			}}
		"""
		)

		self._shadow = QGraphicsDropShadowEffect(self)
		self._set_hover_shadow(False)
		self.setGraphicsEffect(self._shadow)

		lay = QVBoxLayout(self)
		lay.setContentsMargins(16, 16, 16, 16)
		lay.setSpacing(11)

		top_row = QHBoxLayout()
		top_row.setContentsMargins(0, 0, 0, 0)
		top_row.setSpacing(8)

		kg_source = product.get("cylinder_size") or product.get("name", "")
		kg_chip = QLabel(self._kg_badge_text(str(kg_source)))
		kg_chip.setFont(inter(9, QFont.DemiBold))
		kg_chip.setStyleSheet(
			f"color:{TEAL_DARK};background:{MINT_SOFT};border:1px solid #b9ddd6;border-radius:11px;padding:3px 9px;"
		)

		top_row.addWidget(kg_chip)
		top_row.addStretch()
		if self._archived:
			archived_chip = QLabel("ARCHIVED")
			archived_chip.setFont(inter(8, QFont.DemiBold))
			archived_chip.setStyleSheet(
				f"color:{GRAY_5};background:{GRAY_1};border:1px solid {GRAY_2};border-radius:10px;padding:3px 8px;"
			)
			top_row.addWidget(archived_chip)
		lay.addLayout(top_row)

		icon_box = QFrame()
		icon_box.setFixedHeight(138)
		icon_box.setStyleSheet(
			f"""
			QFrame {{
				background: {SURFACE_SOFT};
				border: 1px solid #d9e8e5;
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
		name_lbl.setMinimumHeight(44)
		name_lbl.setStyleSheet(f"color:{INK};background:transparent;border:none;")

		price_row = QHBoxLayout()
		price_row.setContentsMargins(0, 0, 0, 0)
		price_row.setSpacing(8)

		refill_box = self._price_box("Refill", self._format_price(product.get("refill_price")))
		new_tank_box = self._price_box("New Tank", self._format_price(product.get("new_tank_price")))

		price_row.addWidget(refill_box, 1)
		price_row.addWidget(new_tank_box, 1)

		metric_row = QHBoxLayout()
		metric_row.setContentsMargins(0, 0, 0, 0)
		metric_row.setSpacing(8)
		metric_row.addWidget(self._metric_chip("Sold", self._as_int(product.get("total_sold"))), 1)
		metric_row.addWidget(self._metric_chip("Deliveries", self._as_int(product.get("total_deliveries"))), 1)

		btn_row = QHBoxLayout()
		btn_row.setContentsMargins(0, 0, 0, 0)
		btn_row.setSpacing(8)

		if self._archived:
			restore_btn = self._make_card_button("Restore", "primary")
			restore_btn.clicked.connect(lambda: self._on_restore(self._product) if self._on_restore else None)
			btn_row.addWidget(restore_btn, 1)

			delete_btn = self._make_card_button("Delete", "danger")
			delete_btn.clicked.connect(lambda: self._on_delete(self._product) if self._on_delete else None)
			btn_row.addWidget(delete_btn, 1)
		else:
			edit_btn = self._make_card_button("Edit", "soft")
			edit_btn.clicked.connect(lambda: self._on_edit(self._product) if self._on_edit else None)

			archive_btn = self._make_card_button("Archive", "warning")
			archive_btn.clicked.connect(lambda: self._on_archive(self._product) if self._on_archive else None)

			delete_btn = self._make_card_button("Delete", "danger")
			delete_btn.clicked.connect(lambda: self._on_delete(self._product) if self._on_delete else None)

			btn_row.addWidget(edit_btn, 1)
			btn_row.addWidget(archive_btn, 1)
			btn_row.addWidget(delete_btn, 1)

		lay.addWidget(icon_box)
		lay.addWidget(name_lbl)
		lay.addLayout(price_row)
		lay.addLayout(metric_row)
		lay.addStretch(1)
		lay.addLayout(btn_row)

	def enterEvent(self, event):
		self._set_hover_shadow(True)
		super().enterEvent(event)

	def leaveEvent(self, event):
		self._set_hover_shadow(False)
		super().leaveEvent(event)

	def _set_hover_shadow(self, hovered):
		if hovered:
			self._shadow.setBlurRadius(30)
			self._shadow.setOffset(0, 12)
			self._shadow.setColor(QColor(20, 57, 52, 48))
		else:
			self._shadow.setBlurRadius(20)
			self._shadow.setOffset(0, 5)
			self._shadow.setColor(QColor(20, 57, 52, 24))

	def _price_box(self, label, value):
		box = QFrame()
		box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		box.setStyleSheet(
			f"""
			QFrame {{
				background:{WHITE};
				border:1px solid #dbe8e5;
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

	def _metric_chip(self, label, value):
		chip = QFrame()
		chip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		chip.setStyleSheet(
			f"""
			QFrame {{
				background:{SURFACE_SOFT};
				border:1px solid #dce8e5;
				border-radius:7px;
			}}
			"""
		)
		lay = QHBoxLayout(chip)
		lay.setContentsMargins(8, 5, 8, 5)
		lay.setSpacing(4)

		lbl = QLabel(label)
		lbl.setFont(inter(9, QFont.Medium))
		lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		val = QLabel(str(value))
		val.setFont(inter(9, QFont.DemiBold))
		val.setAlignment(Qt.AlignRight)
		val.setStyleSheet(f"color:{INK};background:transparent;border:none;")

		lay.addWidget(lbl)
		lay.addStretch()
		lay.addWidget(val)
		return chip

	def _make_card_button(self, text, kind):
		btn = QPushButton(text)
		btn.setCursor(Qt.PointingHandCursor)
		btn.setFont(inter(10, QFont.Medium))
		btn.setFixedHeight(36)
		btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		btn.setStyleSheet(self._button_style(kind))
		return btn

	def _button_style(self, kind):
		if kind == "primary":
			return f"""
				QPushButton {{
					color: {WHITE};
					background: {TEAL};
					border: 1px solid {TEAL};
					border-radius: 7px;
					padding: 0 10px;
				}}
				QPushButton:hover {{
					background: {TEAL_DARK};
					border-color: {TEAL_DARK};
				}}
			"""
		if kind == "warning":
			return f"""
				QPushButton {{
					color: {AMBER};
					background: {AMBER_SOFT};
					border: 1px solid #efd7a7;
					border-radius: 7px;
					padding: 0 8px;
				}}
				QPushButton:hover {{
					background: #f1d69b;
					border-color: #dca94d;
					color: #7a4d08;
				}}
			"""
		if kind == "danger":
			return f"""
				QPushButton {{
					color: {DANGER};
					background: {DANGER_SOFT};
					border: 1px solid #efc4c4;
					border-radius: 7px;
					padding: 0 8px;
				}}
				QPushButton:hover {{
					background: {DANGER};
					border-color: {DANGER};
					color: {WHITE};
				}}
			"""
		return f"""
			QPushButton {{
				color: {TEAL_DARK};
				background: {TEAL_PALE};
				border: 1px solid #badbd5;
				border-radius: 7px;
				padding: 0 10px;
			}}
			QPushButton:hover {{
				background: {TEAL};
				border-color: {TEAL};
				color: {WHITE};
			}}
		"""

	def _as_int(self, value):
		try:
			return int(float(value or 0))
		except (TypeError, ValueError):
			return 0

	def _kg_badge_text(self, text):
		lowered = str(text or "").lower()
		for kg in ["50kg", "22kg", "11kg"]:
			if kg in lowered:
				return kg.upper()
		if lowered:
			return str(text).upper()
		return "LPG"

	def _format_price(self, value):
		try:
			return f"Php {float(value):,.2f}"
		except (TypeError, ValueError):
			return "Php 0.00"


# ── Product action confirmation ──────────────────────────────────────────────
class _ProductActionDialog(QWidget):
	"""Frameless overlay confirmation for archive and permanent delete."""

	def __init__(self, product, parent=None, action="archive"):
		super().__init__(parent)
		self._product = dict(product or {})
		self._action = action
		self.setStyleSheet("background:rgba(10,35,32,130);")
		self._result = False
		self._on_confirm = None
		self._on_close = None
		self._drag_active = False
		self._drag_offset = QPoint()

		self._card = QFrame(self)
		self._card.setObjectName("delCard")
		self._card.setFixedWidth(430)
		self._card.setStyleSheet(f"""
			QFrame#delCard{{
				background:{CARD_SURFACE};
				border:1px solid {CARD_BORDER};
				border-radius:10px;
			}}
			QLabel{{background:transparent;border:none;}}
			QPushButton{{border:none;}}
		""")
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(46)
		shadow.setOffset(0, 14)
		shadow.setColor(QColor(0, 0, 0, 70))
		self._card.setGraphicsEffect(shadow)

		c_lay = QVBoxLayout(self._card)
		c_lay.setContentsMargins(22, 20, 22, 18)
		c_lay.setSpacing(12)

		if self._action == "delete":
			title_text = f"Delete '{product.get('name', 'this product')}' permanently?"
			body_text = "Only products with no delivery history can be deleted. Products with history should be archived."
			button_text = "Delete"
			action_label = "PERMANENT DELETE"
			accent = DANGER
			soft = DANGER_SOFT
			border = "#efc4c4"
		else:
			title_text = f"Archive '{product.get('name', 'this product')}'?"
			body_text = "This product will be hidden from new deliveries. Existing delivery and transaction history will stay intact."
			button_text = "Archive"
			action_label = "ARCHIVE PRODUCT"
			accent = AMBER
			soft = AMBER_SOFT
			border = "#efd7a7"

		badge = QLabel(action_label)
		badge.setFont(inter(8, QFont.DemiBold))
		badge.setStyleSheet(
			f"color:{accent};background:{soft};border:1px solid {border};border-radius:10px;padding:3px 8px;"
		)
		badge.setFixedHeight(22)

		title_lbl = QLabel(title_text)
		title_lbl.setWordWrap(True)
		title_lbl.setFont(playfair(16, QFont.DemiBold))
		title_lbl.setStyleSheet(f"color:{INK};")

		body_lbl = QLabel(body_text)
		body_lbl.setWordWrap(True)
		body_lbl.setFont(inter(11))
		body_lbl.setStyleSheet(f"color:{GRAY_5};")

		c_lay.addWidget(badge, 0, Qt.AlignLeft)
		c_lay.addWidget(title_lbl)
		c_lay.addWidget(body_lbl)
		c_lay.addSpacing(4)

		btn_row = QHBoxLayout()
		btn_row.setSpacing(10)

		cancel_btn = QPushButton("Cancel")
		cancel_btn.setObjectName("CancelBtn")
		cancel_btn.setFont(inter(11, QFont.Medium))
		cancel_btn.setFixedHeight(34)
		cancel_btn.setCursor(Qt.PointingHandCursor)
		cancel_btn.setStyleSheet(f"""
			QPushButton{{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {CARD_BORDER};border-radius:7px;
				min-width:110px;padding:0 16px;
			}}
			QPushButton:hover{{background:{TEAL_PALE};border-color:{TEAL};color:{TEAL_DARK};}}
		""")
		cancel_btn.clicked.connect(self._on_cancel)

		action_btn = QPushButton(button_text)
		action_btn.setObjectName("ActionBtn")
		action_btn.setFont(inter(11, QFont.Medium))
		action_btn.setFixedHeight(34)
		action_btn.setCursor(Qt.PointingHandCursor)
		action_btn.setStyleSheet(f"""
			QPushButton{{
				color:{accent};background:{soft};
				border:1px solid {border};border-radius:7px;
				min-width:110px;padding:0 16px;
			}}
			QPushButton:hover{{
				background:{accent};
				color:{WHITE};
				border-color:{accent};
			}}
		""")
		action_btn.clicked.connect(self._on_confirm_clicked)

		btn_row.addWidget(cancel_btn, 1, Qt.AlignLeft)
		btn_row.addStretch()
		btn_row.addWidget(action_btn, 1, Qt.AlignRight)
		c_lay.addLayout(btn_row)

	def set_callbacks(self, on_confirm=None, on_close=None):
		self._on_confirm = on_confirm
		self._on_close = on_close

	def show_centered(self):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._card.adjustSize()
		x = (self.width() - self._card.width()) // 2
		y = (self.height() - self._card.height()) // 2
		self._card.move(x, y)
		self.show()
		self.raise_()

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		if self._card:
			x = (self.width() - self._card.width()) // 2
			y = (self.height() - self._card.height()) // 2
			self._card.move(x, y)
		super().resizeEvent(event)

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self._on_cancel()
			return
		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= 60:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active:
			pos = event.position().toPoint()
			new_pos = pos - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			self._card.move(
				max(0, min(new_pos.x(), max_x)),
				max(0, min(new_pos.y(), max_y)),
			)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self._drag_active = False
		super().mouseReleaseEvent(event)

	def _on_cancel(self):
		self._result = False
		self.hide()
		if callable(self._on_close):
			self._on_close()

	def _on_confirm_clicked(self):
		self._result = True
		self.hide()
		if callable(self._on_confirm):
			self._on_confirm(self._product)
		if callable(self._on_close):
			self._on_close()


class _NoticeDialog(QWidget):
	"""Small in-app notice dialog used instead of native message boxes."""

	def __init__(self, title, message, parent=None, kind="warning"):
		super().__init__(parent)
		self._on_close = None
		self._kind = kind
		self._drag_active = False
		self._drag_offset = QPoint()
		self.setStyleSheet("background:rgba(10,35,32,130);")

		accent, soft, border = self._colors_for_kind(kind)

		self._card = QFrame(self)
		self._card.setObjectName("noticeCard")
		self._card.setFixedWidth(440)
		self._card.setStyleSheet(f"""
			QFrame#noticeCard{{
				background:{CARD_SURFACE};
				border:1px solid {CARD_BORDER};
				border-radius:10px;
			}}
			QLabel{{background:transparent;border:none;}}
			QPushButton{{border:none;}}
		""")
		shadow = QGraphicsDropShadowEffect(self._card)
		shadow.setBlurRadius(46)
		shadow.setOffset(0, 14)
		shadow.setColor(QColor(0, 0, 0, 70))
		self._card.setGraphicsEffect(shadow)

		c_lay = QVBoxLayout(self._card)
		c_lay.setContentsMargins(22, 20, 22, 18)
		c_lay.setSpacing(12)

		head_row = QHBoxLayout()
		head_row.setContentsMargins(0, 0, 0, 0)
		head_row.setSpacing(12)

		mark = QLabel("!")
		mark.setAlignment(Qt.AlignCenter)
		mark.setFixedSize(36, 36)
		mark.setFont(inter(15, QFont.DemiBold))
		mark.setStyleSheet(
			f"color:{accent};background:{soft};border:1px solid {border};border-radius:18px;"
		)

		title_lbl = QLabel(str(title or "Notice"))
		title_lbl.setWordWrap(True)
		title_lbl.setFont(playfair(16, QFont.DemiBold))
		title_lbl.setStyleSheet(f"color:{INK};")

		head_row.addWidget(mark, 0, Qt.AlignTop)
		head_row.addWidget(title_lbl, 1)
		c_lay.addLayout(head_row)

		body_lbl = QLabel(str(message or "Something went wrong."))
		body_lbl.setWordWrap(True)
		body_lbl.setFont(inter(11))
		body_lbl.setStyleSheet(f"color:{GRAY_5};line-height:1.35;")
		c_lay.addWidget(body_lbl)
		c_lay.addSpacing(2)

		btn_row = QHBoxLayout()
		btn_row.setContentsMargins(0, 0, 0, 0)
		btn_row.addStretch()

		ok_btn = QPushButton("OK")
		ok_btn.setCursor(Qt.PointingHandCursor)
		ok_btn.setFont(inter(11, QFont.Medium))
		ok_btn.setFixedHeight(34)
		ok_btn.setStyleSheet(f"""
			QPushButton{{
				color:{WHITE};background:{TEAL};
				border:1px solid {TEAL};border-radius:7px;
				min-width:96px;padding:0 18px;
			}}
			QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
		""")
		ok_btn.clicked.connect(self._close)
		btn_row.addWidget(ok_btn)
		c_lay.addLayout(btn_row)

	def set_callbacks(self, on_close=None):
		self._on_close = on_close

	def show_centered(self):
		if self.parent():
			self.setGeometry(self.parent().rect())
		self._card.adjustSize()
		x = (self.width() - self._card.width()) // 2
		y = (self.height() - self._card.height()) // 2
		self._card.move(x, y)
		self.show()
		self.raise_()

	def resizeEvent(self, event):
		if self.parent():
			self.setGeometry(self.parent().rect())
		if self._card:
			x = (self.width() - self._card.width()) // 2
			y = (self.height() - self._card.height()) // 2
			self._card.move(x, y)
		super().resizeEvent(event)

	def mousePressEvent(self, event):
		pos = event.position().toPoint()
		if not self._card.geometry().contains(pos):
			self._close()
			return
		card_pos = pos - self._card.pos()
		if event.button() == Qt.LeftButton and card_pos.y() <= 64:
			self._drag_active = True
			self._drag_offset = card_pos
			event.accept()
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if self._drag_active:
			pos = event.position().toPoint()
			new_pos = pos - self._drag_offset
			max_x = max(0, self.width() - self._card.width())
			max_y = max(0, self.height() - self._card.height())
			self._card.move(
				max(0, min(new_pos.x(), max_x)),
				max(0, min(new_pos.y(), max_y)),
			)
			event.accept()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self._drag_active = False
		super().mouseReleaseEvent(event)

	def _close(self):
		self.hide()
		if callable(self._on_close):
			self._on_close()

	def _colors_for_kind(self, kind):
		if kind == "error":
			return DANGER, DANGER_SOFT, "#efc4c4"
		if kind == "success":
			return TEAL, TEAL_PALE, "#cde6e1"
		return AMBER, AMBER_SOFT, "#efd7a7"


# ── Products page ─────────────────────────────────────────────────────────────
class OwnerProductsView(QWidget):
	def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False, controller=None):
		super().__init__(parent)
		self._show_topbar = show_topbar
		self._topbar_controls_only = topbar_controls_only
		self._all_products = []
		self._filtered_products = []
		self._controller = None
		self._show_archived = False
		self._pending_search_text = ""
		self._search_timer = QTimer(self)
		self._search_timer.setSingleShot(True)
		self._search_timer.setInterval(250)
		self._search_timer.timeout.connect(self._perform_search)
		self._refresh_timer = QTimer(self)
		self._refresh_timer.setInterval(10000)
		self._refresh_timer.timeout.connect(self._refresh_if_visible)

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
		c_lay.setContentsMargins(30, 26, 30, 30)
		c_lay.setSpacing(0)

		# ── Title block ───────────────────────────────────────────────────────
		left = QVBoxLayout()
		left.setSpacing(0)

		sub = QLabel("PRODUCT CATALOG")
		sub.setFont(inter(10, QFont.DemiBold))
		sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

		self._title_lbl = QLabel("LPG Products")
		self._title_lbl.setFont(playfair(28, QFont.Medium))
		self._title_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

		self._page_sub_lbl = QLabel("Manage the owner product catalog with add and edit controls.")
		self._page_sub_lbl.setFont(inter(12))
		self._page_sub_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:5px;")

		left.addWidget(sub)
		left.addWidget(self._title_lbl)
		left.addWidget(self._page_sub_lbl)

		c_lay.addLayout(left)
		c_lay.addSpacing(16)

		# ── Toolbar row: [Search (expands)] [Add button] ─
		toolbar_row = QHBoxLayout()
		toolbar_row.setContentsMargins(0, 0, 0, 0)
		toolbar_row.setSpacing(12)

		self._search = QLineEdit()
		self._search.setPlaceholderText("Search products...")
		self._search.setFont(inter(12))
		self._search.setFixedHeight(40)
		self._search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self._search.setStyleSheet(
			f"""
			QLineEdit{{
				color:{GRAY_5};background:{WHITE};
				border:1px solid {CARD_BORDER};border-radius:8px;
				padding:0 13px;
			}}
			QLineEdit:focus{{border-color:{TEAL};background:{CARD_SURFACE};}}
			"""
		)
		self._search.textChanged.connect(self._on_search)

		self._add_btn = QPushButton("+ Add Product")
		self._add_btn.setCursor(Qt.PointingHandCursor)
		self._add_btn.setFont(inter(12, QFont.Medium))
		self._add_btn.setFixedHeight(40)
		self._add_btn.setFixedWidth(230)
		self._add_btn.clicked.connect(self._add_product)
		self._add_btn.setStyleSheet(
			f"""
			QPushButton {{
				color: {WHITE};
				background: {TEAL};
				border: 1px solid {TEAL};
				border-radius: 8px;
				padding: 0 18px;
			}}
			QPushButton:hover {{
				background: {TEAL_DARK};
				border-color: {TEAL_DARK};
			}}
			"""
		)

		self._archive_toggle_btn = QPushButton("View Archived")
		self._archive_toggle_btn.setCursor(Qt.PointingHandCursor)
		self._archive_toggle_btn.setFont(inter(12, QFont.Medium))
		self._archive_toggle_btn.setFixedHeight(40)
		self._archive_toggle_btn.setFixedWidth(180)
		self._archive_toggle_btn.clicked.connect(self._toggle_archived_products)
		self._archive_toggle_btn.setStyleSheet(
			f"""
			QPushButton {{
				color: {TEAL_DARK};
				background: {WHITE};
				border: 1px solid {CARD_BORDER};
				border-radius: 8px;
				padding: 0 14px;
			}}
			QPushButton:hover {{
				background: {TEAL_PALE};
				border-color: {TEAL};
				color: {TEAL_DARK};
			}}
			"""
		)

		toolbar_row.addWidget(self._search, 1)
		toolbar_row.addWidget(self._archive_toggle_btn, 0, Qt.AlignTop)
		toolbar_row.addWidget(self._add_btn, 0, Qt.AlignTop)

		c_lay.addLayout(toolbar_row)
		c_lay.addSpacing(14)

		list_head = QWidget()
		list_head.setStyleSheet("background:transparent;border:none;")
		lh_lay = QHBoxLayout(list_head)
		lh_lay.setContentsMargins(0, 0, 0, 12)
		lh_lay.setSpacing(10)

		self._count_lbl = QLabel("0 products")
		self._count_lbl.setFont(inter(11))
		self._count_lbl.setStyleSheet(
			f"color:{TEAL_DARK};background:{TEAL_PALE};border:1px solid #cde6e1;border-radius:12px;padding:4px 10px;"
		)

		lh_lay.addStretch()
		lh_lay.addWidget(self._count_lbl, 0, Qt.AlignRight)
		c_lay.addWidget(list_head)

		self._grid_wrap = QWidget()
		self._grid_wrap.setStyleSheet("background:transparent;border:none;")
		self._grid = QGridLayout(self._grid_wrap)
		self._grid.setContentsMargins(0, 0, 0, 0)
		self._grid.setHorizontalSpacing(16)
		self._grid.setVerticalSpacing(16)
		self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

		self._empty_state = QWidget()
		es_lay = QVBoxLayout(self._empty_state)
		es_lay.setContentsMargins(0, 36, 0, 36)
		es_lay.setAlignment(Qt.AlignCenter)

		empty_image = QLabel()
		empty_image.setAlignment(Qt.AlignCenter)
		empty_image.setStyleSheet("background:transparent;border:none;")
		empty_image.setFixedSize(230, 145)
		empty_pixmap = QPixmap(NO_PRODUCTS_IMAGE)
		if not empty_pixmap.isNull():
			scale = self.devicePixelRatio()
			target_w = int(230 * scale)
			target_h = int(145 * scale)
			scaled = empty_pixmap.scaled(
				target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation,
			)
			scaled.setDevicePixelRatio(scale)
			empty_image.setPixmap(scaled)

		self._empty_title = QLabel("No products available")
		self._empty_title.setFont(playfair(16, QFont.Medium))
		self._empty_title.setAlignment(Qt.AlignCenter)
		self._empty_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

		self._empty_sub = QLabel("Nothing to show here yet. Add a product to get started.")
		self._empty_sub.setFont(inter(12))
		self._empty_sub.setAlignment(Qt.AlignCenter)
		self._empty_sub.setWordWrap(False)
		self._empty_sub.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

		es_lay.addWidget(empty_image, 0, Qt.AlignCenter)
		es_lay.addWidget(self._empty_title)
		es_lay.addWidget(self._empty_sub)

		self._list_stack = QStackedWidget()
		self._list_stack.addWidget(self._grid_wrap)
		self._list_stack.addWidget(self._empty_state)
		c_lay.addWidget(self._list_stack)

		scroll.setWidget(self._content)
		root.addWidget(scroll)

		# ── Overlay modals (children of the view, not the scroll area) ────────
		self._product_modal = ProductFormModal(self)
		self._delete_overlay = None  # created on demand per product
		self._notice_overlay = None

	# ── Topbar ────────────────────────────────────────────────────────────────
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

	# ── Resize: keep overlays covering the full view ──────────────────────────
	def resizeEvent(self, event):
		super().resizeEvent(event)
		self._render_grid()
		# Overlays are children; they resize themselves via their own resizeEvent.

	# ── Data ─────────────────────────────────────────────────────────────────
	def load_products(self, products):
		self._all_products = [dict(p) for p in products]
		self._apply_filter(self._search.text() if hasattr(self, "_search") else "")

	def _on_search(self, text):
		self._pending_search_text = (text or "").strip()
		if self._controller and hasattr(self._controller, "search_products"):
			self._search_timer.start()
		else:
			self._apply_filter(text)

	def _perform_search(self):
		if self._controller and hasattr(self._controller, "search_products"):
			self._controller.search_products(self._pending_search_text, archived=self._show_archived)
		else:
			self._apply_filter(self._pending_search_text)

	def _refresh_if_visible(self):
		if not self.isVisible():
			self._sync_refresh_timer()
			return
		if self._product_modal.isVisible():
			return
		if self._delete_overlay is not None and self._delete_overlay.isVisible():
			return
		if self._notice_overlay is not None and self._notice_overlay.isVisible():
			return
		if self._controller and hasattr(self._controller, "refresh_products"):
			self._controller.refresh_products(archived=self._show_archived)

	def _sync_refresh_timer(self):
		should_run = self.isVisible() and self._controller is not None
		if should_run and not self._refresh_timer.isActive():
			self._refresh_timer.start()
		elif not should_run and self._refresh_timer.isActive():
			self._refresh_timer.stop()

	def _toggle_archived_products(self):
		self._set_archived_mode(not self._show_archived)

	def _set_archived_mode(self, archived, refresh=True):
		self._show_archived = bool(archived)
		self._sync_archive_controls()
		if self._search.text():
			self._search.blockSignals(True)
			self._search.clear()
			self._search.blockSignals(False)
		if refresh:
			self._load_current_products()
		else:
			self._apply_filter("")

	def _sync_archive_controls(self):
		if not hasattr(self, "_archive_toggle_btn"):
			return
		if self._show_archived:
			self._title_lbl.setText("Archived Products")
			self._page_sub_lbl.setText("Restore archived products when they should be available again.")
			self._search.setPlaceholderText("Search archived products...")
			self._archive_toggle_btn.setText("Active Products")
			self._add_btn.hide()
		else:
			self._title_lbl.setText("LPG Products")
			self._page_sub_lbl.setText("Manage the owner product catalog with add and edit controls.")
			self._search.setPlaceholderText("Search products...")
			self._archive_toggle_btn.setText("View Archived")
			self._add_btn.show()

	def _load_current_products(self):
		if self._controller and hasattr(self._controller, "refresh_products"):
			self._controller.refresh_products(archived=self._show_archived)
		else:
			self._apply_filter("")

	def _apply_filter(self, text):
		query = (text or "").strip().lower()
		products = list(self._all_products)

		if query:
			products = [
				p for p in products
				if query in str(p.get("name", "")).lower()
				or query in str(p.get("cylinder_size", "")).lower()
				or query in str(p.get("display_name", "")).lower()
			]

		products.sort(key=lambda p: str(p.get("name", "")).lower())

		self._filtered_products = products
		if hasattr(self, "_count_lbl"):
			count = len(self._filtered_products)
			label = "archived product" if self._show_archived else "product"
			self._count_lbl.setText(f"{count} {label}{'s' if count != 1 else ''}")

		self._render_grid()
		self._refresh_empty_state()
		self._list_stack.setCurrentWidget(
			self._grid_wrap if self._filtered_products else self._empty_state
		)

	def _render_grid(self):
		self._clear_layout(self._grid)
		if not self._filtered_products:
			return
		spacing = self._grid.horizontalSpacing()
		available_width = self._grid_wrap.width() or self._content.width() or (PRODUCT_CARD_WIDTH * 4)
		columns = max(1, min(4, (available_width + spacing) // (PRODUCT_CARD_WIDTH + spacing)))
		for index, product in enumerate(self._filtered_products):
			row = index // columns
			col = index % columns
			self._grid.addWidget(
				OwnerProductCard(
					product,
					self._edit_product,
					self._archive_product,
					self._delete_product,
					self._restore_product,
					archived=self._show_archived,
				),
				row,
				col,
			)
		self._grid.setColumnStretch(columns, 1)

	def _refresh_empty_state(self):
		keyword = self._search.text().strip()
		if keyword:
			self._empty_title.setText("No matching products")
			self._empty_sub.setText(f'No product matched "{keyword}". Try a different product name.')
			return
		if self._show_archived:
			self._empty_title.setText("No archived products")
			self._empty_sub.setText("Archived products will show here when you hide them from new deliveries.")
			return
		self._empty_title.setText("No products available")
		self._empty_sub.setText("Nothing to show here yet. Add a product to get started.")

	def _clear_layout(self, layout):
		while layout.count():
			item = layout.takeAt(0)
			widget = item.widget()
			child_layout = item.layout()
			if widget is not None:
				widget.deleteLater()
			elif child_layout is not None:
				self._clear_layout(child_layout)

	def _coerce_error_text(self, message):
		if isinstance(message, dict):
			for key in ("form", "name", "cylinder_size", "refill_price", "new_tank_price"):
				if message.get(key):
					return str(message[key])
			for value in message.values():
				if value:
					return str(value)
			return "Something went wrong."
		return str(message)

	def show_error(self, title, message):
		if self._notice_overlay is not None:
			self._notice_overlay.deleteLater()
			self._notice_overlay = None

		overlay = _NoticeDialog(title, self._coerce_error_text(message), self, kind="error")
		self._notice_overlay = overlay

		def _cleanup():
			if self._notice_overlay is overlay:
				self._notice_overlay = None
			overlay.deleteLater()

		overlay.set_callbacks(on_close=_cleanup)
		overlay.show_centered()

	def reset_view_state(self, refresh=True):
		self._product_modal.reset_state()

		if self._delete_overlay is not None:
			self._delete_overlay.hide()
			self._delete_overlay.deleteLater()
			self._delete_overlay = None

		if self._notice_overlay is not None:
			self._notice_overlay.hide()
			self._notice_overlay.deleteLater()
			self._notice_overlay = None

		if self._search.text():
			self._search.blockSignals(True)
			self._search.clear()
			self._search.blockSignals(False)

		if self._show_archived:
			self._show_archived = False
			self._sync_archive_controls()

		if refresh and self._controller and hasattr(self._controller, "refresh_products"):
			self._controller.refresh_products(archived=self._show_archived)
		else:
			self._apply_filter("")

	def showEvent(self, event):
		super().showEvent(event)
		self._sync_refresh_timer()
		if self._controller and hasattr(self._controller, "refresh_products"):
			self._controller.refresh_products(archived=self._show_archived)

	def hideEvent(self, event):
		self._search_timer.stop()
		self._refresh_timer.stop()
		self.reset_view_state(refresh=False)
		super().hideEvent(event)

	def bind_controller(self, controller, request_initial=False):
		self._controller = controller
		if hasattr(controller, "attach_view"):
			controller.attach_view(self)
		if request_initial and hasattr(controller, "refresh_products"):
			controller.refresh_products(archived=self._show_archived)
		self._sync_refresh_timer()
		return controller

	# ── CRUD actions (now use overlay modals) ─────────────────────────────────
	def _add_product(self):
		cb = self._controller.add_product if self._controller and hasattr(self._controller, "add_product") else None
		self._product_modal.open_add(cb)

	def _edit_product(self, product):
		current = next((p for p in self._all_products if p.get("id") == product.get("id")), None)
		if current is None:
			return
		cb = self._controller.update_product if self._controller and hasattr(self._controller, "update_product") else None
		self._product_modal.open_edit(current, cb)

	def _show_product_action_dialog(self, product, action, on_confirm):
		if self._delete_overlay is not None:
			self._delete_overlay.deleteLater()
			self._delete_overlay = None

		overlay = _ProductActionDialog(product, self, action=action)
		self._delete_overlay = overlay

		def _cleanup():
			if self._delete_overlay is overlay:
				self._delete_overlay = None
			overlay.deleteLater()

		overlay.set_callbacks(on_confirm=on_confirm, on_close=_cleanup)
		overlay.show_centered()

	def _archive_product(self, product):
		def _confirm_archive(selected_product):
			if not self._controller or not hasattr(self._controller, "archive_product"):
				return
			ok, response = self._controller.archive_product(selected_product)
			if not ok:
				self.show_error("Archive Product Failed", response)
				return
			self._load_current_products()

		self._show_product_action_dialog(product, "archive", _confirm_archive)

	def _delete_product(self, product):
		def _confirm_delete(selected_product):
			if not self._controller or not hasattr(self._controller, "delete_product"):
				return
			ok, response = self._controller.delete_product(
				selected_product,
				archived=self._show_archived,
			)
			if not ok:
				self.show_error("Delete Product Failed", response)
				return
			self._load_current_products()

		self._show_product_action_dialog(product, "delete", _confirm_delete)

	def _restore_product(self, product):
		if not self._controller or not hasattr(self._controller, "restore_product"):
			return
		ok, response = self._controller.restore_product(product)
		if not ok:
			self.show_error("Restore Product Failed", response)
			return
		self._load_current_products()


def main():
	from controllers.owner_product_controller import OwnerProductController

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
