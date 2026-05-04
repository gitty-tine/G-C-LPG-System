from database.connection import get_connection


class NotificationModel:
    _table_ready = False

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

    ROLE_AUDIT_TABLES = {
        "admin": ("customers", "deliveries", "transactions"),
        "owner": ("deliveries", "lpg_products", "transactions"),
    }
    DEFAULT_AUDIT_TABLES = ("customers", "deliveries", "lpg_products", "transactions")

    @staticmethod
    def _ensure_table(cursor):
        if NotificationModel._table_ready:
            return
        cursor.execute(NotificationModel.TABLE_SQL)
        NotificationModel._table_ready = True

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
    def _evaluation_stamp(cursor):
        cursor.execute("SELECT NOW() AS current_at, DATE_FORMAT(NOW(), '%b %d, %Y %h:%i %p') AS current_at_fmt")
        row = cursor.fetchone() or {}
        return row.get("current_at"), row.get("current_at_fmt")

    @staticmethod
    def _summary_notification(
        key,
        title,
        message,
        category,
        severity,
        action,
        evaluated_at,
        evaluated_at_fmt,
        context_text=None,
        sort_at=None,
    ):
        time_text = f"Last evaluated {evaluated_at_fmt}" if evaluated_at_fmt else "Last evaluated"
        return {
            "key": key,
            "title": title,
            "message": message,
            "category": category,
            "severity": severity,
            "severity_label": "High" if severity == "high" else "Info",
            "action": action,
            "created_at": sort_at,
            "created_at_fmt": context_text or time_text,
            "evaluated_at": evaluated_at,
            "evaluated_at_fmt": evaluated_at_fmt,
            "time_label": "Last evaluated",
            "time_text": time_text,
            "source": "summary",
            "source_label": "Summary",
        }

    @staticmethod
    def _fetch_overdue_delivery_alert(cursor, evaluated_at, evaluated_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                MIN(schedule_date) AS oldest_date,
                DATE_FORMAT(MIN(schedule_date), '%b %d, %Y') AS oldest_date_fmt,
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
        oldest_text = row.get("oldest_date_fmt") or row.get("oldest_date") or "the earliest open date"
        return NotificationModel._summary_notification(
            f"summary:overdue-deliveries:{total}:{row.get('oldest_date')}",
            "Overdue deliveries",
            f"{total} {NotificationModel._plural(total, 'delivery', 'deliveries')} are overdue. Oldest was scheduled for {oldest_text} ({day_text}).",
            "Deliveries",
            "high",
            "deliveries",
            evaluated_at,
            evaluated_at_fmt,
            f"Oldest scheduled {oldest_text}",
            row.get("oldest_date"),
        )

    @staticmethod
    def _fetch_today_delivery_alert(cursor, evaluated_at, evaluated_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN LOWER(REPLACE(status, ' ', '_')) = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                SUM(CASE WHEN LOWER(REPLACE(status, ' ', '_')) IN ('in_transit', 'on_delivery') THEN 1 ELSE 0 END) AS transit_count,
                CURDATE() AS today,
                DATE_FORMAT(CURDATE(), '%b %d, %Y') AS today_fmt
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
            f"{total} deliveries are still open today: {pending} pending, {transit} in transit.",
            "Deliveries",
            "normal",
            "deliveries",
            evaluated_at,
            evaluated_at_fmt,
            f"For {row.get('today_fmt') or 'today'}",
            row.get("today"),
        )

    @staticmethod
    def _fetch_unpaid_transaction_alert(cursor, evaluated_at, evaluated_at_fmt):
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                ROUND(COALESCE(SUM(t.total_amount), 0), 2) AS total_amount,
                MIN(d.schedule_date) AS oldest_delivery_date,
                DATE_FORMAT(MIN(d.schedule_date), '%b %d, %Y') AS oldest_delivery_fmt
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
            f"{total} delivered {NotificationModel._plural(total, 'transaction')} are still unpaid. Outstanding balance: {NotificationModel._money(amount)}.",
            "Transactions",
            "high",
            "transactions",
            evaluated_at,
            evaluated_at_fmt,
            f"Oldest delivered {row.get('oldest_delivery_fmt') or '-'}",
            row.get("oldest_delivery_date"),
        )

    @staticmethod
    def _snapshot_map(value):
        text = str(value or "").strip()
        if not text or text in {"-", "None"}:
            return {}

        parsed = {}
        for part in text.split(", "):
            if ":" not in part:
                continue
            key, raw_value = part.split(":", 1)
            parsed[key.strip().lower()] = raw_value.strip()
        return parsed

    @staticmethod
    def _pretty_value(value):
        text = str(value or "").strip()
        if not text:
            return "-"
        cleaned = text.replace("_", " ")
        if cleaned.lower() in {"pending", "in transit", "on delivery", "delivered", "cancelled", "paid", "unpaid", "yes", "no"}:
            return cleaned.title()
        return cleaned

    @staticmethod
    def _record_ref(record_id):
        return f" #{record_id}" if record_id is not None else ""

    @staticmethod
    def _record_description(table_name, values, raw_value=None):
        if table_name == "deliveries":
            parts = []
            customer = values.get("customer")
            date = values.get("date") or values.get("schedule date")
            status = values.get("status")
            if customer:
                parts.append(customer)
            if date:
                parts.append(f"scheduled {date}")
            if status:
                parts.append(f"status {NotificationModel._pretty_value(status)}")
            return ", ".join(parts)

        if table_name == "transactions":
            parts = []
            customer = values.get("customer")
            amount = values.get("total amount")
            payment = values.get("payment status")
            if customer:
                parts.append(customer)
            if amount:
                parts.append(f"PHP {amount}" if not str(amount).upper().startswith("PHP") else amount)
            if payment:
                parts.append(f"payment {NotificationModel._pretty_value(payment)}")
            return ", ".join(parts)

        if table_name == "lpg_products":
            name = " ".join(
                part for part in (values.get("name"), values.get("size")) if part
            ).strip()
            if name:
                return name

        if table_name == "customers":
            if values.get("name"):
                return values.get("name")

        text = str(raw_value or "").strip()
        if text and text != "-":
            return text[:90] + ("..." if len(text) > 90 else "")
        return ""

    @staticmethod
    def _active_change(old_map, new_map):
        old_active = NotificationModel._pretty_value(old_map.get("active")).lower()
        new_active = NotificationModel._pretty_value(new_map.get("active")).lower()
        if old_active == "yes" and new_active == "no":
            return "archived"
        if old_active == "no" and new_active == "yes":
            return "restored"
        return None

    @staticmethod
    def _changed_fields(old_map, new_map):
        changes = []
        for key, new_value in new_map.items():
            old_value = old_map.get(key)
            if old_value == new_value:
                continue
            label = key.replace("_", " ").title()
            changes.append(
                f"{label} changed from {NotificationModel._pretty_value(old_value)} to {NotificationModel._pretty_value(new_value)}"
            )
        return changes

    @staticmethod
    def _audit_title(row):
        table_name = str(row.get("table_name") or "").lower()
        action = str(row.get("action") or "").upper()
        label = NotificationModel.TABLE_LABELS.get(table_name, "Record")
        verb = NotificationModel.ACTION_LABELS.get(action, "changed")
        old_map = NotificationModel._snapshot_map(row.get("old_value"))
        new_map = NotificationModel._snapshot_map(row.get("new_value"))
        active_change = NotificationModel._active_change(old_map, new_map)
        if active_change:
            return f"{label} {active_change}"
        if table_name == "deliveries" and action == "UPDATE" and old_map.get("status") != new_map.get("status"):
            return "Delivery status changed"
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
        ref = NotificationModel._record_ref(record_id)
        old_map = NotificationModel._snapshot_map(row.get("old_value"))
        new_map = NotificationModel._snapshot_map(row.get("new_value"))

        if action == "INSERT":
            desc = NotificationModel._record_description(table_name, new_map, row.get("new_value"))
            detail = f": {desc}" if desc else ""
            return f"{actor} added {label}{ref}{detail}."

        if action == "DELETE":
            desc = NotificationModel._record_description(table_name, old_map, row.get("old_value"))
            detail = f": {desc}" if desc else ""
            return f"{actor} deleted {label}{ref}{detail}."

        active_change = NotificationModel._active_change(old_map, new_map)
        if active_change:
            desc = NotificationModel._record_description(table_name, new_map or old_map, row.get("new_value") or row.get("old_value"))
            detail = f": {desc}" if desc else ""
            return f"{actor} {active_change} {label}{ref}{detail}."

        if table_name == "transactions" and action == "UPDATE":
            old_status = NotificationModel._pretty_value(old_map.get("payment status"))
            new_status = NotificationModel._pretty_value(new_map.get("payment status"))
            if new_status != "-":
                if new_status.lower() == "paid":
                    return f"{actor} marked transaction{ref} as paid (was {old_status})."
                return f"{actor} changed transaction{ref} payment from {old_status} to {new_status}."

        if table_name == "deliveries" and action == "UPDATE":
            old_status = old_map.get("status")
            new_status = new_map.get("status")
            customer = new_map.get("customer") or old_map.get("customer")
            customer_text = f" for {customer}" if customer else ""
            if old_status != new_status and new_status:
                return (
                    f"{actor} changed delivery{ref}{customer_text} from "
                    f"{NotificationModel._pretty_value(old_status)} to {NotificationModel._pretty_value(new_status)}."
                )

        changes = NotificationModel._changed_fields(old_map, new_map)
        if changes:
            shown = "; ".join(changes[:2])
            if len(changes) > 2:
                shown += f"; {len(changes) - 2} more changes"
            return f"{actor} {verb} {label}{ref}: {shown}."

        return f"{actor} {verb} {label}{ref}."

    @staticmethod
    def _fetch_recent_activity(cursor, role=None, limit=6):
        role_key = str(role or "").strip().lower()
        allowed_tables = NotificationModel.ROLE_AUDIT_TABLES.get(
            role_key,
            NotificationModel.DEFAULT_AUDIT_TABLES,
        )
        placeholders = ", ".join(["%s"] * len(allowed_tables))
        cursor.execute(f"""
            SELECT
                a.id,
                a.action,
                LOWER(a.table_name) AS table_name,
                a.record_id,
                a.old_value,
                a.new_value,
                a.changed_at AS created_at,
                DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p') AS created_at_fmt,
                TRIM(COALESCE(u.full_name, 'System')) AS changed_by
            FROM audit_logs a
            LEFT JOIN users u ON u.id = a.user_id
            WHERE LOWER(a.table_name) IN ({placeholders})
            ORDER BY a.changed_at DESC, a.id DESC
            LIMIT %s
        """, tuple(list(allowed_tables) + [limit]))

        notifications = []
        for row in cursor.fetchall():
            table_name = str(row.get("table_name") or "").lower()
            notifications.append({
                "key": f"audit:{row.get('id')}",
                "title": NotificationModel._audit_title(row),
                "message": NotificationModel._audit_message(row),
                "category": NotificationModel.TABLE_LABELS.get(table_name, "Activity"),
                "severity": "normal",
                "severity_label": "Info",
                "action": NotificationModel.TABLE_ACTIONS.get(table_name, "audit_logs"),
                "created_at": row.get("created_at"),
                "created_at_fmt": row.get("created_at_fmt"),
                "time_label": "Recorded",
                "time_text": row.get("created_at_fmt") or "",
                "source": "audit",
                "source_label": "Audit",
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

            evaluated_at, evaluated_at_fmt = NotificationModel._evaluation_stamp(cursor)
            notifications = [
                NotificationModel._fetch_overdue_delivery_alert(cursor, evaluated_at, evaluated_at_fmt),
                NotificationModel._fetch_today_delivery_alert(cursor, evaluated_at, evaluated_at_fmt),
                NotificationModel._fetch_unpaid_transaction_alert(cursor, evaluated_at, evaluated_at_fmt),
            ]
            notifications = [item for item in notifications if item]
            notifications.extend(NotificationModel._fetch_recent_activity(cursor, role=role, limit=6))

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
                if hasattr(value, "toordinal"):
                    return value.toordinal() * 86400
                return 0

            notifications.sort(
                key=lambda item: (
                    1 if item.get("is_read") else 0,
                    0 if item.get("severity") == "high" else 1,
                    0 if item.get("source") == "summary" else 1,
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
