import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime, QSortFilterProxyModel, QPoint
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QPainter, QPixmap, QStandardItemModel, QStandardItem
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QTableView, QHeaderView, QLineEdit, QTextEdit,
    QGraphicsDropShadowEffect, QAbstractItemView, QMessageBox,
    QStackedWidget,
    QSpacerItem
)

from controllers.customer_controller import CustomerController
from views.admin_dashboard_view import owner_scrollbar_qss

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

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

    return grp, inp


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
        header.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(22, 18, 18, 16)

        self._modal_title = QLabel("Add Customer")
        self._modal_title.setFont(playfair(16, QFont.DemiBold))
        self._modal_title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        h_lay.addWidget(self._modal_title)
        h_lay.addStretch()
        card_lay.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(22, 20, 22, 20)
        b_lay.setSpacing(14)

        f1, self.inp_name    = make_field("Full Name",       "e.g. Kristine Katigbak",           required=True)
        f2, self.inp_address = make_field("Address",         "e.g. Brgy. Putol, Tuy, Batangas", required=True, multiline=True)
        f3, self.inp_contact = make_field("Contact Number",  "e.g. 09171234567",            required=True)
        f4, self.inp_notes   = make_field("Notes",           "Optional delivery instructions",  required=False, multiline=True)

        for f in [f1, f2, f3, f4]:
            b_lay.addWidget(f)

        self._err_lbl = QLabel("")
        self._err_lbl.setFont(inter(11))
        self._err_lbl.setStyleSheet(f"color:{RED_BTN};background:transparent;border:none;")
        self._err_lbl.hide()
        b_lay.addWidget(self._err_lbl)

        card_lay.addWidget(body)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(f"background:transparent;border:none;border-top:1px solid {GRAY_2};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(22, 14, 22, 16)
        f_lay.setSpacing(10)
        f_lay.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_btn.setFont(inter(12, QFont.Medium))
        self._cancel_btn.setFixedHeight(34)
        self._cancel_btn.setStyleSheet(f"""
            QPushButton{{color:{GRAY_5};background:{WHITE};border:1px solid {GRAY_2};border-radius:4px;padding:0 18px;}}
            QPushButton:hover{{background:{GRAY_1};}}
        """)
        self._cancel_btn.clicked.connect(self.hide)

        self._save_btn = QPushButton("Save Customer")
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.setFont(inter(12, QFont.Medium))
        self._save_btn.setFixedHeight(34)
        self._save_btn.setStyleSheet(f"""
            QPushButton{{color:{WHITE};background:{TEAL};border:1px solid {TEAL};border-radius:4px;padding:0 18px;}}
            QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
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
        self._save_btn.setText("Save Customer")
        self._clear_fields()
        self._err_lbl.hide()
        self._show_centered()

    def open_edit(self, customer_data, callback):
        self._mode     = "edit"
        self._callback = callback
        self._edit_id  = customer_data.get("id")
        self._modal_title.setText("Edit Customer Details")
        self._save_btn.setText("Update Details")
        self._err_lbl.hide()
        self.inp_name.setText(customer_data.get("full_name", ""))
        self.inp_address.setPlainText(customer_data.get("address", ""))
        self.inp_contact.setText(customer_data.get("contact_number", ""))
        self.inp_notes.setPlainText(customer_data.get("notes", ""))
        self._show_centered()

    def _show_centered(self):
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

    def _clear_fields(self):
        self.inp_name.clear()
        self.inp_address.clear()
        self.inp_contact.clear()
        self.inp_notes.clear()

    def _on_save(self):
        name    = self.inp_name.text().strip()
        address = self.inp_address.toPlainText().strip()
        contact = self.inp_contact.text().strip()
        notes   = self.inp_notes.toPlainText().strip()

        if not name:
            self._show_error("Full name is required.")
            return
        if not address:
            self._show_error("Address is required.")
            return
        if not contact:
            self._show_error("Contact number is required.")
            return

        self._err_lbl.hide()
        data = {
            "id":             self._edit_id,
            "full_name":      name,
            "address":        address,
            "contact_number": contact,
            "notes":          notes,
        }
        if self._callback:
            self._callback(data, self._mode)
        self.hide()

    def _show_error(self, msg):
        self._err_lbl.setText(msg)
        self._err_lbl.show()


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


# ── Customer page widget ──────────────────────────────────────────────────────
class CustomerView(QWidget):
    def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False):
        super().__init__(parent)
        self._show_topbar = show_topbar
        self._topbar_controls_only = topbar_controls_only
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
        scroll.setStyleSheet(owner_scrollbar_qss())

        content = QWidget()
        content.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(28, 24, 28, 28)
        c_lay.setSpacing(0)

        # Page title row
        title_row = QHBoxLayout()
        title_row.setSpacing(0)

        left = QVBoxLayout()
        left.setSpacing(0)

        sub = QLabel("CLIENT RECORDS")
        sub.setFont(inter(10, QFont.DemiBold))
        sub.setStyleSheet(f"color:{TEAL};letter-spacing:2px;background:transparent;border:none;margin-bottom:5px;")

        title = QLabel("Customers")
        title.setFont(playfair(28, QFont.Medium))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        page_sub = QLabel("Manage all customer records for G and C LPG Trading.")
        page_sub.setFont(inter(12))
        page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

        left.addWidget(sub)
        left.addWidget(title)
        left.addWidget(page_sub)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search customer by name or contact number...")
        self._search.setFont(inter(12))
        self._search.setFixedHeight(36)
        self._search.setMinimumWidth(420)
        self._search.setMaximumWidth(520)
        self._search.setStyleSheet(f"""
            QLineEdit{{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:4px;
                padding:0 10px;
            }}
            QLineEdit:focus{{border-color:{TEAL};}}
        """)
        self._search.textChanged.connect(self._on_search)

        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setStyleSheet(f"color:{GRAY_2};background:{GRAY_2};border:none;margin-bottom:6px;margin-left:24px;")

        title_row.addLayout(left)
        title_row.addWidget(rule, 1, Qt.AlignBottom)
        title_row.addWidget(self._search, 0, Qt.AlignRight | Qt.AlignTop)
        c_lay.addLayout(title_row)
        c_lay.addSpacing(22)

        self._add_btn = QPushButton("+ Add Customer")
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setFont(inter(12, QFont.Medium))
        self._add_btn.setFixedHeight(36)
        self._add_btn.setMinimumWidth(230)
        self._add_btn.setStyleSheet(f"""
            QPushButton{{color:{WHITE};background:{TEAL};border:1px solid {TEAL};border-radius:4px;padding:0 18px;}}
            QPushButton:hover{{background:{TEAL_DARK};border-color:{TEAL_DARK};}}
        """)
        self._add_btn.clicked.connect(self._open_add)
        c_lay.addSpacing(14)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self._stat_total    = self._stat_card("Total Customers",    "0", TEAL)
        self._stat_new      = self._stat_card("Added This Month",   "0", TEAL_MID)

        stats_row.addWidget(self._stat_total)
        stats_row.addWidget(self._stat_new)
        stats_row.addStretch()
        stats_row.addWidget(self._add_btn, 0, Qt.AlignBottom)
        c_lay.addLayout(stats_row)
        c_lay.addSpacing(16)

        # Table card
        table_card = QFrame()
        table_card.setMinimumHeight(520)
        table_card.setMaximumHeight(520)
        table_card.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")
        t_lay = QVBoxLayout(table_card)
        t_lay.setContentsMargins(0, 0, 0, 0)
        t_lay.setSpacing(0)

        # Table header bar
        th_bar = QWidget()
        th_bar.setFixedHeight(52)
        th_bar.setStyleSheet(f"background:transparent;border:none;border-bottom:1px solid {GRAY_2};")
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

        # Table
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels([
            "Full Name", "Address", "Contact Number", "Notes", "Date Added", "Actions"
        ])

        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self._table.setStyleSheet(f"""
            QTableView{{
                background:transparent;border:none;
                font-family:'{INTER_FAMILY}';font-size:12px;color:{GRAY_5};outline:none;
                selection-background-color:{TEAL_PALE};
            }}
            QTableView::item{{
                padding:10px 16px;
                border-bottom:0.5px solid {GRAY_2};
            }}
            QTableView::item:selected{{
                background:{TEAL_PALE};color:{TEAL_DARK};
            }}
            QHeaderView::section{{
                background:{WHITE};color:{GRAY_4};
                font-size:10px;font-weight:600;letter-spacing:1.5px;
                padding:10px 16px 8px;border:none;
                border-bottom:1px solid {GRAY_2};
                font-family:'{INTER_FAMILY}';
            }}
            QScrollBar:vertical{{
                background:transparent;
                width:10px;
                margin:8px 4px 8px 0;
            }}
            QScrollBar::handle:vertical{{
                background:rgba(26,122,110,0.28);
                min-height:28px;
                border-radius:5px;
            }}
            QScrollBar::handle:vertical:hover{{
                background:rgba(26,122,110,0.42);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{{
                height:0;
                background:transparent;
                border:none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{{
                background:transparent;
            }}
        """)
        self._table.setStyleSheet(self._table.styleSheet() + owner_scrollbar_qss())
        self._table.setItemDelegateForColumn(5, ActionDelegate(self._table, self))
        self._table.verticalHeader().setDefaultSectionSize(56)

        # Empty state
        self._empty_state = QWidget()
        self._empty_state.setStyleSheet("background:transparent;border:none;")
        es_lay = QVBoxLayout(self._empty_state)
        es_lay.setAlignment(Qt.AlignCenter)
        es_lay.setContentsMargins(0, 48, 0, 48)

        es_title = QLabel("No customers yet")
        es_title.setFont(playfair(16, QFont.Medium))
        es_title.setAlignment(Qt.AlignCenter)
        es_title.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        es_sub = QLabel("Click \"+ Add Customer\" to add your first customer.")
        es_sub.setFont(inter(12))
        es_sub.setAlignment(Qt.AlignCenter)
        es_sub.setStyleSheet(f"color:{GRAY_3};background:transparent;border:none;")

        es_lay.addSpacing(8)
        es_lay.addWidget(es_title)
        es_lay.addSpacing(4)
        es_lay.addWidget(es_sub)

        self._table_stack = QStackedWidget()
        self._table_stack.addWidget(self._table)
        self._table_stack.addWidget(self._empty_state)
        t_lay.addWidget(self._table_stack)
        c_lay.addWidget(table_card)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # Modals
        self._form_modal   = CustomerFormModal(self)
        self._delete_modal = DeleteConfirmModal(self)

        self._refresh_empty_state()

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

    def _stat_card(self, label, value, top_color):
        card_width = 460
        card_height = 80

        class PaintedCard(QFrame):
            def __init__(self, lbl, val, tc, parent=None):
                super().__init__(parent)
                self._tc = QColor(tc)
                self.setFixedSize(card_width, card_height)
                self.setStyleSheet(f"QFrame{{background:{WHITE};border:1px solid {GRAY_2};border-radius:6px;}}")
                lay = QVBoxLayout(self)
                lay.setContentsMargins(16, 10, 16, 10)
                lay.setSpacing(4)
                l = QLabel(lbl)
                l.setFont(inter(10, QFont.DemiBold))
                l.setStyleSheet(f"color:{GRAY_4};letter-spacing:1px;background:transparent;border:none;")
                self._val_lbl = QLabel(val)
                self._val_lbl.setFont(playfair(22, QFont.Medium))
                self._val_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
                lay.addWidget(l)
                lay.addWidget(self._val_lbl)

            def set_value(self, v):
                self._val_lbl.setText(str(v))

            def paintEvent(self, ev):
                super().paintEvent(ev)
                p = QPainter(self)
                p.setPen(Qt.NoPen)
                p.setBrush(self._tc)
                p.drawRoundedRect(0, 0, self.width(), 3, 1, 1)

        return PaintedCard(label, value, top_color)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _open_add(self):
        self._form_modal.open_add(self._on_form_saved)

    def _open_edit(self, row):
        data = self._get_row_data(row)
        self._form_modal.open_edit(data, self._on_form_saved)

    def _open_delete(self, row):
        data = self._get_row_data(row)
        self._delete_modal.open(data["full_name"], data["id"], self._on_delete_confirmed)

    def _on_form_saved(self, data, mode):
        if mode == "add":
            ok, res = CustomerController.add_customer(
                data.get("full_name", ""),
                data.get("address", ""),
                data.get("contact_number", ""),
                data.get("notes", ""),
            )
            if ok:
                self._append_row(res)
            else:
                self._show_error_message("Add Customer Failed", res)
        else:
            ok, res = CustomerController.update_customer(
                data.get("id"),
                data.get("full_name", ""),
                data.get("address", ""),
                data.get("contact_number", ""),
                data.get("notes", ""),
            )
            if ok:
                self._update_row(res)
            else:
                self._show_error_message("Update Customer Failed", res)
        self._refresh_counts()

    def _on_delete_confirmed(self, customer_id):
        ok, res = CustomerController.delete_customer(customer_id)
        if ok:
            for row in range(self._model.rowCount()):
                if self._model.item(row, 0).data(Qt.UserRole) == customer_id:
                    self._model.removeRow(row)
                    break
            self._refresh_counts()
        else:
            self._show_error_message("Delete Customer Failed", res)

    def _on_search(self, text):
        keyword = text.strip()
        if keyword == "":
            self._load_from_db()
            return
        ok, res = CustomerController.search_customers(keyword)
        if ok:
            self.load_customers(res)
        else:
            self._show_error_message("Search Failed", res)

    # ── Data helpers ──────────────────────────────────────────────────────────
    def _get_row_data(self, proxy_row):
        src_row = self._proxy.mapToSource(self._proxy.index(proxy_row, 0)).row()
        return {
            "id":             self._model.item(src_row, 0).data(Qt.UserRole),
            "full_name":      self._model.item(src_row, 0).text(),
            "address":        self._model.item(src_row, 1).text(),
            "contact_number": self._model.item(src_row, 2).text(),
            "notes":          self._model.item(src_row, 3).text(),
        }

    def _append_row(self, data):
        import datetime
        row_id = data.get("id") or (self._model.rowCount() + 1)
        items = [
            QStandardItem(data.get("full_name", "")),
            QStandardItem(data.get("address", "")),
            QStandardItem(data.get("contact_number", "")),
            QStandardItem(data.get("notes", "") or "—"),
            QStandardItem(datetime.date.today().strftime("%b %d, %Y")),
            QStandardItem(""),
        ]
        items[0].setData(row_id, Qt.UserRole)
        for item in items:
            item.setFont(inter(12))
            item.setForeground(QColor(GRAY_5))
        self._model.appendRow(items)
        self._refresh_empty_state()

    def _update_row(self, data):
        for row in range(self._model.rowCount()):
            if self._model.item(row, 0).data(Qt.UserRole) == data.get("id"):
                self._model.item(row, 0).setText(data.get("full_name", ""))
                self._model.item(row, 1).setText(data.get("address", ""))
                self._model.item(row, 2).setText(data.get("contact_number", ""))
                self._model.item(row, 3).setText(data.get("notes", "") or "—")
                break

    def load_customers(self, customers):
        self._model.setRowCount(0)
        for c in customers:
            self._append_row(c)
        self._refresh_counts()

    def _refresh_counts(self):
        total = self._model.rowCount()
        self._stat_total.set_value(total)
        self._count_lbl.setText(f"{self._proxy.rowCount()} record{'s' if self._proxy.rowCount() != 1 else ''}")
        self._refresh_empty_state()

    def _refresh_empty_state(self):
        has_rows = self._proxy.rowCount() > 0
        self._table_stack.setCurrentWidget(self._table if has_rows else self._empty_state)

    # --- Data loading helpers ---
    def _load_from_db(self):
        ok, res = CustomerController.list_customers()
        if ok:
            self.load_customers(res)
        else:
            self._show_error_message("Load Failed", res)

    def _show_error_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


# ── Action delegate — Edit / Delete buttons per row ───────────────────────────
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QStyle, QApplication as _QApp
from PySide6.QtCore import QRect, QSize


class ActionDelegate(QStyledItemDelegate):
    def __init__(self, table, page):
        super().__init__(table)
        self._table = table
        self._page  = page

    def paint(self, painter, option, index):
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(TEAL_PALE))

        btn_w  = 60
        btn_h  = 26
        gap    = 6
        total  = btn_w * 2 + gap
        x      = option.rect.x() + (option.rect.width() - total) // 2
        y      = option.rect.y() + (option.rect.height() - btn_h) // 2

        # Edit button
        edit_rect = QRect(x, y, btn_w, btn_h)
        painter.setPen(QColor(TEAL))
        painter.setBrush(QColor(TEAL_PALE))
        painter.drawRoundedRect(edit_rect, 4, 4)
        painter.setFont(inter(10, QFont.Medium))
        painter.setPen(QColor(TEAL_DARK))
        painter.drawText(edit_rect, Qt.AlignCenter, "Edit")

        # Delete button
        del_rect = QRect(x + btn_w + gap, y, btn_w, btn_h)
        painter.setPen(QColor(RED_BTN))
        painter.setBrush(QColor(RED_BG))
        painter.drawRoundedRect(del_rect, 4, 4)
        painter.setFont(inter(10, QFont.Medium))
        painter.setPen(QColor(RED_BTN))
        painter.drawText(del_rect, Qt.AlignCenter, "Delete")

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(140, 56)

    def editorEvent(self, event, model, option, index):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.MouseButtonRelease:
            btn_w = 60
            btn_h = 26
            gap   = 6
            total = btn_w * 2 + gap
            x     = option.rect.x() + (option.rect.width() - total) // 2
            y     = option.rect.y() + (option.rect.height() - btn_h) // 2

            pos = event.position().toPoint()
            edit_rect = QRect(x, y, btn_w, btn_h)
            del_rect  = QRect(x + btn_w + gap, y, btn_w, btn_h)

            proxy_row = index.row()
            if edit_rect.contains(pos):
                self._page._open_edit(proxy_row)
                return True
            if del_rect.contains(pos):
                self._page._open_delete(proxy_row)
                return True
        return False


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
