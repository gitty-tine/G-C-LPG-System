import sys
import os
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt, QSize, QTimer
from PySide6.QtGui import (
    QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QFontDatabase
)
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QToolButton, QVBoxLayout, QWidget
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
INTER_FAMILY = "Inter"


def load_fonts():
    """Load custom fonts from assets/fonts directory."""
    global INTER_FAMILY
    fonts_dir = os.path.join(PROJECT_ROOT, "assets", "fonts")
    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(".ttf"):
                font_path = os.path.join(fonts_dir, font_file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1 and font_file == "Inter_18pt-Regular.ttf":
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        INTER_FAMILY = families[0]

# Prefer workspace-local assets so the app runs across devices.
BG_CANDIDATES = [
    os.path.join(ASSETS_DIR, "blurred_background.png"),
    os.path.join(ASSETS_DIR, "blurred background.png"),
]
BG_IMAGE = next((p for p in BG_CANDIDATES if os.path.exists(p)), "")

TEAL      = "#1A7A6E"
TEAL_DARK = "#145F55"


class GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(60)
        self.setStyleSheet(f"""
            QPushButton {{
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 700;
                font-family: '{INTER_FAMILY}';
                border: none;
                border-radius: 10px;
                letter-spacing: 2px;
            }}
        """)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        g = QLinearGradient(0, 0, self.rect().width(), 0)
        g.setColorAt(0, QColor(TEAL))
        g.setColorAt(1, QColor(TEAL_DARK))
        p.fillPath(path, g)
        super().paintEvent(event)


class LoginView(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        from controllers.login_controller import LoginController

        self._controller = controller or LoginController()
        load_fonts()  # ensure Inter is registered even on re-open after sign out
        app = QApplication.instance()
        if app:
            app.setFont(QFont(INTER_FAMILY, 11))
        self._pw_visible = False
        self._intro_done = False
        self._bg = QPixmap(BG_IMAGE) if os.path.exists(BG_IMAGE) else None
        self.setWindowTitle("G and C LPG Trading — Delivery Scheduling & Tracking System")
        self._build_ui()
        self.showFullScreen()

    def _eye_icon(self, visible=False):
        size = 18
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(90, 98, 110), 1.7)
        painter.setPen(pen)

        # Draw an eye outline with a center pupil, plus a slash when hidden.
        path = QPainterPath()
        path.moveTo(2, size / 2)
        path.quadTo(size / 2, 2, size - 2, size / 2)
        path.quadTo(size / 2, size - 2, 2, size / 2)
        painter.drawPath(path)

        painter.setBrush(QColor(90, 98, 110))
        painter.drawEllipse(size // 2 - 2, size // 2 - 2, 4, 4)

        if not visible:
            slash = QPen(QColor(90, 98, 110), 1.7)
            painter.setPen(slash)
            painter.drawLine(3, size - 3, size - 3, 3)

        painter.end()
        return QIcon(pix)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.setStyleSheet(f"""
            * {{ font-family: '{INTER_FAMILY}'; }}

            QFrame#card {{
                background: rgba(255, 255, 255, 0.97);
                border: none;
                border-radius: 20px;
            }}

            QLabel#business {{
                color: {TEAL};
                font-size: 15px;
                font-weight: 800;
                letter-spacing: 3px;
            }}
            QLabel#sys_name {{
                color: #1A1A1A;
                font-size: 30px;
                font-weight: 800;
            }}
            QLabel#sys_loc {{
                color: #666666;
                font-size: 14px;
            }}
            QLabel#fld {{
                color: #2A2A2A;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#copyright {{
                color: rgba(255, 255, 255, 0.65);
                font-size: 12px;
            }}

            QFrame#roleSwitch {{
                background-color: #EEF4F3;
                border-radius: 10px;
                border: 1.5px solid #C8DCDA;
            }}
            QPushButton[role="true"] {{
                color: #555555;
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton[role="true"]:checked {{
                background: {TEAL};
                color: #FFFFFF;
                font-weight: 700;
            }}

            QLineEdit {{
                min-height: 58px;
                background: #F5FAFA;
                border: 1.5px solid #C0D8D5;
                border-radius: 10px;
                padding: 0 16px;
                color: #1A1A1A;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: 2px solid {TEAL};
                background: #FFFFFF;
            }}
            QLineEdit::placeholder {{ color: #BBBBBB; }}
            QLineEdit[error="true"] {{
                border: 2px solid #D64545;
                background: #FFF5F5;
            }}

            QFrame#pwWrap {{
                background: #F5FAFA;
                border: 1.5px solid #C0D8D5;
                border-radius: 10px;
            }}
            QFrame#pwWrap:focus-within {{
                border: 2px solid {TEAL};
                background: #FFFFFF;
            }}
            QFrame#pwWrap[error="true"] {{
                border: 2px solid #D64545;
                background: #FFF5F5;
            }}

            QLabel#formError {{
                color: #D64545;
                font-size: 12px;
                font-weight: 600;
            }}

            QToolButton#eye {{
                border: none;
                background: transparent;
                color: #AAAAAA;
                font-size: 16px;
                padding-right: 14px;
                min-height: 58px;
            }}
            QToolButton#eye:hover {{ color: {TEAL}; }}

            QPushButton#closeBtn {{
                color: rgba(255,255,255,0.50);
                background: transparent;
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 7px;
                font-size: 12px;
                padding: 5px 14px;
            }}
            QPushButton#closeBtn:hover {{
                color: white;
                border-color: rgba(255,255,255,0.60);
                background: rgba(255,255,255,0.08);
            }}
        """)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # top bar — close button top right
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 18, 28, 0)
        top_bar.addStretch()
        close_btn = QPushButton("✕  Close")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)
        root.addLayout(top_bar)

        root.addStretch(2)

        # ── Card ──────────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(580)
        self.card = card

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(80)
        shadow.setOffset(0, 24)
        shadow.setColor(QColor(0, 0, 0, 90))
        card.setGraphicsEffect(shadow)

        self.card_opacity = QGraphicsOpacityEffect(card)
        self.card_opacity.setOpacity(0.0)
        card.setGraphicsEffect(self.card_opacity)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(60, 52, 60, 48)
        cl.setSpacing(0)

        # Business name
        biz = QLabel("G AND C LPG TRADING")
        biz.setObjectName("business")
        biz.setAlignment(Qt.AlignCenter)
        cl.addWidget(biz)
        cl.addSpacing(12)

        # System title
        sys_name = QLabel("Delivery Scheduling &\nTracking System")
        sys_name.setObjectName("sys_name")
        sys_name.setAlignment(Qt.AlignCenter)
        sys_name.setWordWrap(True)
        cl.addWidget(sys_name)
        cl.addSpacing(8)

        # Location
        loc = QLabel("Tuy, Batangas")
        loc.setObjectName("sys_loc")
        loc.setAlignment(Qt.AlignCenter)
        cl.addWidget(loc)
        cl.addSpacing(32)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #DDE9E7;")
        cl.addWidget(div)
        cl.addSpacing(30)

        # Role switcher
        role_frame = QFrame()
        role_frame.setObjectName("roleSwitch")
        role_frame.setFixedHeight(56)
        rl = QHBoxLayout(role_frame)
        rl.setContentsMargins(6, 6, 6, 6)
        rl.setSpacing(6)

        self.owner_btn = QPushButton("Owner")
        self.owner_btn.setCheckable(True)
        self.owner_btn.setChecked(True)
        self.owner_btn.setProperty("role", True)
        self.owner_btn.setCursor(Qt.PointingHandCursor)

        self.admin_btn = QPushButton("Admin")
        self.admin_btn.setCheckable(True)
        self.admin_btn.setProperty("role", True)
        self.admin_btn.setCursor(Qt.PointingHandCursor)

        grp = QButtonGroup(self)
        grp.setExclusive(True)
        grp.addButton(self.owner_btn)
        grp.addButton(self.admin_btn)

        rl.addWidget(self.owner_btn)
        rl.addWidget(self.admin_btn)
        cl.addWidget(role_frame)
        cl.addSpacing(28)

        # Username
        ul = QLabel("USERNAME")
        ul.setObjectName("fld")
        cl.addWidget(ul)
        cl.addSpacing(8)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setProperty("error", False)
        self.username_input.textChanged.connect(self._clear_error_styles)
        cl.addWidget(self.username_input)
        cl.addSpacing(22)

        # Password
        pl = QLabel("PASSWORD")
        pl.setObjectName("fld")
        cl.addWidget(pl)
        cl.addSpacing(8)

        pw_wrap = QFrame()
        pw_wrap.setObjectName("pwWrap")
        pw_wrap.setFixedHeight(58)
        pw_wrap.setProperty("error", False)
        pw_row = QHBoxLayout(pw_wrap)
        pw_row.setContentsMargins(0, 0, 0, 0)
        pw_row.setSpacing(0)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Enter your password")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                padding-left: 16px; border-radius: 10px;
                min-height: 56px; font-size: 15px;
            }
        """)
        self.pw_input.returnPressed.connect(self.handle_login)
        self.pw_input.textChanged.connect(self._clear_error_styles)

        eye = QToolButton()
        eye.setObjectName("eye")
        eye.setIcon(self._eye_icon(False))
        eye.setIconSize(QSize(18, 18))
        eye.setCursor(Qt.PointingHandCursor)
        eye.clicked.connect(self._toggle_pw)

        pw_row.addWidget(self.pw_input)
        pw_row.addWidget(eye)
        self.pw_wrap = pw_wrap
        cl.addWidget(pw_wrap)
        self.form_error = QLabel("")
        self.form_error.setObjectName("formError")
        self.form_error.setVisible(False)
        cl.addWidget(self.form_error)
        cl.addSpacing(34)

        # Sign in button
        sign_btn = GradientButton("SIGN IN")
        sign_btn.clicked.connect(self.handle_login)
        cl.addWidget(sign_btn)

        forgot_row = QHBoxLayout()
        forgot_row.setContentsMargins(0, 8, 0, 0)
        forgot_row.addStretch()
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setFont(QFont(INTER_FAMILY, 11))
        forgot_btn.setStyleSheet(f"""
            QPushButton {{
                color: {TEAL};
                background: transparent;
                border: none;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {TEAL_DARK};
            }}
        """)
        forgot_btn.clicked.connect(self._open_forgot_password)
        forgot_row.addWidget(forgot_btn)
        cl.addLayout(forgot_row)

        root.addWidget(card, alignment=Qt.AlignHCenter)
        root.addStretch(2)

        # Copyright
        copy = QLabel("© 2026 G and C LPG Trading. All rights reserved.")
        copy.setObjectName("copyright")
        copy.setAlignment(Qt.AlignCenter)
        root.addWidget(copy)
        root.addSpacing(22)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._intro_done:
            self._intro_done = True
            QTimer.singleShot(120, self._play_intro_animation)

    def _play_intro_animation(self):
        if not hasattr(self, "card"):
            return

        start_pos = self.card.pos() + QPoint(0, 28)
        end_pos = self.card.pos()
        self.card.move(start_pos)

        fade = QPropertyAnimation(self.card_opacity, b"opacity", self)
        fade.setDuration(520)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        slide = QPropertyAnimation(self.card, b"pos", self)
        slide.setDuration(520)
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
        self.pw_input.setEchoMode(
            QLineEdit.Normal if self._pw_visible else QLineEdit.Password
        )
        button = self.sender()
        if isinstance(button, QToolButton):
            button.setIcon(self._eye_icon(self._pw_visible))

    def _set_form_error(self, message, username_error=False, password_error=False):
        self.username_input.setProperty("error", username_error)
        self.pw_wrap.setProperty("error", password_error)
        self.username_input.style().unpolish(self.username_input)
        self.username_input.style().polish(self.username_input)
        self.pw_wrap.style().unpolish(self.pw_wrap)
        self.pw_wrap.style().polish(self.pw_wrap)
        self.form_error.setText(message)
        self.form_error.setVisible(bool(message))

    def _clear_error_styles(self):
        if self.username_input.property("error") or self.pw_wrap.property("error"):
            self._set_form_error("", False, False)

    def _current_role(self):
        return "owner" if self.owner_btn.isChecked() else "admin"

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
                self._error_shake.addAnimation(self._create_shake_animation(self.username_input))
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
            role_hint=self._current_role(),
        )

        if not success:
            self._error_shake = QParallelAnimationGroup(self)
            self._error_shake.addAnimation(self._create_shake_animation(self.username_input))
            self._error_shake.addAnimation(self._create_shake_animation(self.pw_wrap))
            self._error_shake.start()
            self._set_form_error(message, username_error=True, password_error=True)
            return

        # Login success — route to appropriate dashboard based on role
        self._open_dashboard(dashboard)

    def _open_forgot_password(self):
        from views.admin_dashboard_view import ForgotPasswordModal
        if not hasattr(self, "_forgot_modal") or self._forgot_modal is None:
            self._forgot_modal = ForgotPasswordModal(self.centralWidget())
        self._forgot_modal.open()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_forgot_modal") and self._forgot_modal:
            self._forgot_modal.setGeometry(self.centralWidget().rect())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self._bg and not self._bg.isNull():
            scaled = self._bg.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width()  - scaled.width())  // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 50))
        else:
            painter.fillRect(self.rect(), QColor("#D6EDEA"))

        super().paintEvent(event)

    def keyPressEvent(self, event):
        # Allow Alt+F4 to close naturally, block Escape
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    load_fonts()  # Load custom fonts early
    app.setFont(QFont(INTER_FAMILY, 11))
    w = LoginView()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
