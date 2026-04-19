from database.connection import get_connection


class AuditActorModel:
    @staticmethod
    def sync_actor(table_name, record_id, action, user_id, old_value=None, new_value=None, lookback_minutes=10):
        if not table_name or record_id is None or not action or not user_id:
            return False

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE audit_logs
                SET
                    user_id = %s,
                    old_value = CASE
                        WHEN %s IS NOT NULL THEN %s
                        ELSE old_value
                    END,
                    new_value = CASE
                        WHEN %s IS NOT NULL THEN %s
                        ELSE new_value
                    END
                WHERE id = (
                    SELECT id
                    FROM (
                        SELECT id
                        FROM audit_logs
                        WHERE table_name = %s
                          AND record_id = %s
                          AND action = %s
                          AND changed_at >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
                        ORDER BY changed_at DESC, id DESC
                        LIMIT 1
                    ) latest_log
                )
                """,
                (
                    user_id,
                    old_value, old_value,
                    new_value, new_value,
                    table_name, record_id, action, lookback_minutes,
                ),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        action,
                        table_name,
                        record_id,
                        old_value if old_value is not None else "-",
                        new_value if new_value is not None else "-",
                    ),
                )

            conn.commit()
            return True
        except Exception:
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
