import os

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESSAGE_ICON_PATH = os.path.join(BASE_DIR, "assets", "message_icon.png")

TEAL = "#1A7A6E"
TEAL_DARK = "#145F55"
TEAL_LIGHT = "#2aa898"
TEAL_PALE = "#e8f5f3"
TEAL_PALE2 = "#d0ede9"
WHITE = "#ffffff"
GRAY_1 = "#f4f5f4"
GRAY_2 = "#e6eae9"
GRAY_3 = "#c4ccc9"
GRAY_4 = "#7a8a87"
GRAY_5 = "#3a4a47"
RED = "#8a1a1a"


def ui_font(size, weight=QFont.Normal):
    font = QFont("Inter", int(size or 11))
    font.setWeight(weight)
    return font


def _shorten(text, limit=68):
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return f"{text[:max(0, limit - 3)]}..."


class MessageIconButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)
        if os.path.exists(MESSAGE_ICON_PATH):
            self.setIcon(QIcon(MESSAGE_ICON_PATH))
            self.setIconSize(QSize(19, 19))
        else:
            self.setText("M")
            self.setFont(ui_font(12, QFont.DemiBold))
        self.setStyleSheet(f"""
            QPushButton {{
                color:{GRAY_4};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:6px;
            }}
            QPushButton:hover {{
                background:{TEAL_PALE};border-color:{TEAL_LIGHT};
            }}
        """)

        self._badge = QLabel(self)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._badge.setFont(ui_font(7, QFont.DemiBold))
        self._badge.setFixedSize(18, 18)
        self._badge.setStyleSheet(f"""
            QLabel {{
                color:{WHITE};background:{RED};
                border:2px solid {WHITE};border-radius:9px;
            }}
        """)
        self._badge.hide()
        self.set_unread_count(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._badge.move(self.width() - self._badge.width() - 1, 1)
        self._badge.raise_()

    def set_unread_count(self, count):
        try:
            count = int(count or 0)
        except (TypeError, ValueError):
            count = 0
        if count <= 0:
            self._badge.hide()
            self.setToolTip("No unread messages")
            return
        self._badge.setText("9+" if count > 9 else str(count))
        self._badge.show()
        self._badge.raise_()
        self.setToolTip(f"{count} unread message{'s' if count != 1 else ''}")


class ConversationRow(QFrame):
    def __init__(self, conversation, active=False, on_clicked=None, parent=None):
        super().__init__(parent)
        self._conversation = conversation or {}
        self._on_clicked = on_clicked
        unread = int(self._conversation.get("unread_count") or 0)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("conversationRow")
        bg = TEAL_PALE if active else WHITE
        border = TEAL_PALE2 if active or unread else GRAY_2
        self.setStyleSheet(f"""
            QFrame#conversationRow {{
                background:{bg};
                border:1px solid {border};
                border-radius:7px;
            }}
            QFrame#conversationRow:hover {{
                background:{TEAL_PALE};
                border-color:{TEAL_LIGHT};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 9, 10, 9)
        root.setSpacing(9)

        avatar = QLabel(self._initials())
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(ui_font(10, QFont.DemiBold))
        avatar.setStyleSheet(f"""
            color:{WHITE};background:{TEAL};
            border:none;border-radius:17px;
        """)
        root.addWidget(avatar, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        name = QLabel(str(self._conversation.get("display_name") or "Staff"))
        name.setFont(ui_font(10, QFont.DemiBold if unread else QFont.Medium))
        name.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")

        role = QLabel(str(self._conversation.get("role_label") or "Staff"))
        role.setFont(ui_font(8))
        role.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")

        latest = self._latest_text()
        preview = QLabel(latest)
        preview.setFont(ui_font(9, QFont.Medium if unread else QFont.Normal))
        preview.setStyleSheet(f"color:{GRAY_5};background:transparent;border:none;")

        text_col.addWidget(name)
        text_col.addWidget(role)
        text_col.addWidget(preview)
        root.addLayout(text_col, 1)

        side_col = QVBoxLayout()
        side_col.setContentsMargins(0, 0, 0, 0)
        side_col.setSpacing(5)
        side_col.setAlignment(Qt.AlignRight | Qt.AlignTop)

        time_lbl = QLabel(str(self._conversation.get("latest_at_fmt") or ""))
        time_lbl.setFont(ui_font(7))
        time_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
        time_lbl.setAlignment(Qt.AlignRight)
        side_col.addWidget(time_lbl)

        if unread:
            badge = QLabel("9+" if unread > 9 else str(unread))
            badge.setAlignment(Qt.AlignCenter)
            badge.setFont(ui_font(7, QFont.DemiBold))
            badge.setFixedSize(20, 18)
            badge.setStyleSheet(f"""
                color:{WHITE};background:{RED};
                border:none;border-radius:9px;
            """)
            side_col.addWidget(badge, 0, Qt.AlignRight)
        else:
            side_col.addStretch()
        root.addLayout(side_col)

    def _initials(self):
        name = str(self._conversation.get("display_name") or "S").strip()
        pieces = [part for part in name.split() if part]
        initials = "".join(part[0].upper() for part in pieces[:2])
        return initials or "S"

    def _latest_text(self):
        body = self._conversation.get("latest_body")
        if not body:
            return "No messages yet"
        prefix = "You: " if self._conversation.get("latest_from_me") else ""
        return _shorten(f"{prefix}{body}", 48)

    def mousePressEvent(self, event):
        if self._on_clicked is not None:
            self._on_clicked(self._conversation)
            event.accept()
            return
        super().mousePressEvent(event)


class MessageBubble(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        message = message or {}
        is_me = bool(message.get("is_from_me"))

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        if is_me:
            root.addStretch()

        bubble = QFrame()
        bubble.setObjectName("messageBubble")
        bubble.setMaximumWidth(330)
        bg = TEAL if is_me else GRAY_1
        fg = WHITE if is_me else GRAY_5
        border = TEAL if is_me else GRAY_2
        bubble.setStyleSheet(f"""
            QFrame#messageBubble {{
                background:{bg};
                border:1px solid {border};
                border-radius:8px;
            }}
        """)
        lay = QVBoxLayout(bubble)
        lay.setContentsMargins(12, 9, 12, 8)
        lay.setSpacing(5)

        body = QLabel(str(message.get("body") or ""))
        body.setWordWrap(True)
        body.setFont(ui_font(10))
        body.setStyleSheet(f"color:{fg};background:transparent;border:none;")
        lay.addWidget(body)

        meta = QLabel(str(message.get("created_at_fmt") or ""))
        meta.setFont(ui_font(7))
        meta.setAlignment(Qt.AlignRight)
        meta.setStyleSheet(
            f"color:{'#d9f0ed' if is_me else GRAY_4};background:transparent;border:none;"
        )
        lay.addWidget(meta)

        root.addWidget(bubble)
        if not is_me:
            root.addStretch()


class MessagingPanel(QFrame):
    def __init__(self, controller, on_unread_changed=None, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._on_unread_changed = on_unread_changed
        self._conversations = []
        self._active_conversation = None
        self._active_user_id = None

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("messagePanel")
        self.setFixedSize(720, 520)
        self.setStyleSheet(f"""
            QFrame#messagePanel {{
                background:{WHITE};
                border:1px solid #dfe7e5;
                border-radius:8px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_body(), 1)

    def _build_header(self):
        header = QWidget()
        header.setFixedHeight(62)
        header.setStyleSheet(
            f"background:#fbfdfc;border:none;border-bottom:1px solid {GRAY_2};"
            "border-top-left-radius:8px;border-top-right-radius:8px;"
        )
        lay = QHBoxLayout(header)
        lay.setContentsMargins(18, 10, 12, 10)
        lay.setSpacing(8)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(1)
        title = QLabel("Messages")
        title.setFont(ui_font(14, QFont.DemiBold))
        title.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        self._subtitle_lbl = QLabel("Staff conversations")
        self._subtitle_lbl.setFont(ui_font(9))
        self._subtitle_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
        title_col.addWidget(title)
        title_col.addWidget(self._subtitle_lbl)
        lay.addLayout(title_col, 1)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setCursor(Qt.PointingHandCursor)
        self._refresh_btn.setFixedHeight(30)
        self._refresh_btn.setFont(ui_font(9, QFont.Medium))
        self._refresh_btn.setStyleSheet(self._small_button_qss())
        self._refresh_btn.clicked.connect(self.refresh)
        lay.addWidget(self._refresh_btn)

        close_btn = QPushButton("x")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(30, 30)
        close_btn.setFont(ui_font(11, QFont.DemiBold))
        close_btn.setStyleSheet(self._small_button_qss())
        close_btn.clicked.connect(self.hide)
        lay.addWidget(close_btn)
        return header

    def _build_body(self):
        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        lay = QHBoxLayout(body)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        conv_pane = QFrame()
        conv_pane.setFixedWidth(260)
        conv_pane.setStyleSheet(f"background:{WHITE};border:none;border-right:1px solid {GRAY_2};")
        conv_lay = QVBoxLayout(conv_pane)
        conv_lay.setContentsMargins(10, 10, 10, 10)
        conv_lay.setSpacing(8)

        self._conversation_scroll = QScrollArea()
        self._conversation_scroll.setWidgetResizable(True)
        self._conversation_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._conversation_scroll.setStyleSheet(self._scroll_qss())
        self._conversation_list = QWidget()
        self._conversation_list.setStyleSheet("background:transparent;border:none;")
        self._conversation_lay = QVBoxLayout(self._conversation_list)
        self._conversation_lay.setContentsMargins(0, 0, 0, 0)
        self._conversation_lay.setSpacing(8)
        self._conversation_scroll.setWidget(self._conversation_list)
        conv_lay.addWidget(self._conversation_scroll)
        lay.addWidget(conv_pane)

        chat_pane = QWidget()
        chat_pane.setStyleSheet("background:transparent;border:none;")
        chat_lay = QVBoxLayout(chat_pane)
        chat_lay.setContentsMargins(0, 0, 0, 0)
        chat_lay.setSpacing(0)

        chat_header = QWidget()
        chat_header.setFixedHeight(58)
        chat_header.setStyleSheet(f"background:{WHITE};border:none;border-bottom:1px solid {GRAY_2};")
        ch_lay = QVBoxLayout(chat_header)
        ch_lay.setContentsMargins(16, 9, 16, 8)
        ch_lay.setSpacing(1)
        self._active_name_lbl = QLabel("Select a conversation")
        self._active_name_lbl.setFont(ui_font(12, QFont.DemiBold))
        self._active_name_lbl.setStyleSheet(f"color:{TEAL_DARK};background:transparent;border:none;")
        self._active_role_lbl = QLabel("Choose a staff member from the left")
        self._active_role_lbl.setFont(ui_font(9))
        self._active_role_lbl.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
        ch_lay.addWidget(self._active_name_lbl)
        ch_lay.addWidget(self._active_role_lbl)
        chat_lay.addWidget(chat_header)

        self._message_scroll = QScrollArea()
        self._message_scroll.setWidgetResizable(True)
        self._message_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._message_scroll.setStyleSheet(self._scroll_qss())
        self._message_list = QWidget()
        self._message_list.setStyleSheet(f"background:{WHITE};border:none;")
        self._message_lay = QVBoxLayout(self._message_list)
        self._message_lay.setContentsMargins(16, 14, 16, 14)
        self._message_lay.setSpacing(10)
        self._message_scroll.setWidget(self._message_list)
        chat_lay.addWidget(self._message_scroll, 1)

        composer = QWidget()
        composer.setFixedHeight(92)
        composer.setStyleSheet(f"background:#fbfdfc;border:none;border-top:1px solid {GRAY_2};")
        comp_lay = QHBoxLayout(composer)
        comp_lay.setContentsMargins(14, 12, 14, 12)
        comp_lay.setSpacing(10)

        self._message_input = QTextEdit()
        self._message_input.setAcceptRichText(False)
        self._message_input.setPlaceholderText("Type a message")
        self._message_input.setFixedHeight(58)
        self._message_input.setFont(ui_font(10))
        self._message_input.setStyleSheet(f"""
            QTextEdit {{
                color:{GRAY_5};background:{WHITE};
                border:1px solid {GRAY_2};border-radius:7px;
                padding:8px;
            }}
            QTextEdit:focus {{
                border-color:{TEAL_LIGHT};
            }}
        """)
        comp_lay.addWidget(self._message_input, 1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setCursor(Qt.PointingHandCursor)
        self._send_btn.setFixedSize(78, 42)
        self._send_btn.setFont(ui_font(10, QFont.DemiBold))
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                color:{WHITE};background:{TEAL};
                border:1px solid {TEAL};border-radius:7px;
            }}
            QPushButton:hover {{
                background:{TEAL_DARK};border-color:{TEAL_DARK};
            }}
            QPushButton:disabled {{
                color:{GRAY_4};background:{GRAY_1};border-color:{GRAY_2};
            }}
        """)
        self._send_btn.clicked.connect(self._send_message)
        comp_lay.addWidget(self._send_btn, 0, Qt.AlignBottom)
        chat_lay.addWidget(composer)
        lay.addWidget(chat_pane, 1)

        self._set_composer_enabled(False)
        self._render_empty_thread("Select a conversation to start messaging.")
        return body

    def _small_button_qss(self):
        return f"""
            QPushButton {{
                color:{TEAL_DARK};background:{TEAL_PALE};
                border:1px solid {TEAL_PALE2};border-radius:6px;
                padding:0 10px;
            }}
            QPushButton:hover {{
                background:{TEAL_PALE2};border-color:{TEAL_LIGHT};
            }}
        """

    def _scroll_qss(self):
        return f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 0;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {TEAL};
                min-height: 28px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {TEAL_LIGHT};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
                background: transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _set_composer_enabled(self, enabled):
        self._message_input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)

    def _conversation_by_id(self, user_id):
        try:
            user_id = int(user_id or 0)
        except (TypeError, ValueError):
            user_id = 0
        for conversation in self._conversations:
            if int(conversation.get("user_id") or 0) == user_id:
                return conversation
        return None

    def _set_unread_count(self, count):
        if self._on_unread_changed is not None:
            self._on_unread_changed(int(count or 0))

    def refresh(self):
        if self._active_user_id:
            self.open_conversation(self._active_conversation or {"user_id": self._active_user_id})
            return
        self.refresh_conversations()

    def refresh_conversations(self):
        success, result = self._controller.list_conversations()
        if not success:
            self._render_conversation_error(result)
            self._set_unread_count(0)
            return False
        self._conversations = list(result or [])
        self._render_conversations()
        self._set_unread_count(
            sum(int(item.get("unread_count") or 0) for item in self._conversations)
        )
        return True

    def refresh_unread_badge(self):
        success, result = self._controller.unread_count()
        if success:
            self._set_unread_count(int(result or 0))
        else:
            self._set_unread_count(0)
        return success

    def _render_conversation_error(self, message):
        self._clear_layout(self._conversation_lay)
        lbl = QLabel(str(message or "Unable to load messages."))
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(ui_font(10))
        lbl.setStyleSheet(f"color:{RED};background:transparent;border:none;")
        self._conversation_lay.addWidget(lbl)
        self._conversation_lay.addStretch()

    def _render_conversations(self):
        self._clear_layout(self._conversation_lay)
        if not self._conversations:
            empty = QLabel("No other staff accounts found.")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            empty.setFont(ui_font(10))
            empty.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
            self._conversation_lay.addWidget(empty)
            self._conversation_lay.addStretch()
            return

        for conversation in self._conversations:
            user_id = int(conversation.get("user_id") or 0)
            self._conversation_lay.addWidget(
                ConversationRow(
                    conversation,
                    active=user_id == self._active_user_id,
                    on_clicked=self.open_conversation,
                )
            )
        self._conversation_lay.addStretch()

    def _render_empty_thread(self, message):
        self._clear_layout(self._message_lay)
        empty = QLabel(message)
        empty.setWordWrap(True)
        empty.setAlignment(Qt.AlignCenter)
        empty.setFont(ui_font(10))
        empty.setMinimumHeight(220)
        empty.setStyleSheet(f"color:{GRAY_4};background:transparent;border:none;")
        self._message_lay.addWidget(empty)
        self._message_lay.addStretch()

    def _render_thread(self, messages):
        self._clear_layout(self._message_lay)
        if not messages:
            self._render_empty_thread("No messages yet.")
            return
        for message in messages:
            self._message_lay.addWidget(MessageBubble(message))
        self._message_lay.addStretch()
        QTimer.singleShot(0, self._scroll_messages_to_bottom)

    def _scroll_messages_to_bottom(self):
        bar = self._message_scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def open_conversation(self, conversation):
        conversation = conversation or {}
        other_user_id = int(conversation.get("user_id") or 0)
        if other_user_id <= 0:
            return
        self._active_user_id = other_user_id
        self._active_conversation = conversation
        self._active_name_lbl.setText(str(conversation.get("display_name") or "Staff"))
        self._active_role_lbl.setText(str(conversation.get("role_label") or "Staff"))
        self._set_composer_enabled(True)

        success, result = self._controller.open_conversation(other_user_id)
        if not success:
            self._render_empty_thread(str(result or "Unable to open conversation."))
            return
        self._render_thread(list(result or []))
        self.refresh_conversations()
        updated = self._conversation_by_id(other_user_id)
        if updated:
            self._active_conversation = updated
            self._active_name_lbl.setText(str(updated.get("display_name") or "Staff"))
            self._active_role_lbl.setText(str(updated.get("role_label") or "Staff"))

    def _send_message(self):
        if not self._active_user_id:
            return
        body = self._message_input.toPlainText().strip()
        if not body:
            self._message_input.setFocus()
            return
        self._send_btn.setEnabled(False)
        success, result = self._controller.send_message(self._active_user_id, body)
        self._send_btn.setEnabled(True)
        if not success:
            self._render_empty_thread(str(result or "Unable to send message."))
            return
        self._message_input.clear()
        self.open_conversation(
            self._active_conversation or {"user_id": self._active_user_id}
        )
        self._message_input.setFocus()

    def _position_for_anchor(self, anchor, gap=8, margin=8):
        self.adjustSize()
        anchor_top_left = anchor.mapToGlobal(QPoint(0, 0))
        anchor_bottom_right = anchor.mapToGlobal(QPoint(anchor.width(), anchor.height()))
        screen = QApplication.screenAt(anchor_bottom_right)
        if screen is None and anchor.window() is not None:
            screen = anchor.window().screen()
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return QPoint(anchor_bottom_right.x() - self.width(), anchor_bottom_right.y() + gap)

        available = screen.availableGeometry()
        width = self.width()
        height = self.height()

        min_x = available.left() + margin
        max_x = available.right() - width - margin + 1
        x = anchor_bottom_right.x() - width
        x = min_x if max_x < min_x else min(max(x, min_x), max_x)

        min_y = available.top() + margin
        max_y = available.bottom() - height - margin + 1
        y = anchor_bottom_right.y() + gap
        if y > max_y:
            y = anchor_top_left.y() - height - gap
        y = min_y if max_y < min_y else min(max(y, min_y), max_y)
        return QPoint(x, y)

    def show_for(self, anchor):
        self.refresh_conversations()
        self.move(self._position_for_anchor(anchor))
        self.show()
        self.raise_()
        if self._active_user_id:
            self._message_input.setFocus()
