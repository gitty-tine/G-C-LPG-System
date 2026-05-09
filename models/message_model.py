from database.connection import get_connection


class MessageModel:
    # SQL fragment to limit threads to staff roles.
    STAFF_ROLE_SQL = "LOWER(COALESCE(role, '')) IN ('admin', 'owner')"

    @staticmethod
    def _role_label(role):
        role = str(role or "").strip().lower()
        if role == "owner":
            return "Owner"
        if role == "admin":
            return "Admin"
        return "Staff"

    @staticmethod
    def _display_name(row):
        return (
            str(row.get("full_name") or "").strip()
            or str(row.get("username") or "").strip()
            or MessageModel._role_label(row.get("role"))
        )

    @staticmethod
    def _normalize_user(row):
        # Normalize DB row into the UI-friendly shape.
        row = row or {}
        return {
            "user_id": int(row.get("user_id") or row.get("id") or 0),
            "full_name": str(row.get("full_name") or "").strip(),
            "username": str(row.get("username") or "").strip(),
            "role": str(row.get("role") or "").strip().lower(),
            "role_label": MessageModel._role_label(row.get("role")),
            "display_name": MessageModel._display_name(row),
        }

    @staticmethod
    def _normalize_message(row, current_user_id):
        row = row or {}
        sender_id = int(row.get("sender_id") or 0)
        receiver_id = int(row.get("receiver_id") or 0)
        return {
            "id": int(row.get("id") or 0),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "body": str(row.get("body") or ""),
            "created_at": row.get("created_at"),
            "created_at_fmt": row.get("created_at_fmt") or "",
            "read_at": row.get("read_at"),
            "is_from_me": sender_id == int(current_user_id or 0),
            "sender_name": str(row.get("sender_name") or "").strip() or "Staff",
        }

    @staticmethod
    def get_unread_count(user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            # Pull each staff user with latest message and unread count.
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM internal_messages
                WHERE receiver_id = %s
                  AND read_at IS NULL
                """,
                (user_id,),
            )
            row = cursor.fetchone() or {}
            return int(row.get("total") or 0)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def list_conversations(user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                f"""
                SELECT
                    u.id AS user_id,
                    TRIM(COALESCE(u.full_name, '')) AS full_name,
                    TRIM(COALESCE(u.username, '')) AS username,
                    LOWER(COALESCE(u.role, '')) AS role,
                    (
                        SELECT m.id
                        FROM internal_messages m
                        WHERE (m.sender_id = %s AND m.receiver_id = u.id)
                           OR (m.sender_id = u.id AND m.receiver_id = %s)
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT 1
                    ) AS latest_id,
                    (
                        SELECT m.sender_id
                        FROM internal_messages m
                        WHERE (m.sender_id = %s AND m.receiver_id = u.id)
                           OR (m.sender_id = u.id AND m.receiver_id = %s)
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT 1
                    ) AS latest_sender_id,
                    (
                        SELECT m.body
                        FROM internal_messages m
                        WHERE (m.sender_id = %s AND m.receiver_id = u.id)
                           OR (m.sender_id = u.id AND m.receiver_id = %s)
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT 1
                    ) AS latest_body,
                    (
                        SELECT m.created_at
                        FROM internal_messages m
                        WHERE (m.sender_id = %s AND m.receiver_id = u.id)
                           OR (m.sender_id = u.id AND m.receiver_id = %s)
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT 1
                    ) AS latest_at,
                    (
                        SELECT DATE_FORMAT(m.created_at, '%b %d, %Y %h:%i %p')
                        FROM internal_messages m
                        WHERE (m.sender_id = %s AND m.receiver_id = u.id)
                           OR (m.sender_id = u.id AND m.receiver_id = %s)
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT 1
                    ) AS latest_at_fmt,
                    (
                        SELECT COUNT(*)
                        FROM internal_messages m
                        WHERE m.sender_id = u.id
                          AND m.receiver_id = %s
                          AND m.read_at IS NULL
                    ) AS unread_count
                FROM users u
                WHERE u.id <> %s
                  AND {MessageModel.STAFF_ROLE_SQL}
                ORDER BY unread_count DESC,
                         COALESCE(latest_at, '1000-01-01') DESC,
                         full_name ASC,
                         username ASC
                """,
                (
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                    user_id,
                ),
            )
            conversations = []
            for row in cursor.fetchall():
                user = MessageModel._normalize_user(row)
                latest_body = str(row.get("latest_body") or "")
                latest_sender_id = int(row.get("latest_sender_id") or 0)
                conversations.append({
                    **user,
                    "latest_id": row.get("latest_id"),
                    "latest_body": latest_body,
                    "latest_at": row.get("latest_at"),
                    "latest_at_fmt": row.get("latest_at_fmt") or "",
                    "latest_from_me": latest_sender_id == int(user_id or 0),
                    "unread_count": int(row.get("unread_count") or 0),
                })
            return conversations
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_thread(user_id, other_user_id, limit=100):
        # Fetch most recent N messages, then return oldest-first for display.
        limit = max(1, min(int(limit or 100), 200))
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                f"""
                SELECT *
                FROM (
                    SELECT
                        m.id,
                        m.sender_id,
                        m.receiver_id,
                        m.body,
                        m.read_at,
                        m.created_at,
                        DATE_FORMAT(m.created_at, '%b %d, %Y %h:%i %p') AS created_at_fmt,
                        TRIM(COALESCE(s.full_name, s.username, 'Staff')) AS sender_name
                    FROM internal_messages m
                    INNER JOIN users s ON s.id = m.sender_id
                    WHERE (m.sender_id = %s AND m.receiver_id = %s)
                       OR (m.sender_id = %s AND m.receiver_id = %s)
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT {limit}
                ) recent_messages
                ORDER BY created_at ASC, id ASC
                """,
                (user_id, other_user_id, other_user_id, user_id),
            )
            return [
                MessageModel._normalize_message(row, user_id)
                for row in cursor.fetchall()
            ]
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def mark_thread_read(user_id, other_user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Stored procedure: validates conversation users and marks unread thread messages as read.
            cursor.callproc("sp_mark_internal_thread_read", [user_id, other_user_id])
            for result in cursor.stored_results():
                result.fetchall()
            conn.commit()
            return True
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def send_message(sender_id, receiver_id, body):
        body = str(body or "").strip()
        if not body:
            raise ValueError("Message cannot be empty.")
        if len(body) > 1000:
            raise ValueError("Message is too long. Please keep it under 1000 characters.")
        if int(sender_id or 0) == int(receiver_id or 0):
            raise ValueError("You cannot send a message to yourself.")

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            # Stored procedure: validates staff sender/receiver and creates the internal message.
            cursor.callproc("sp_send_internal_message", [sender_id, receiver_id, body])
            message_id = 0
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    message_id = int(row.get("new_message_id") or 0)
            conn.commit()
            return int(message_id or 0)
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
