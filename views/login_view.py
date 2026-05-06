import os
import sys

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRectF,
    Qt,
    QSize,
    QTimer,
)
from PySide6.QtGui import QColor, QCursor, QFont, QFontDatabase, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.error_logger import install_error_logging_hooks, log_exception

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
INTER_FAMILY = "Inter"

TEAL = "#176F63"
TEAL_DARK = "#10584F"
ERROR = "#C93F3F"
UI_SCALE = 1.0


def scaled(value):
    return max(1, int(round(value * UI_SCALE)))


def load_fonts():
    global INTER_FAMILY

    fonts_dir = os.path.join(ASSETS_DIR, "fonts")
    if not os.path.exists(fonts_dir):
        return

    for font_file in (
        "Inter_18pt-Regular.ttf",
        "Inter_18pt-Medium.ttf",
        "Inter_18pt-SemiBold.ttf",
        "Inter_24pt-Bold.ttf",
    ):
        font_path = os.path.join(fonts_dir, font_file)
        if not os.path.exists(font_path):
            continue
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1 and font_file == "Inter_18pt-Regular.ttf":
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                INTER_FAMILY = families[0]


def asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)


LOGIN_BACKGROUND = asset_path("login_background.png")
LOGIN_CHARACTER = asset_path("login_char.png")
LOGIN_LOGO = asset_path("login_firelogo.png")
LOGIN_PROFILE = asset_path("login_profile.png")
LOGIN_PASSWORD = asset_path("login_pass.png")


class ErrorLoggingApplication(QApplication):
    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except Exception as exc:
            log_exception(
                exc,
                source="qt",
                action="event_notify",
                severity="CRITICAL",
                context={
                    "receiver": repr(receiver),
                    "event_type": self._event_type(event),
                },
            )
            raise

    @staticmethod
    def _event_type(event):
        if event is None:
            return None
        try:
            return int(event.type())
        except Exception:
            return str(event.type())


class AspectImageLabel(QLabel):
    def __init__(self, path, parent=None, crop_margins=None, scale=1.0, x_offset=0, bottom_offset=0):
        super().__init__(parent)
        self._pixmap = QPixmap(path) if path and os.path.exists(path) else QPixmap()
        self._scale = scale
        self._x_offset = x_offset
        self._bottom_offset = bottom_offset
        if crop_margins and not self._pixmap.isNull():
            left, top, right, bottom = crop_margins
            width = max(1, self._pixmap.width() - left - right)
            height = max(1, self._pixmap.height() - top - bottom)
            self._pixmap = self._pixmap.copy(left, top, width, height)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background:transparent;border:none;")

    def paintEvent(self, event):
        if self._pixmap.isNull():
            return super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        target_size = QSize(
            max(1, int(self.width() * self._scale)),
            max(1, int(self.height() * self._scale)),
        )
        scaled = self._pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2 + self._x_offset
        y = self.height() - scaled.height() - self._bottom_offset
        x = max(0, min(x, self.width() - scaled.width()))
        y = max(0, min(y, self.height() - scaled.height()))
        painter.drawPixmap(x, y, scaled)


class PaintedRoundedFrame(QFrame):
    def __init__(
        self,
        fill,
        border,
        radius,
        border_width=1.0,
        error_fill=None,
        error_border=None,
        parent=None,
    ):
        super().__init__(parent)
        self._fill = QColor(fill)
        self._border = QColor(border)
        self._radius = radius
        self._border_width = border_width
        self._error_fill = QColor(error_fill) if error_fill else None
        self._error_border = QColor(error_border) if error_border else None
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;border:none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        inset = max(1.0, self._border_width / 2.0)
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)

        fill = self._fill
        border = self._border
        if self.property("error"):
            fill = self._error_fill or fill
            border = self._error_border or border

        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.fillPath(path, fill)
        painter.setPen(QPen(border, self._border_width))
        painter.drawPath(path)


class LoginButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(scaled(76))
        self.setFont(QFont(INTER_FAMILY, scaled(18), QFont.DemiBold))
        self.setStyleSheet(
            f"""
            QPushButton {{
                color:#FFFFFF;
                background:{TEAL};
                border:1px solid {TEAL_DARK};
                border-radius:{scaled(13)}px;
                font-size:{scaled(19)}px;
                letter-spacing:{scaled(6)}px;
            }}
            QPushButton:hover {{
                background:{TEAL_DARK};
            }}
            QPushButton:pressed {{
                background:#0D4942;
            }}
            """
        )


class LoginView(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        from controllers.login_controller import LoginController

        global UI_SCALE
        UI_SCALE = self._detect_reference_scale()

        self._controller = controller or LoginController()
        self._pw_visible = False
        self._intro_done = False
        self._bg = QPixmap(LOGIN_BACKGROUND) if os.path.exists(LOGIN_BACKGROUND) else QPixmap()

        load_fonts()
        app = QApplication.instance()
        if app:
            app.setFont(QFont(INTER_FAMILY, 11))

        self.setWindowTitle("G and C LPG Trading - Delivery Scheduling & Tracking System")
        self._build_ui()
        self.showFullScreen()

    def _screen_for_scaling(self):
        screen = QApplication.screenAt(QCursor.pos())
        if screen is None and self.windowHandle() is not None:
            screen = self.windowHandle().screen()
        if screen is None:
            screen = self.screen() or QApplication.primaryScreen()
        return screen

    def _detect_reference_scale(self):
        screen = self._screen_for_scaling()
        if not screen:
            return 1.0

        geometry = screen.geometry()
        scale = min(geometry.width() / 1920, geometry.height() / 1080)
        return max(0.6, min(scale, 1.4))

    def _eye_icon(self, visible=False):
        size = 20
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(86, 102, 98), 1.8))

        path = QPainterPath()
        path.moveTo(2, size / 2)
        path.quadTo(size / 2, 3, size - 2, size / 2)
        path.quadTo(size / 2, size - 3, 2, size / 2)
        painter.drawPath(path)

        painter.setBrush(QColor(86, 102, 98))
        painter.drawEllipse(size // 2 - 2, size // 2 - 2, 4, 4)

        if not visible:
            painter.setPen(QPen(QColor(86, 102, 98), 1.8))
            painter.drawLine(4, size - 4, size - 4, 4)

        painter.end()
        return QIcon(pix)

    def _asset_icon_label(self, path, size=34):
        label = QLabel()
        label.setFixedSize(scaled(52), scaled(52))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background:transparent;border:none;")
        pixmap = QPixmap(path) if os.path.exists(path) else QPixmap()
        if not pixmap.isNull():
            icon_size = scaled(size)
            label.setPixmap(pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        return label

    def _make_input(self, icon_path, placeholder, password=False):
        wrap = PaintedRoundedFrame(
            fill=QColor(255, 255, 255, 246),
            border=QColor("#4D837C"),
            radius=15,
            border_width=2.0,
            error_fill=QColor("#FFF6F6"),
            error_border=QColor(ERROR),
        )
        wrap.setObjectName("inputWrap")
        wrap.setProperty("error", False)
        wrap.setFixedHeight(scaled(80))

        row = QHBoxLayout(wrap)
        row.setContentsMargins(scaled(30), 0, scaled(22), 0)
        row.setSpacing(scaled(18))
        row.addWidget(self._asset_icon_label(icon_path))

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFrame(False)
        line_edit.setEchoMode(QLineEdit.Password if password else QLineEdit.Normal)
        line_edit.setFont(QFont(INTER_FAMILY, scaled(16)))
        line_edit.setStyleSheet(
            """
            QLineEdit {
                color:#1E2725;
                background:transparent;
                border:none;
                padding:0;
            }
            QLineEdit::placeholder {
                color:#8E9694;
            }
            """
        )
        row.addWidget(line_edit, 1)

        if password:
            eye = QToolButton()
            eye.setObjectName("eye")
            eye.setIcon(self._eye_icon(False))
            eye_size = scaled(20)
            eye.setIconSize(QSize(eye_size, eye_size))
            eye.setToolTip("Show password")
            eye.setCursor(Qt.PointingHandCursor)
            eye.clicked.connect(self._toggle_pw)
            row.addWidget(eye)
            self.eye_btn = eye

        return wrap, line_edit

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("loginCentral")
        self.setCentralWidget(central)

        self.setStyleSheet(
            f"""
            * {{
                font-family:'{INTER_FAMILY}';
                letter-spacing:0;
            }}
            QWidget#loginCentral {{
                background:transparent;
            }}
            QLabel#brand {{
                color:{TEAL};
                font-size:{scaled(25)}px;
                font-weight:800;
                letter-spacing:{scaled(8)}px;
            }}
            QLabel#title {{
                color:#050706;
                font-size:{scaled(41)}px;
                font-weight:800;
            }}
            QLabel#fieldLabel {{
                color:{TEAL_DARK};
                font-size:{scaled(19)}px;
                font-weight:800;
                letter-spacing:{scaled(1)}px;
            }}
            QLabel#formError {{
                color:{ERROR};
                font-size:{scaled(14)}px;
                font-weight:700;
            }}
            QLabel#copyright {{
                color:rgba(255,255,255,220);
                font-size:{scaled(20)}px;
                font-weight:400;
            }}
            QToolButton#eye {{
                background:transparent;
                border:none;
                padding:0 {scaled(2)}px;
                min-width:{scaled(28)}px;
            }}
            QPushButton#forgotBtn {{
                color:{TEAL_DARK};
                background:transparent;
                border:none;
                text-decoration:underline;
                font-size:{scaled(19)}px;
                font-weight:500;
            }}
            QPushButton#forgotBtn:hover {{
                color:{TEAL};
            }}
            QPushButton#closeBtn {{
                color:rgba(255,255,255,200);
                background-color:rgba(255,255,255,26);
                border:1px solid rgba(255,255,255,72);
                border-radius:7px;
                font-size:12px;
                padding:6px 14px;
            }}
            QPushButton#closeBtn:hover {{
                color:white;
                background-color:rgba(255,255,255,46);
                border-color:rgba(255,255,255,140);
            }}
            """
        )

        self.close_btn = QPushButton("Close", central)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)

        glass_frame = PaintedRoundedFrame(
            fill=QColor(255, 255, 255, 46),
            border=QColor(255, 255, 255, 225),
            radius=28,
            border_width=2.0,
            parent=central,
        )
        glass_frame.setObjectName("loginGlassFrame")
        glass_frame.setFixedSize(scaled(742), scaled(912))
        self.card = glass_frame

        self.card_opacity = QGraphicsOpacityEffect(glass_frame)
        self.card_opacity.setOpacity(0.0)
        glass_frame.setGraphicsEffect(self.card_opacity)

        glass_lay = QVBoxLayout(glass_frame)
        glass_lay.setContentsMargins(scaled(18), scaled(18), scaled(18), scaled(18))
        glass_lay.setSpacing(0)

        card = PaintedRoundedFrame(
            fill=QColor("#F7FCFB"),
            border=QColor(255, 255, 255, 235),
            radius=22,
            border_width=1.0,
            parent=glass_frame,
        )
        card.setObjectName("loginCard")
        card.setFixedSize(scaled(706), scaled(876))
        glass_lay.addWidget(card, 0, Qt.AlignCenter)

        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(scaled(54), scaled(58), scaled(54), scaled(48))
        card_lay.setSpacing(0)

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background:transparent;border:none;")
        logo.setFixedHeight(scaled(102))
        logo_pix = QPixmap(LOGIN_LOGO) if os.path.exists(LOGIN_LOGO) else QPixmap()
        if not logo_pix.isNull():
            logo_size = scaled(96)
            logo.setPixmap(logo_pix.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        card_lay.addWidget(logo)
        card_lay.addSpacing(scaled(12))

        brand = QLabel("G & C LPG TRADING")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignCenter)
        brand.setFixedHeight(scaled(34))
        card_lay.addWidget(brand)
        card_lay.addSpacing(scaled(14))

        title = QLabel("Delivery Scheduling &\nTracking System")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFixedHeight(scaled(98))
        card_lay.addWidget(title)
        card_lay.addSpacing(scaled(34))

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background:#C9DAD6;border:none;")
        card_lay.addWidget(divider)
        card_lay.addSpacing(scaled(33))

        username_label = QLabel("USERNAME")
        username_label.setObjectName("fieldLabel")
        username_label.setFixedHeight(scaled(24))
        card_lay.addWidget(username_label)
        card_lay.addSpacing(scaled(12))

        self.username_wrap, self.username_input = self._make_input(
            LOGIN_PROFILE,
            "Enter your username",
            password=False,
        )
        self.username_input.returnPressed.connect(self.handle_login)
        self.username_input.textChanged.connect(self._clear_error_styles)
        card_lay.addWidget(self.username_wrap)
        card_lay.addSpacing(scaled(32))

        password_label = QLabel("PASSWORD")
        password_label.setObjectName("fieldLabel")
        password_label.setFixedHeight(scaled(24))
        card_lay.addWidget(password_label)
        card_lay.addSpacing(scaled(12))

        self.pw_wrap, self.pw_input = self._make_input(
            LOGIN_PASSWORD,
            "Enter your password",
            password=True,
        )
        self.pw_input.returnPressed.connect(self.handle_login)
        self.pw_input.textChanged.connect(self._clear_error_styles)
        card_lay.addWidget(self.pw_wrap)

        self.form_error = QLabel("", card)
        self.form_error.setObjectName("formError")
        self.form_error.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.form_error.setWordWrap(True)
        self.form_error.setFixedHeight(scaled(42))
        self.form_error.hide()
        card_lay.addSpacing(scaled(42))

        self.sign_btn = LoginButton("LOG IN")
        self.sign_btn.clicked.connect(self.handle_login)
        card_lay.addWidget(self.sign_btn)

        forgot_row = QHBoxLayout()
        forgot_row.setContentsMargins(0, scaled(19), 0, 0)
        forgot_row.addStretch()
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setObjectName("forgotBtn")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setFixedHeight(scaled(30))
        forgot_btn.clicked.connect(self._open_forgot_password)
        forgot_row.addWidget(forgot_btn)
        forgot_row.addStretch()
        card_lay.addLayout(forgot_row)
        card_lay.addStretch(1)

        hero = QWidget()
        hero.setParent(central)
        hero.setFixedSize(scaled(900), scaled(860))
        hero.setStyleSheet("background:transparent;border:none;")
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(0, 0, 0, 0)
        hero_lay.setSpacing(0)
        self.char_label = AspectImageLabel(
            LOGIN_CHARACTER,
            scale=1.0,
        )
        self.char_label.setFixedSize(scaled(900), scaled(860))
        hero_lay.addWidget(self.char_label, 1)
        self.hero = hero

        self.copy = QLabel("\u00A9 2026 G&C LPG Trading. All rights reserved.", central)
        self.copy.setObjectName("copyright")
        self.copy.setAlignment(Qt.AlignCenter)

        self._apply_reference_geometry()
        QTimer.singleShot(0, self._apply_reference_geometry)
        QTimer.singleShot(0, self._position_form_error)

    def _apply_reference_geometry(self):
        central = self.centralWidget()
        if not central:
            return
        if not all(hasattr(self, name) for name in ("close_btn", "card", "hero", "copy")):
            return

        width = central.width()
        height = central.height()
        origin_x = max(0, (width - scaled(1920)) // 2)
        origin_y = max(0, (height - scaled(1080)) // 2)

        self.close_btn.setGeometry(width - scaled(112), origin_y + scaled(20), scaled(78), scaled(36))
        self.card.setGeometry(origin_x + scaled(236), origin_y + scaled(84), scaled(742), scaled(912))
        self.hero.setGeometry(origin_x + scaled(1015), origin_y + scaled(155), scaled(900), scaled(860))
        self.copy.setGeometry(0, height - scaled(53), width, scaled(32))
        self._position_form_error()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._intro_done:
            self._intro_done = True
            QTimer.singleShot(120, self._play_intro_animation)

    def _play_intro_animation(self):
        if not hasattr(self, "card"):
            return

        start_pos = self.card.pos() + QPoint(0, 24)
        end_pos = self.card.pos()
        self.card.move(start_pos)

        fade = QPropertyAnimation(self.card_opacity, b"opacity", self)
        fade.setDuration(480)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        slide = QPropertyAnimation(self.card, b"pos", self)
        slide.setDuration(480)
        slide.setStartValue(start_pos)
        slide.setEndValue(end_pos)
        slide.setEasingCurve(QEasingCurve.OutCubic)

        self._intro_anim = QParallelAnimationGroup(self)
        self._intro_anim.addAnimation(fade)
        self._intro_anim.addAnimation(slide)
        self._intro_anim.start()

    def _create_shake_animation(self, widget, offset=10, duration=320):
        base_pos = widget.pos()
        anim = QPropertyAnimation(widget, b"pos", self)
        anim.setDuration(duration)
        anim.setKeyValueAt(0.0, base_pos)
        anim.setKeyValueAt(0.15, base_pos + QPoint(-offset, 0))
        anim.setKeyValueAt(0.3, base_pos + QPoint(offset, 0))
        anim.setKeyValueAt(0.45, base_pos + QPoint(-offset + 3, 0))
        anim.setKeyValueAt(0.6, base_pos + QPoint(offset - 3, 0))
        anim.setKeyValueAt(0.75, base_pos + QPoint(-3, 0))
        anim.setKeyValueAt(1.0, base_pos)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        return anim

    def _toggle_pw(self):
        self._pw_visible = not self._pw_visible
        self.pw_input.setEchoMode(QLineEdit.Normal if self._pw_visible else QLineEdit.Password)
        self.eye_btn.setIcon(self._eye_icon(self._pw_visible))
        self.eye_btn.setToolTip("Hide password" if self._pw_visible else "Show password")

    def _refresh_error_style(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _set_form_error(self, message, username_error=False, password_error=False):
        self.username_wrap.setProperty("error", username_error)
        self.pw_wrap.setProperty("error", password_error)
        self._refresh_error_style(self.username_wrap)
        self._refresh_error_style(self.pw_wrap)
        message = str(message or "").strip()
        self.form_error.setText(message)
        self.form_error.setVisible(bool(message))
        self._position_form_error()
        if message:
            self.form_error.raise_()

    def _form_error_height(self, message):
        if not message:
            return 0
        line_count = max(1, message.count("\n") + 1)
        if len(message) > 90:
            line_count = max(line_count, 3)
        elif len(message) > 48:
            line_count = max(line_count, 2)
        return scaled(min(42, 22 + ((line_count - 1) * 16)))

    def _position_form_error(self):
        if not all(hasattr(self, name) for name in ("form_error", "pw_wrap", "sign_btn")):
            return

        width = self.pw_wrap.width()
        x = self.pw_wrap.x()
        y = self.pw_wrap.y() + self.pw_wrap.height() + scaled(7)
        height = self._form_error_height(self.form_error.text())
        button_y = self.sign_btn.y()

        if width <= 0:
            width = scaled(598)
        if height <= 0:
            height = scaled(34)
        if button_y > y:
            height = min(height, max(scaled(14), button_y - y - scaled(3)))

        self.form_error.setGeometry(x, y, width, height)

    def _clear_error_styles(self):
        if self.username_wrap.property("error") or self.pw_wrap.property("error"):
            self._set_form_error("", False, False)

    def _open_dashboard(self, dashboard):
        self.dashboard = dashboard
        self.dashboard.show()
        self.close()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.pw_input.text().strip()
        self._set_form_error("", False, False)

        if not username or not password:
            self._error_shake = QParallelAnimationGroup(self)
            if not username:
                self.username_input.setFocus()
                self._error_shake.addAnimation(self._create_shake_animation(self.username_wrap))
            if not password:
                if username:
                    self.pw_input.setFocus()
                self._error_shake.addAnimation(self._create_shake_animation(self.pw_wrap))
            self._error_shake.start()
            self._set_form_error(
                "Please enter your username and password.",
                username_error=not username,
                password_error=not password,
            )
            return

        success, message, dashboard = self._controller.handle_login(
            username=username,
            password=password,
        )

        if not success:
            self._error_shake = QParallelAnimationGroup(self)
            self._error_shake.addAnimation(self._create_shake_animation(self.username_wrap))
            self._error_shake.addAnimation(self._create_shake_animation(self.pw_wrap))
            self._error_shake.start()
            self._set_form_error(message, username_error=True, password_error=True)
            return

        self._open_dashboard(dashboard)

    def _open_forgot_password(self):
        from views.admin_dashboard_view import ForgotPasswordModal

        if not hasattr(self, "_forgot_modal") or self._forgot_modal is None:
            self._forgot_modal = ForgotPasswordModal(self.centralWidget())
        self._forgot_modal.open()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_reference_geometry()
        if hasattr(self, "_forgot_modal") and self._forgot_modal:
            self._forgot_modal.setGeometry(self.centralWidget().rect())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if not self._bg.isNull():
            scaled = self._bg.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(self.rect(), QColor(18, 97, 87, 28))
        else:
            painter.fillRect(self.rect(), QColor("#D9EFEC"))

        super().paintEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)


def main():
    install_error_logging_hooks()
    app = ErrorLoggingApplication(sys.argv)
    load_fonts()
    app.setFont(QFont(INTER_FAMILY, 11))
    view = LoginView()
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
