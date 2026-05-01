from database.connection import get_connection


class NotificationModel:
    TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS notification_reads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            notification_key VARCHAR(160) NOT NULL,
            read_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uq_notification_reads_user_key (user_id, notification_key),
            KEY idx_notification_reads_user_read_at (user_id, read_at)
        )
    """

    TABLE_LABELS = {
        "customers": "Customer",
        "deliveries": "Delivery",
        "lpg_products": "LPG product",
        "transactions": "Transaction",
        "users": "User",
    }

    ACTION_LABELS = {
        "INSERT": "added",
        "UPDATE": "updated",
        "DELETE": "deleted",
    }

    TABLE_ACTIONS = {
        "customers": "customers",
        "deliveries": "deliveries",
        "lpg_products": "products",
        "transactions": "transactions",
        "users": "audit_logs",
    }

    @staticmethod
    def _ensure_table(cursor):
        cursor.execute(NotificationModel.TABLE_SQL)

    @staticmethod
    def _plural(count, singular, plural=None):
        return singular if int(count or 0) == 1 else (plural or f"{singular}s")

    @staticmethod
    def _money(value):
        try:
            return f"PHP {float(value or 0):,.2f}"
        except (TypeError, ValueError):
            return "PHP 0.00"

    @staticmethod
    def _current_stamp(cursor):
        cursor.execute("SELECT NOW() AS current_at, DATE_FORMAT(NOW(), '%b %d, %Y %h:%i %p') AS current_at_fmt")
        row = cursor.fetchone() or {}
        return row.get("current_at"), row.get("current_at_fmt")

    @staticmethod
    def _summary_notification(key, title, message, category, severity, action, created_at, created_at_fmt):
        return {
            "key": key,
            "title": title,
            "message": message,
            "category": category,
            "severity": severity,
            "action": action,
            "created_at": created_at,
            "created_at_fmt": created_at_fmt,
            "source": "summary",
        }

    @staticmethod
    def _fetch_overdue_delivery_alert(cursor, created_at, created_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                MIN(schedule_date) AS oldest_date,
                DATEDIFF(CURDATE(), MIN(schedule_date)) AS oldest_days
            FROM deliveries
            WHERE schedule_date < CURDATE()
              AND LOWER(REPLACE(status, ' ', '_')) NOT IN ('delivered', 'cancelled')
        """)
        row = cursor.fetchone() or {}
        total = int(row.get("total") or 0)
        if total <= 0:
            return None

        days = int(row.get("oldest_days") or 0)
        day_text = f"{days} {NotificationModel._plural(days, 'day')} overdue"
        return NotificationModel._summary_notification(
            f"summary:overdue-deliveries:{total}:{row.get('oldest_date')}",
            "Overdue deliveries",
            f"{total} {NotificationModel._plural(total, 'delivery', 'deliveries')} past schedule still need status updates. Oldest is {day_text}.",
            "Deliveries",
            "high",
            "deliveries",
            created_at,
            created_at_fmt,
        )

    @staticmethod
    def _fetch_today_delivery_alert(cursor, created_at, created_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN LOWER(REPLACE(status, ' ', '_')) = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                SUM(CASE WHEN LOWER(REPLACE(status, ' ', '_')) IN ('in_transit', 'on_delivery') THEN 1 ELSE 0 END) AS transit_count
            FROM deliveries
            WHERE schedule_date = CURDATE()
              AND LOWER(REPLACE(status, ' ', '_')) IN ('pending', 'in_transit', 'on_delivery')
        """)
        row = cursor.fetchone() or {}
        total = int(row.get("total") or 0)
        if total <= 0:
            return None

        pending = int(row.get("pending_count") or 0)
        transit = int(row.get("transit_count") or 0)
        return NotificationModel._summary_notification(
            f"summary:today-open-deliveries:{total}:{pending}:{transit}",
            "Today's open deliveries",
            f"{pending} pending and {transit} in transit for today.",
            "Deliveries",
            "normal",
            "deliveries",
            created_at,
            created_at_fmt,
        )

    @staticmethod
    def _fetch_unpaid_transaction_alert(cursor, created_at, created_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                ROUND(COALESCE(SUM(t.total_amount), 0), 2) AS total_amount
            FROM transactions t
            INNER JOIN deliveries d ON d.id = t.delivery_id
            WHERE LOWER(COALESCE(t.payment_status, 'unpaid')) = 'unpaid'
              AND LOWER(REPLACE(d.status, ' ', '_')) = 'delivered'
        """)
        row = cursor.fetchone() or {}
        total = int(row.get("total") or 0)
        amount = row.get("total_amount") or 0
        if total <= 0:
            return None

        return NotificationModel._summary_notification(
            f"summary:unpaid-delivered:{total}:{amount}",
            "Unpaid delivered transactions",
            f"{total} delivered {NotificationModel._plural(total, 'transaction')} remain unpaid, totaling {NotificationModel._money(amount)}.",
            "Transactions",
            "high",
            "transactions",
            created_at,
            created_at_fmt,
        )

    @staticmethod
    def _audit_title(table_name, action):
        label = NotificationModel.TABLE_LABELS.get(table_name, "Record")
        verb = NotificationModel.ACTION_LABELS.get(action, "changed")
        if table_name == "transactions" and action == "UPDATE":
            return "Payment updated"
        return f"{label} {verb}"

    @staticmethod
    def _audit_message(row):
        table_name = str(row.get("table_name") or "").lower()
        action = str(row.get("action") or "").upper()
        actor = str(row.get("changed_by") or "Someone").strip() or "Someone"
        label = NotificationModel.TABLE_LABELS.get(table_name, "record").lower()
        verb = NotificationModel.ACTION_LABELS.get(action, "changed")
        record_id = row.get("record_id")
        ref = f" #{record_id}" if record_id is not None else ""

        if table_name == "transactions" and action == "UPDATE":
            return f"{actor} updated payment details for transaction{ref}."
        return f"{actor} {verb} {label}{ref}."

    @staticmethod
    def _fetch_recent_activity(cursor, limit=6):
        cursor.execute("""
            SELECT
                a.id,
                a.action,
                LOWER(a.table_name) AS table_name,
                a.record_id,
                a.changed_at AS created_at,
                DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p') AS created_at_fmt,
                TRIM(COALESCE(u.full_name, 'System')) AS changed_by
            FROM audit_logs a
            LEFT JOIN users u ON u.id = a.user_id
            WHERE LOWER(a.table_name) IN ('customers', 'deliveries', 'lpg_products', 'transactions', 'users')
            ORDER BY a.changed_at DESC, a.id DESC
            LIMIT %s
        """, (limit,))

        notifications = []
        for row in cursor.fetchall():
            table_name = str(row.get("table_name") or "").lower()
            action = str(row.get("action") or "").upper()
            notifications.append({
                "key": f"audit:{row.get('id')}",
                "title": NotificationModel._audit_title(table_name, action),
                "message": NotificationModel._audit_message(row),
                "category": NotificationModel.TABLE_LABELS.get(table_name, "Activity"),
                "severity": "normal",
                "action": NotificationModel.TABLE_ACTIONS.get(table_name, "audit_logs"),
                "created_at": row.get("created_at"),
                "created_at_fmt": row.get("created_at_fmt"),
                "source": "audit",
            })
        return notifications

    @staticmethod
    def _read_map(cursor, user_id, keys):
        if not keys:
            return {}

        placeholders = ", ".join(["%s"] * len(keys))
        cursor.execute(f"""
            SELECT
                notification_key,
                read_at,
                DATE_FORMAT(read_at, '%b %d, %Y %h:%i %p') AS read_at_fmt
            FROM notification_reads
            WHERE user_id = %s
              AND notification_key IN ({placeholders})
        """, tuple([user_id] + keys))
        return {row["notification_key"]: row for row in cursor.fetchall()}

    @staticmethod
    def get_for_user(user_id, role=None, limit=12):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            NotificationModel._ensure_table(cursor)
            conn.commit()

            created_at, created_at_fmt = NotificationModel._current_stamp(cursor)
            notifications = [
                NotificationModel._fetch_overdue_delivery_alert(cursor, created_at, created_at_fmt),
                NotificationModel._fetch_today_delivery_alert(cursor, created_at, created_at_fmt),
                NotificationModel._fetch_unpaid_transaction_alert(cursor, created_at, created_at_fmt),
            ]
            notifications = [item for item in notifications if item]
            notifications.extend(NotificationModel._fetch_recent_activity(cursor, limit=6))

            keys = [item["key"] for item in notifications]
            read_map = NotificationModel._read_map(cursor, user_id, keys)
            for item in notifications:
                read_row = read_map.get(item["key"])
                item["is_read"] = read_row is not None
                item["read_at"] = read_row.get("read_at") if read_row else None
                item["read_at_fmt"] = read_row.get("read_at_fmt") if read_row else None

            def _created_ts(item):
                value = item.get("created_at")
                if hasattr(value, "timestamp"):
                    return value.timestamp()
                return 0

            notifications.sort(
                key=lambda item: (
                    1 if item.get("is_read") else 0,
                    0 if item.get("severity") == "high" else 1,
                    -_created_ts(item),
                )
            )
            return notifications[:limit]
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def mark_read(user_id, notification_key):
        if not notification_key:
            return True

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            NotificationModel._ensure_table(cursor)
            cursor.execute("""
                INSERT INTO notification_reads (user_id, notification_key, read_at)
                VALUES (%s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    read_at = NOW(),
                    updated_at = NOW()
            """, (user_id, notification_key))
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
    def mark_many_read(user_id, notification_keys):
        keys = [key for key in notification_keys if key]
        if not keys:
            return True

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            NotificationModel._ensure_table(cursor)
            cursor.executemany("""
                INSERT INTO notification_reads (user_id, notification_key, read_at)
                VALUES (%s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    read_at = NOW(),
                    updated_at = NOW()
            """, [(user_id, key) for key in keys])
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
