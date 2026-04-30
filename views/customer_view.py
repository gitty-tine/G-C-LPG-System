import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime, QPoint
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QPixmap
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QLineEdit, QTextEdit,
    QGraphicsDropShadowEffect,
    QStackedWidget,
)

from controllers.customer_controller import CustomerController
from views.admin_dashboard_view import owner_scrollbar_qss

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
NO_CUSTOMERS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

TEAL       = "#1A7A6E"
TEAL_DARK  = "#145F55"
TEAL_MID   = "#1d8a7c"
TEAL_PALE  = "#e8f5f3"
TEAL_PALE2 = "#d0ede9"
WHITE      = "#ffffff"
GRAY_1     = "#f4f5f4"
GRAY_2     = "#e6eae9"
GRAY_3     = "#c4ccc9"
GRAY_4     = "#7a8a87"
GRAY_5     = "#3a4a47"
RED        = "#8a1a1a"
RED_BG     = "#fdeaea"
RED_BTN    = "#c0392b"
AMBER      = "#9a6700"
AMBER_BG   = "#fff6db"
AMBER_LINE = "#f1d48a"

CUSTOMER_NAME_W = 155
CUSTOMER_ADDRESS_W = 150
CUSTOMER_CONTACT_W = 110
CUSTOMER_DELIVERIES_W = 72
CUSTOMER_LAST_W = 105
CUSTOMER_NOTES_W = 120
CUSTOMER_CREATED_W = 105
CUSTOMER_ACTIONS_W = 112

PLAYFAIR_FAMILY = "Playfair Display"
INTER_FAMILY    = "Inter"


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


def trim_text(value, limit):
    text = " ".join(str(value or "-").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


class HDivider(QFrame):
    def __init__(self, color=GRAY_2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{color};border:none;")


# ── Reusable form field ───────────────────────────────────────────────────────
def make_field(label_text, placeholder, required=True, multiline=False):
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

    if multiline:
        inp = QTextEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFont(inter(12))
        inp.setFixedHeight(72)
        inp.setStyleSheet(f"""
            QTextEdit{{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:4px;
                padding:6px 10px;font-family:'{INTER_FAMILY}';
            }}
            QTextEdit:focus{{border-color:{TEAL};}}
        """)
        g_lay.addWidget(inp)
    else:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFont(inter(12))
        inp.setFixedHeight(34)
        inp.setStyleSheet(f"""
            QLineEdit{{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:4px;
                padding:0 10px;
            }}
            QLineEdit:focus{{border-color:{TEAL};}}
        """)
        g_lay.addWidget(inp)

    err = QLabel("")
    err.setFont(inter(10))
    err.setStyleSheet(f"color:{RED_BTN};background:transparent;border:none;")
    err.setContentsMargins(2, 2, 0, 0)
    err.setWordWrap(True)
    err.hide()
    g_lay.addWidget(err)

    return grp, inp, err


# ── Customer form modal overlay ───────────────────────────────────────────────
class CustomerFormModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(0,0,0,100);")
        self._mode     = "add"
        self._callback = None
        self._edit_id  = None
        self._drag_active = False
        self._drag_offset = QPoint()
        self.hide()

        # Modal card
        self._card = QFrame(self)
        self._card.setObjectName("modalCard")
        self._card.setFixedWidth(520)
        self._card.setStyleSheet(f"""
            QFrame#modalCard{{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 60))
        self._card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(self._card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet(
            f"background:{TEAL_DARK};border:none;"
            "border-top-left-radius:8px;border-top-right-radius:8px;"
        )
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(22, 16, 22, 14)
        h_lay.setSpacing(3)

        self._modal_title = QLabel("Add Customer")
        self._modal_title.setFont(playfair(16, QFont.DemiBold))
        self._modal_title.setStyleSheet(f"color:{WHITE};background:transparent;border:none;")

        self._modal_subtitle = QLabel("Fill in the details to add a new customer.")
        self._modal_subtitle.setFont(inter(11))
        self._modal_subtitle.setStyleSheet(f"color:#a8e6df;background:transparent;border:none;")

        h_lay.addWidget(self._modal_title)
        h_lay.addWidget(self._modal_subtitle)
        card_lay.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(22, 20, 22, 20)
        b_lay.setSpacing(14)

        f1, self.inp_name, self.err_name = make_field(
            "Full Name", "e.g. Kristine Katigbak", required=True
        )
        f2, self.inp_address, self.err_address = make_field(
            "Address", "e.g. Brgy. Putol, Tuy, Batangas", required=True, multiline=True
        )
        f3, self.inp_contact, self.err_contact = make_field(
            "Contact Number", "e.g. 09171234567", required=True
        )
        f4, self.inp_notes, self.err_notes = make_field(
            "Notes", "Optional delivery instructions", required=False, multiline=True
        )

        self.inp_name.textChanged.connect(lambda _: self._clear_field_error(self.err_name))
        self.inp_address.textChanged.connect(lambda: self._clear_field_error(self.err_address))
        self.inp_contact.textChanged.connect(lambda _: self._clear_field_error(self.err_contact))
        self.inp_notes.textChanged.connect(lambda: self._clear_field_error(self.err_notes))

        for f in [f1, f2, f3, f4]:
            b_lay.addWidget(f)

        self._err_lbl = QLabel("")
        self._err_lbl.setFont(inter(11))
        self._err_lbl.setStyleSheet(f"color:{RED_BTN};background:transparent;border:none;")
        self._err_lbl.setWordWrap(True)
        self._err_lbl.hide()
        b_lay.addWidget(self._err_lbl)

        card_lay.addWidget(body)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(f"background:{WHITE};border:none;border-top:1px solid {GRAY_2};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(22, 14, 22, 16)
        f_lay.setSpacing(10)
        f_lay.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_btn.setFont(inter(12, QFont.Medium))
        self._cancel_btn.setFixedHeight(34)
        self._cancel_btn.setStyleSheet(f"""
            QPushButton{{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_3};border-radius:6px;padding:0 18px;
            }}
            QPushButton:hover{{border-color:{TEAL};color:{TEAL_DARK};}}
        """)
        self._cancel_btn.clicked.connect(self.hide)

        self._save_btn = QPushButton("Save Customer")
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.setFont(inter(12, QFont.Medium))
        self._save_btn.setFixedHeight(34)
        self._save_btn.setStyleSheet(f"""
            QPushButton{{
                color:{WHITE};background:{TEAL};
                border:none;border-radius:6px;padding:0 18px;
            }}
            QPushButton:hover{{background:{TEAL_DARK};}}
        """)
        self._save_btn.clicked.connect(self._on_save)

        f_lay.addWidget(self._cancel_btn)
        f_lay.addWidget(self._save_btn)
        card_lay.addWidget(footer)

    def open_add(self, callback):
        self._mode     = "add"
        self._callback = callback
        self._edit_id  = None
        self._modal_title.setText("Add Customer")
        self._modal_subtitle.setText("Fill in the details to add a new customer.")
        self._save_btn.setText("Save Customer")
        self._clear_fields()
        self._clear_inline_errors()
        self._show_centered()

    def open_edit(self, customer_data, callback):
        self._mode     = "edit"
        self._callback = callback
        self._edit_id  = customer_data.get("id")
        self._modal_title.setText("Edit Customer Details")
        self._modal_subtitle.setText("Update the customer's details below.")
        self._save_btn.setText("Update Details")
        self._clear_inline_errors()
        self.inp_name.setText(customer_data.get("full_name", ""))
        self.inp_address.setPlainText(customer_data.get("address", ""))
        self.inp_contact.setText(customer_data.get("contact_number", ""))
        self.inp_notes.setPlainText(customer_data.get("notes", ""))
        self._show_centered()

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

    def _clear_fields(self):
        self.inp_name.clear()
        self.inp_address.clear()
        self.inp_contact.clear()
        self.inp_notes.clear()

    def _clear_inline_errors(self):
        for err in [self.err_name, self.err_address, self.err_contact, self.err_notes]:
            err.clear()
            err.hide()
        self._err_lbl.clear()
        self._err_lbl.hide()
        self._refresh_card_geometry()

    def _clear_field_error(self, err_label):
        changed = False
        if not err_label.isHidden() or err_label.text():
            err_label.clear()
            err_label.hide()
            changed = True
        if not self._err_lbl.isHidden() or self._err_lbl.text():
            self._err_lbl.clear()
            self._err_lbl.hide()
            changed = True
        if changed:
            self._refresh_card_geometry()

    def reset_state(self):
        self._mode = "add"
        self._callback = None
        self._edit_id = None
        self._drag_active = False
        self._drag_offset = QPoint()
        self._modal_title.setText("Add Customer")
        self._modal_subtitle.setText("Fill in the details to add a new customer.")
        self._save_btn.setText("Save Customer")
        self._clear_fields()
        self._clear_inline_errors()
        self.hide()

    def _on_save(self):
        self._clear_inline_errors()

        name = re.sub(r'[^a-zA-Z0-9\s]', '', self.inp_name.text()).strip()
        address = self.inp_address.toPlainText().strip()
        contact = self.inp_contact.text().strip()
        notes   = self.inp_notes.toPlainText().strip()

        has_error = False

        if not name:
            self.err_name.setText("Full name is required.")
            self.err_name.show()
            has_error = True
        if not address:
            self.err_address.setText("Address is required.")
            self.err_address.show()
            has_error = True
        if not contact:
            self.err_contact.setText("Contact number is required.")
            self.err_contact.show()
            has_error = True

        if has_error:
            self._refresh_card_geometry()
            return

        data = {
            "id":             self._edit_id,
            "full_name":      name,
            "address":        address,
            "contact_number": contact,
            "notes":          notes,
        }
        if self._callback:
            if self._callback(data, self._mode) is False:
                return
        self.hide()

    def show_server_error(self, message):
        self._clear_inline_errors()
        message = str(message or "").strip()
        msg_lower = message.lower()
        if "name" in msg_lower:
            self.err_name.setText(message)
            self.err_name.show()
        elif "address" in msg_lower:
            self.err_address.setText(message)
            self.err_address.show()
        elif "contact" in msg_lower:
            self.err_contact.setText(message)
            self.err_contact.show()
        else:
            self._err_lbl.setText(message)
            self._err_lbl.show()
        self._refresh_card_geometry()

    def _show_error(self, msg):
        self._err_lbl.setText(msg)
        self._err_lbl.show()
        self._refresh_card_geometry()


# ── Delete confirmation modal ─────────────────────────────────────────────────
class DeleteConfirmModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(0,0,0,100);")
        self._callback = None
        self._drag_active = False
        self._drag_offset = QPoint()
        self.hide()

        self._card = QFrame(self)
        self._card.setObjectName("delCard")
        self._card.setFixedWidth(440)
        self._card.setStyleSheet(f"""
            QFrame#delCard{{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 60))
        self._card.setGraphicsEffect(shadow)

        c_lay = QVBoxLayout(self._card)
        c_lay.setContentsMargins(24, 24, 24, 20)
        c_lay.setSpacing(14)

        icon_lbl = QLabel("!")
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(inter(18, QFont.DemiBold))
        icon_lbl.setStyleSheet(f"background:{RED_BG};color:{RED_BTN};border-radius:20px;border:none;")

        title = QLabel("Delete Customer")
        title.setFont(playfair(16, QFont.DemiBold))
        title.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

        self._msg = QLabel("Are you sure you want to delete this customer? This action cannot be undone.")
        self._msg.setFont(inter(12))
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(44)
        self._msg.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        c_lay.addWidget(icon_lbl)
        c_lay.addWidget(title)
        c_lay.addWidget(self._msg)
        c_lay.addWidget(HDivider(GRAY_2))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setFont(inter(12, QFont.Medium))
        cancel.setFixedHeight(34)
        cancel.setStyleSheet(f"""
            QPushButton{{color:{GRAY_5};background:{WHITE};border:1px solid {GRAY_2};border-radius:4px;padding:0 18px;}}
            QPushButton:hover{{background:{GRAY_1};}}
        """)
        cancel.clicked.connect(self.hide)

        self._del_btn = QPushButton("Delete")
        self._del_btn.setCursor(Qt.PointingHandCursor)
        self._del_btn.setFont(inter(12, QFont.Medium))
        self._del_btn.setFixedHeight(34)
        self._del_btn.setStyleSheet(f"""
            QPushButton{{color:{WHITE};background:{RED_BTN};border:1px solid {RED_BTN};border-radius:4px;padding:0 18px;}}
            QPushButton:hover{{background:#a93226;border-color:#a93226;}}
        """)
        self._del_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel)
        btn_row.addWidget(self._del_btn)
        c_lay.addLayout(btn_row)

    def open(self, customer_name, customer_id, callback):
        self._callback    = callback
        self._customer_id = customer_id
        self._msg.setText(f'Are you sure you want to delete "{customer_name}"? This action cannot be undone.')
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._card.adjustSize()
        x = (self.width()  - self._card.width())  // 2
        y = (self.height() - self._card.height()) // 2
        self._card.move(x, y)
        self.show()
        self.raise_()

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        if self._card:
            x = (self.width()  - self._card.width())  // 2
            y = (self.height() - self._card.height()) // 2
            self._card.move(x, y)
        super().resizeEvent(event)

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

    def _on_confirm(self):
        if self._callback:
            self._callback(self._customer_id)
        self.hide()

    def reset_state(self):
        self._callback = None
        self._drag_active = False
        self._drag_offset = QPoint()
        self._msg.setText("Are you sure you want to delete this customer? This action cannot be undone.")
        self.hide()


class StatusModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(15,23,20,110);")
        self._drag_active = False
        self._drag_offset = QPoint()
        self.hide()

        self._card = QFrame(self)
        self._card.setObjectName("statusCard")
        self._card.setFixedWidth(470)
        self._card.setStyleSheet(f"""
            QFrame#statusCard{{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:10px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(0, 0, 0, 70))
        self._card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._hero = QFrame()
        self._hero.setMinimumHeight(102)
        self._hero.setStyleSheet(f"background:{AMBER_BG};border:none;border-top-left-radius:10px;border-top-right-radius:10px;")
        hero_lay = QVBoxLayout(self._hero)
        hero_lay.setContentsMargins(24, 20, 24, 18)
        hero_lay.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        self._icon = QLabel("!")
        self._icon.setFixedSize(44, 44)
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setFont(inter(18, QFont.DemiBold))
        self._icon.setStyleSheet(
            f"background:{WHITE};color:{AMBER};border:1px solid {AMBER_LINE};border-radius:22px;"
        )

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        self._eyebrow = QLabel("Action blocked")
        self._eyebrow.setFont(inter(10, QFont.DemiBold))
        self._eyebrow.setStyleSheet(f"color:{AMBER};letter-spacing:1.1px;background:transparent;border:none;")

        self._title = QLabel("Unable to delete customer")
        self._title.setFont(playfair(17, QFont.DemiBold))
        self._title.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

        title_col.addWidget(self._eyebrow)
        title_col.addWidget(self._title)

        top_row.addWidget(self._icon, 0, Qt.AlignTop)
        top_row.addLayout(title_col)
        top_row.addStretch()
        hero_lay.addLayout(top_row)

        layout.addWidget(self._hero)

        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 20, 24, 20)
        body_lay.setSpacing(0)

        self._message = QLabel("")
        self._message.setFont(inter(12))
        self._message.setWordWrap(True)
        self._message.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;line-height:1.35;")

        body_lay.addWidget(self._message)
        layout.addWidget(body)

        footer = QWidget()
        footer.setStyleSheet("background:transparent;border:none;")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(24, 14, 24, 16)
        footer_lay.setSpacing(10)
        footer_lay.addStretch()

        layout.addWidget(footer)

    def open(self, title, message, eyebrow="Action blocked", button_text=None):
        self._title.setText(title)
        self._message.setText(message)
        self._eyebrow.setText(eyebrow)

        if self.parent():
            self.setGeometry(self.parent().rect())
        self._card.adjustSize()
        x = (self.width()  - self._card.width())  // 2
        y = (self.height() - self._card.height()) // 2
        self._card.move(x, y)
        self.show()
        self.raise_()
        QTimer.singleShot(4000, self.hide)

    def reset_state(self):
        self._drag_active = False
        self._drag_offset = QPoint()
        self._eyebrow.setText("Action blocked")
        self._title.setText("Unable to delete customer")
        self._message.clear()
        self.hide()

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        if self._card:
            x = (self.width()  - self._card.width())  // 2
            y = (self.height() - self._card.height()) // 2
            self._card.move(x, y)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if not self._card.geometry().contains(pos):
            self.hide()
            return

        card_pos = pos - self._card.pos()
        if event.button() == Qt.LeftButton and card_pos.y() <= 92:
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


# ── Customer page widget ──────────────────────────────────────────────────────
class CustomerView(QWidget):
    def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False):
        super().__init__(parent)
        self._show_topbar = show_topbar
        self._topbar_controls_only = topbar_controls_only
        self._visible_customers = []
        self._pending_search_text = ""
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._perform_search)
        load_fonts()
        self.setStyleSheet(f"background:{GRAY_1};")
        self._build_ui()
        self._load_from_db()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if self._show_topbar:
            root.addWidget(self._build_topbar())

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(owner_scrollbar_qss())

        content = QWidget()
        content.setStyleSheet("background:transparent;")
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(28, 24, 28, 28)
        c_lay.setSpacing(14)

        # Page title row
        title_row = QHBoxLayout()
        title_row.setSpacing(0)

        left = QVBoxLayout()
        left.setSpacing(0)
        left.setContentsMargins(0, 0, 0, 0)

        sub = QLabel("CLIENT RECORDS")
        sub.setFont(inter(10, QFont.DemiBold))
        sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:2px;")

        title = QLabel("Customers")
        title.setFont(playfair(28, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        page_sub = QLabel("Manage all customer records for G and C LPG Trading.")
        page_sub.setFont(inter(12))
        page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:0px;")

        left.addWidget(sub)
        left.addWidget(title)
        left.addWidget(page_sub)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by name, contact, address, or notes...")
        self._search.setFont(inter(12))
        self._search.setFixedHeight(36)
        self._search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._search.setStyleSheet(f"""
            QLineEdit{{
                color:{GRAY_5};
                background:#fbfcfc;
                border:1px solid #d6e2df;
                border-radius:8px;
                padding:0 12px;
            }}
            QLineEdit:hover{{
                border-color:#b9d4cf;
                background:{WHITE};
            }}
            QLineEdit:focus{{
                border-color:{TEAL};
                background:{WHITE};
            }}
        """)
        self._search.textChanged.connect(self._on_search)

        title_row.addLayout(left)
        c_lay.addLayout(title_row)

        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 4, 0, 0)
        summary_row.setSpacing(12)
        total_card, self._summary_total_lbl = self._summary_card(
            "VISIBLE CUSTOMERS",
            "0",
            "Matching current view",
            TEAL,
        )
        active_card, self._summary_active_lbl = self._summary_card(
            "WITH DELIVERIES",
            "0",
            "Customers with delivery history",
            TEAL_DARK,
        )
        deliveries_card, self._summary_deliveries_lbl = self._summary_card(
            "DELIVERY RECORDS",
            "0",
            "Total linked deliveries",
            GRAY_5,
        )
        summary_row.addWidget(total_card, 1)
        summary_row.addWidget(active_card, 1)
        summary_row.addWidget(deliveries_card, 1)
        c_lay.addLayout(summary_row)

        self._add_btn = QPushButton("+ Add Customer")
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setFont(inter(12, QFont.Medium))
        self._add_btn.setFixedHeight(38)
        self._add_btn.setMinimumWidth(180)
        self._add_btn.setStyleSheet(f"""
            QPushButton{{
                color:{WHITE};
                background:{TEAL};
                border:1px solid {TEAL};
                border-radius:7px;
                padding:0 18px;
            }}
            QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
        """)
        self._add_btn.clicked.connect(self._open_add)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 2)
        action_row.setSpacing(12)
        action_row.addWidget(self._search, 1, Qt.AlignVCenter)
        action_row.addWidget(self._add_btn, 0, Qt.AlignRight | Qt.AlignVCenter)
        c_lay.addLayout(action_row)

        # Table card
        table_card = QFrame()
        table_card.setObjectName("CustomerTableCard")
        table_card.setMinimumHeight(540)
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_card.setStyleSheet(
            f"""
            QFrame#CustomerTableCard{{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
            }}
            """
        )
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(0, 0, 0, 0)
        t_lay.setSpacing(0)

        # Table header bar
        th_bar = QWidget()
        th_bar.setFixedHeight(56)
        th_bar.setStyleSheet(f"background:#fbfdfc;border:none;border-bottom:1px solid {GRAY_2};")
        thb_lay = QHBoxLayout(th_bar)
        thb_lay.setContentsMargins(18, 0, 18, 0)

        tbl_title = QLabel("Customer List")
        tbl_title.setFont(playfair(14, QFont.Medium))
        tbl_title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        self._count_lbl = QLabel("0 records")
        self._count_lbl.setFont(inter(11))
        self._count_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        thb_lay.addWidget(tbl_title)
        thb_lay.addStretch()
        thb_lay.addWidget(self._count_lbl)
        t_lay.addWidget(th_bar)

        self._customers_page = QWidget()
        self._customers_page.setStyleSheet("background:transparent;border:none;")
        customer_page_lay = QVBoxLayout(self._customers_page)
        customer_page_lay.setContentsMargins(0, 0, 0, 0)
        customer_page_lay.setSpacing(0)

        table_header = QWidget()
        table_header.setFixedHeight(50)
        table_header.setStyleSheet(f"background:#f4f8f7;border:none;border-bottom:1px solid {GRAY_2};")
        header_lay = QGridLayout(table_header)
        header_lay.setContentsMargins(16, 0, 16, 0)
        header_lay.setHorizontalSpacing(10)
        header_lay.setVerticalSpacing(0)
        self._configure_customer_columns(header_lay)

        headers = [
            ("CUSTOMER", Qt.AlignLeft | Qt.AlignVCenter),
            ("ADDRESS", Qt.AlignLeft | Qt.AlignVCenter),
            ("CONTACT", Qt.AlignLeft | Qt.AlignVCenter),
            ("ORDERS", Qt.AlignCenter),
            ("LAST", Qt.AlignCenter),
            ("NOTES", Qt.AlignLeft | Qt.AlignVCenter),
            ("ADDED", Qt.AlignCenter),
            ("ACTIONS", Qt.AlignCenter),
        ]
        for col, (text, alignment) in enumerate(headers):
            header_lay.addWidget(self._customer_header_label(text, alignment), 0, col)
        customer_page_lay.addWidget(table_header)

        self._customer_scroll = QScrollArea()
        self._customer_scroll.setWidgetResizable(True)
        self._customer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._customer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._customer_scroll.setStyleSheet(owner_scrollbar_qss())

        self._customer_list = QWidget()
        self._customer_list.setStyleSheet("background:transparent;border:none;")
        self._customer_rows_lay = QVBoxLayout(self._customer_list)
        self._customer_rows_lay.setContentsMargins(14, 14, 14, 14)
        self._customer_rows_lay.setSpacing(8)

        self._customer_scroll.setWidget(self._customer_list)
        customer_page_lay.addWidget(self._customer_scroll)

        # Empty state
        self._empty_state = QWidget()
        self._empty_state.setStyleSheet("background:transparent;border:none;")
        es_lay = QVBoxLayout(self._empty_state)
        es_lay.setAlignment(Qt.AlignCenter)
        es_lay.setContentsMargins(0, 48, 0, 48)

        es_image = QLabel()
        es_image.setAlignment(Qt.AlignCenter)
        es_image.setStyleSheet("background:transparent;border:none;")
        es_image.setFixedSize(230, 145)
        empty_pixmap = QPixmap(NO_CUSTOMERS_IMAGE)
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
            es_image.setPixmap(scaled)

        self._empty_title = QLabel("No customers yet")
        self._empty_title.setFont(playfair(16, QFont.Medium))
        self._empty_title.setAlignment(Qt.AlignCenter)
        self._empty_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        self._empty_sub = QLabel('Click "+ Add Customer" to add your first customer.')
        self._empty_sub.setFont(inter(12))
        self._empty_sub.setAlignment(Qt.AlignCenter)
        self._empty_sub.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

        es_lay.addWidget(es_image, 0, Qt.AlignCenter)
        es_lay.addSpacing(8)
        es_lay.addWidget(self._empty_title)
        es_lay.addSpacing(4)
        es_lay.addWidget(self._empty_sub)

        self._table_stack = QStackedWidget()
        self._table_stack.addWidget(self._customers_page)
        self._table_stack.addWidget(self._empty_state)
        t_lay.addWidget(self._table_stack)
        c_lay.addWidget(table_card, 1)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # Modals
        self._form_modal   = CustomerFormModal(self)
        self._delete_modal = DeleteConfirmModal(self)
        self._status_modal = StatusModal(self)

        self._refresh_empty_state()

    def _summary_card(self, title, value, caption, color):
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background:{WHITE};
                border:1px solid {GRAY_2};
                border-radius:8px;
                border-top:3px solid {color};
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

    def _configure_customer_columns(self, layout):
        widths = {
            0: CUSTOMER_NAME_W,
            1: CUSTOMER_ADDRESS_W,
            2: CUSTOMER_CONTACT_W,
            3: CUSTOMER_DELIVERIES_W,
            4: CUSTOMER_LAST_W,
            5: CUSTOMER_NOTES_W,
            6: CUSTOMER_CREATED_W,
            7: CUSTOMER_ACTIONS_W,
        }
        for column, width in widths.items():
            layout.setColumnMinimumWidth(column, width)
            layout.setColumnStretch(column, 0)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(5, 1)

    def _customer_header_label(self, text, alignment):
        label = QLabel(text)
        label.setFont(inter(9, QFont.DemiBold))
        label.setAlignment(alignment)
        label.setStyleSheet(
            f"color:{GRAY_4};letter-spacing:1.2px;background:transparent;border:none;"
        )
        return label

    def _clear_customer_rows(self):
        if not hasattr(self, "_customer_rows_lay"):
            return
        while self._customer_rows_lay.count():
            item = self._customer_rows_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_customer_row(self, customer):
        row = QFrame()
        row.setObjectName("CustomerRow")
        row.setFixedHeight(68)
        row.setStyleSheet(
            f"""
            QFrame#CustomerRow {{
                background:#fbfdfc;
                border:1px solid {GRAY_2};
                border-radius:6px;
            }}
            QFrame#CustomerRow:hover {{
                background:#eef8f6;
                border-color:#c9ddd9;
            }}
            """
        )

        grid = QGridLayout(row)
        grid.setContentsMargins(14, 0, 14, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(0)
        self._configure_customer_columns(grid)

        grid.addWidget(self._customer_cell(customer.get("full_name", ""), TEAL_DARK, QFont.Medium), 0, 0)
        grid.addWidget(self._customer_cell(customer.get("address", ""), GRAY_5), 0, 1)
        grid.addWidget(self._customer_cell(customer.get("contact_number", ""), GRAY_5), 0, 2)
        grid.addWidget(
            self._customer_cell(
                customer.get("total_deliveries", 0),
                TEAL_DARK,
                QFont.DemiBold,
                Qt.AlignCenter,
            ),
            0,
            3,
        )
        grid.addWidget(
            self._customer_cell(customer.get("last_delivery", "-"), GRAY_5, QFont.Normal, Qt.AlignCenter),
            0,
            4,
        )
        grid.addWidget(self._customer_cell(customer.get("notes", "-"), GRAY_5), 0, 5)
        grid.addWidget(
            self._customer_cell(customer.get("created_at", "-"), GRAY_5, QFont.Normal, Qt.AlignCenter),
            0,
            6,
        )
        grid.addWidget(self._customer_actions_cell(customer), 0, 7)
        return row

    def _customer_cell(
        self,
        value,
        color=GRAY_5,
        weight=QFont.Normal,
        alignment=Qt.AlignLeft | Qt.AlignVCenter,
    ):
        raw_text = str(value if value is not None else "-")
        label = QLabel(trim_text(raw_text, 34))
        label.setFont(inter(11, weight))
        label.setAlignment(alignment)
        label.setMinimumWidth(0)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        label.setToolTip(raw_text)
        label.setStyleSheet(f"color:{color};background:transparent;border:none;")
        return label

    def _customer_actions_cell(self, customer):
        wrapper = QWidget()
        wrapper.setStyleSheet("background:transparent;border:none;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFont(inter(10, QFont.Medium))
        edit_btn.setFixedSize(48, 30)
        edit_btn.setStyleSheet(
            f"""
            QPushButton {{
                color:{WHITE};
                background:{TEAL};
                border:1px solid {TEAL};
                border-radius:6px;
            }}
            QPushButton:hover {{
                background:{TEAL_DARK};
                border-color:{TEAL_DARK};
            }}
            """
        )
        edit_btn.clicked.connect(lambda _checked=False, item=customer: self._open_edit(item))

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFont(inter(10, QFont.Medium))
        delete_btn.setFixedSize(58, 30)
        delete_btn.setStyleSheet(
            f"""
            QPushButton {{
                color:{RED_BTN};
                background:{RED_BG};
                border:1px solid #f4c7c7;
                border-radius:6px;
            }}
            QPushButton:hover {{
                background:#fbdada;
                border-color:#e4a8a8;
            }}
            """
        )
        delete_btn.clicked.connect(lambda _checked=False, item=customer: self._open_delete(item))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        return wrapper

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
            breadcrumb = QLabel("CUSTOMER MANAGEMENT")
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
        self._date_lbl.setText(QDate.currentDate().toString("dddd, MMMM d, yyyy"))

    # ── Actions ───────────────────────────────────────────────────────────────
    def _open_add(self):
        self._form_modal.open_add(self._on_form_saved)

    def _open_edit(self, customer):
        self._form_modal.open_edit(dict(customer), self._on_form_saved)

    def _open_delete(self, customer):
        self._delete_modal.open(customer["full_name"], customer["id"], self._on_delete_confirmed)

    def _on_form_saved(self, data, mode):
        if mode == "add":
            ok, res = CustomerController.add_customer(
                data.get("full_name", ""),
                data.get("address", ""),
                data.get("contact_number", ""),
                data.get("notes", ""),
            )
            if ok:
                self._refresh_visible_customers()
                return True
            else:
                self._form_modal.show_server_error(res)
                return False
        else:
            ok, res = CustomerController.update_customer(
                data.get("id"),
                data.get("full_name", ""),
                data.get("address", ""),
                data.get("contact_number", ""),
                data.get("notes", ""),
            )
            if ok:
                self._refresh_visible_customers()
                return True
            else:
                self._form_modal.show_server_error(res)
                return False

    def _on_delete_confirmed(self, customer_id):
        ok, res = CustomerController.delete_customer(customer_id)
        if ok:
            self._refresh_visible_customers()
        else:
            self._show_error_message("Delete Customer Failed", res)

    def _on_search(self, text):
        self._pending_search_text = text.strip()
        self._search_timer.start()

    def _perform_search(self):
        keyword = self._pending_search_text
        if keyword == "":
            self._load_from_db()
            return
        ok, res = CustomerController.search_customers(keyword)
        if ok:
            self.load_customers(res)
        else:
            self._show_error_message("Search Failed", res)

    # ── Data helpers ──────────────────────────────────────────────────────────
    def _customer_row_data(self, customer):
        return {
            "id": customer.get("id"),
            "full_name": customer.get("full_name", ""),
            "address": customer.get("address", ""),
            "contact_number": customer.get("contact_number", ""),
            "total_deliveries": customer.get("total_deliveries", 0) or 0,
            "last_delivery": customer.get("last_delivery", "") or "-",
            "notes": customer.get("notes", "") or "-",
            "created_at": customer.get("created_at", "") or "-",
        }

    def load_customers(self, customers):
        self._visible_customers = [self._customer_row_data(c) for c in customers]
        self._clear_customer_rows()

        for customer in self._visible_customers:
            self._customer_rows_lay.addWidget(self._build_customer_row(customer))
        self._customer_rows_lay.addStretch()

        self._refresh_summary_cards(self._visible_customers)
        self._refresh_counts()

    def _refresh_summary_cards(self, customers):
        total_customers = len(customers)
        with_deliveries = 0
        delivery_records = 0

        for customer in customers:
            try:
                total_deliveries = int(customer.get("total_deliveries", 0) or 0)
            except (TypeError, ValueError):
                total_deliveries = 0
            if total_deliveries > 0:
                with_deliveries += 1
            delivery_records += total_deliveries

        self._summary_total_lbl.setText(str(total_customers))
        self._summary_active_lbl.setText(str(with_deliveries))
        self._summary_deliveries_lbl.setText(str(delivery_records))

    def _refresh_counts(self):
        count = len(self._visible_customers)
        self._count_lbl.setText(f"{count} record{'s' if count != 1 else ''}")
        self._refresh_empty_state()

    def _refresh_empty_state(self):
        has_rows = len(self._visible_customers) > 0
        keyword = self._search.text().strip()
        if keyword:
            self._empty_title.setText("No matching customers")
            self._empty_sub.setText(
                f'No customer matched "{keyword}". Try a different name or contact number.'
            )
        else:
            self._empty_title.setText("No customers yet")
            self._empty_sub.setText('Click "+ Add Customer" to add your first customer.')
        self._table_stack.setCurrentWidget(self._customers_page if has_rows else self._empty_state)

    # --- Data loading helpers ---
    def reset_view_state(self):
        self._form_modal.reset_state()
        self._delete_modal.reset_state()
        self._status_modal.reset_state()

        self._search_timer.stop()
        self._pending_search_text = ""
        if self._search.text():
            self._search.blockSignals(True)
            self._search.clear()
            self._search.blockSignals(False)

        self._load_from_db()

    def _refresh_visible_customers(self):
        keyword = self._search.text().strip()
        if keyword == "":
            self._load_from_db()
            return

        ok, res = CustomerController.search_customers(keyword)
        if ok:
            self.load_customers(res)
        else:
            self._show_error_message("Search Failed", res)

    def _load_from_db(self):
        ok, res = CustomerController.list_customers()
        if ok:
            self.load_customers(res)
        else:
            self._show_error_message("Load Failed", res)

    def _show_error_message(self, title, message):
        lowered_title = (title or "").lower()
        lowered_message = (message or "").lower()

        if "delete customer" in lowered_title:
            self._status_modal.open(
                "Unable to Delete Customer",
                message,
                eyebrow="Delete blocked",
                button_text="OK",
            )
            return

        self._status_modal.open(
            title or "Something went wrong",
            message or "Please try again.",
            eyebrow="Request not completed",
            button_text="Close",
        )


# ── Standalone test ───────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setFont(inter(11))
    from views.admin_dashboard_view import DashboardView

    win = DashboardView()

    win.keyPressEvent = lambda e: None
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
