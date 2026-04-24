import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt, QTimer, QDate, QTime, Signal, Slot
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
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
    QGridLayout,
    QStackedWidget,
    QMessageBox,
)

from views.admin_dashboard_view import owner_scrollbar_qss

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
PRODUCT_ICON_PATH = os.path.join(BASE_DIR, "assets", "lpg_product_icon.png")
NO_PRODUCTS_IMAGE = os.path.join(BASE_DIR, "assets", "gnc_icon.png")

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


class ProductCard(QFrame):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self._product = product
        self.setMinimumHeight(340)
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

        size_text = product.get("cylinder_size") or "LPG"
        kg_chip = QLabel(self._kg_badge_text(size_text))
        kg_chip.setFont(inter(9, QFont.DemiBold))
        kg_chip.setStyleSheet(
            f"color:{TEAL_DARK};background:{TEAL_PALE};border:1px solid #cde6e1;border-radius:11px;padding:3px 8px;"
        )

        ro_chip = QLabel("READ ONLY")
        ro_chip.setFont(inter(8, QFont.DemiBold))
        ro_chip.setStyleSheet(
            f"color:{GRAY_4};background:#f1f3f2;border:1px solid #dde2e0;border-radius:10px;padding:3px 8px;"
        )

        top_row.addWidget(kg_chip)
        top_row.addStretch()
        top_row.addWidget(ro_chip)

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

        lay.addWidget(icon_box)
        lay.addWidget(name_lbl)
        lay.addLayout(price_row)
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

    def _kg_badge_text(self, name):
        return str(name or "LPG").upper()

    def _format_price(self, value):
        try:
            return f"Php {float(value):,.2f}"
        except (TypeError, ValueError):
            return "Php 0.00"


class ProductView(QWidget):
    """Presentation-only product grid; delegates data fetching to a controller via signals."""

    # Emits whenever the view needs (re)loaded data. Controller should respond by calling set_products.
    productsRequested = Signal(str)  # keyword (empty string means full list)

    def __init__(self, parent=None, show_topbar=True, topbar_controls_only=False, controller=None):
        super().__init__(parent)
        self._show_topbar = show_topbar
        self._topbar_controls_only = topbar_controls_only
        self._products = []

        load_fonts()
        self.setStyleSheet(f"background:{GRAY_1};")
        self._build_ui()

        # Allow optional controller injection for convenience; keeps view logic passive.
        if controller is not None:
            self.bind_controller(controller)

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

        page_sub = QLabel("Admin read-only product board. Owner price updates are reflected here after sync.")
        page_sub.setFont(inter(12))
        page_sub.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;margin-top:4px;")

        left.addWidget(sub)
        left.addWidget(title)
        left.addWidget(page_sub)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search products...")
        self._search.setFont(inter(12))
        self._search.setFixedHeight(36)
        self._search.setMinimumWidth(360)
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

        c_lay.addLayout(title_row)
        c_lay.addSpacing(18)

        list_head = QWidget()
        list_head.setStyleSheet("background:transparent;border:none;")
        lh_lay = QHBoxLayout(list_head)
        lh_lay.setContentsMargins(0, 0, 0, 10)

        self._count_lbl = QLabel("0 products")
        self._count_lbl.setFont(inter(11))
        self._count_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        lh_lay.addStretch()
        lh_lay.addWidget(self._count_lbl)
        c_lay.addWidget(list_head)

        self._grid_wrap = QWidget()
        self._grid_wrap.setStyleSheet("background:transparent;border:none;")
        self._grid = QGridLayout(self._grid_wrap)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(14)
        self._grid.setVerticalSpacing(14)
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
                target_w,
                target_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
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

    def _on_search(self, text):
        # The view only emits intent; controller decides how to respond (filter, fetch, etc.).
        keyword = (text or "").strip()
        self.productsRequested.emit(keyword)

    def set_products(self, products):
        """Controller-facing entry point to display a product list."""
        self._products = list(products or [])
        self._render_grid()
        self._count_lbl.setText(f"{len(self._products)} products")
        self._refresh_empty_state()
        self._list_stack.setCurrentWidget(self._grid_wrap if self._products else self._empty_state)

    # Backward-compatible alias for older callers.
    def load_products(self, products):
        self.set_products(products)

    def _render_grid(self):
        self._clear_layout(self._grid)

        if not self._products:
            return

        columns = 4

        for i, product in enumerate(self._products):
            row = i // columns
            col = i % columns
            self._grid.addWidget(ProductCard(product), row, col)

        self._grid.setColumnStretch(columns, 1)

    def _refresh_empty_state(self):
        keyword = self._search.text().strip()
        if keyword:
            self._empty_title.setText("No matching products")
            self._empty_sub.setText(
                f'No product matched "{keyword}". Try a different product name.'
            )
            return

        self._empty_title.setText("No products available")
        self._empty_sub.setText("Nothing to show here yet. Add a product to get started.")

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

    def _show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(str(message))
        msg.exec()

    # Public helper so controllers can surface problems without reaching into internals.
    def show_error(self, title, message):
        self._show_error(title, message)

    def reset_view_state(self):
        if self._search.text():
            self._search.blockSignals(True)
            self._search.clear()
            self._search.blockSignals(False)
        self.productsRequested.emit("")

    def bind_controller(self, controller, request_initial=True):
        """Connect controller slots to view signals without hard dependencies.

        Expected controller interface:
            - slot or callable: on_products_requested(keyword: str) -> None
            - method: set_products(products) is called by the controller using view.set_products
        """
        if hasattr(controller, "on_products_requested"):
            self.productsRequested.connect(controller.on_products_requested)
            if request_initial:
                self.productsRequested.emit("")
        return controller


def main():
    app = QApplication(sys.argv)
    load_fonts()
    app.setFont(inter(11))
    win = ProductView(show_topbar=True)

    class _ProductControllerAdapter:
        """Minimal bridge so the preview window still loads data via ProductController."""

        @Slot(str)
        def on_products_requested(self, keyword):
            try:
                from controllers.product_controller import ProductController
            except Exception as exc:  # pragma: no cover - defensive fallback for preview mode
                win.show_error("Load Failed", exc)
                return

            if keyword:
                ok, res = ProductController.search_products(keyword)
            else:
                ok, res = ProductController.list_products()

            if ok:
                win.set_products(res)
            else:
                win.show_error("Load Failed", res)

    adapter = _ProductControllerAdapter()
    win.bind_controller(adapter)
    win.productsRequested.emit("")
    win.resize(1320, 840)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
