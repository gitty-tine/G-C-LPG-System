from database.connection import get_connection


class AuditLogModel:
    @staticmethod
    def get_all(date_from=None, date_to=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    a.id,
                    a.user_id,
                    a.action                                          AS raw_action,
                    a.table_name                                      AS raw_table,
                    a.record_id,
                    COALESCE(a.old_value, '-')                        AS old_value,
                    COALESCE(a.new_value, '-')                        AS new_value,
                    DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p')   AS changed_at,
                    a.changed_at                                      AS changed_at_raw,
                    TRIM(u.full_name)                                 AS changed_by,
                    u.role                                            AS changed_by_role,
                    CASE a.action
                        WHEN 'INSERT' THEN 'Added'
                        WHEN 'UPDATE' THEN 'Updated'
                        WHEN 'DELETE' THEN 'Deleted'
                        ELSE a.action
                    END                                               AS activity_type,
                    CASE a.table_name
                        WHEN 'customers'    THEN 'Customers'
                        WHEN 'lpg_products' THEN 'LPG Products'
                        WHEN 'deliveries'   THEN 'Deliveries'
                        WHEN 'transactions' THEN 'Transactions'
                        WHEN 'users'        THEN 'Users'
                        ELSE a.table_name
                    END                                               AS section_name,
                    CASE a.action
                        WHEN 'INSERT' THEN CONCAT(
                            CASE a.table_name
                                WHEN 'customers'    THEN 'Customer'
                                WHEN 'lpg_products' THEN 'LPG product'
                                WHEN 'deliveries'   THEN 'Delivery'
                                WHEN 'transactions' THEN 'Transaction'
                                WHEN 'users'        THEN 'User'
                                ELSE 'Record'
                            END,
                            ' was added'
                        )
                        WHEN 'UPDATE' THEN CONCAT(
                            CASE a.table_name
                                WHEN 'customers'    THEN 'Customer record'
                                WHEN 'lpg_products' THEN 'Product record'
                                WHEN 'deliveries'   THEN 'Delivery record'
                                WHEN 'transactions' THEN 'Transaction record'
                                WHEN 'users'        THEN 'User record'
                                ELSE 'Record'
                            END,
                            ' was updated'
                        )
                        WHEN 'DELETE' THEN CONCAT(
                            CASE a.table_name
                                WHEN 'customers'    THEN 'Customer'
                                WHEN 'lpg_products' THEN 'LPG product'
                                WHEN 'deliveries'   THEN 'Delivery'
                                WHEN 'transactions' THEN 'Transaction'
                                WHEN 'users'        THEN 'User'
                                ELSE 'Record'
                            END,
                            ' was deleted'
                        )
                        ELSE 'Record changed'
                    END                                               AS description
                FROM audit_logs a
                INNER JOIN users u ON u.id = a.user_id
            """

            params = []
            if date_from and date_to:
                query += " WHERE DATE(a.changed_at) BETWEEN %s AND %s"
                params.extend([date_from, date_to])

            query += " ORDER BY a.changed_at DESC"
            cursor.execute(query, tuple(params) if params else None)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_action(action_label, date_from=None, date_to=None):
        action_map = {
            "Added": "INSERT",
            "Updated": "UPDATE",
            "Deleted": "DELETE",
        }
        raw_action = action_map.get(action_label, action_label)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    a.id,
                    a.action                                          AS raw_action,
                    a.table_name                                      AS raw_table,
                    a.record_id,
                    COALESCE(a.old_value, '-')                        AS old_value,
                    COALESCE(a.new_value, '-')                        AS new_value,
                    DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p')   AS changed_at,
                    a.changed_at                                      AS changed_at_raw,
                    TRIM(u.full_name)                                 AS changed_by,
                    u.role                                            AS changed_by_role,
                    CASE a.action
                        WHEN 'INSERT' THEN 'Added'
                        WHEN 'UPDATE' THEN 'Updated'
                        WHEN 'DELETE' THEN 'Deleted'
                        ELSE a.action
                    END                                               AS activity_type,
                    CASE a.table_name
                        WHEN 'customers'    THEN 'Customers'
                        WHEN 'lpg_products' THEN 'LPG Products'
                        WHEN 'deliveries'   THEN 'Deliveries'
                        WHEN 'transactions' THEN 'Transactions'
                        WHEN 'users'        THEN 'Users'
                        ELSE a.table_name
                    END                                               AS section_name
                FROM audit_logs a
                INNER JOIN users u ON u.id = a.user_id
                WHERE a.action = %s
            """

            params = [raw_action]
            if date_from and date_to:
                query += " AND DATE(a.changed_at) BETWEEN %s AND %s"
                params.extend([date_from, date_to])

            query += " ORDER BY a.changed_at DESC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_section(section_label, date_from=None, date_to=None):
        section_map = {
            "Customers": "customers",
            "LPG Products": "lpg_products",
            "Deliveries": "deliveries",
            "Transactions": "transactions",
            "Users": "users",
        }
        raw_table = section_map.get(section_label, section_label.lower())

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    a.id,
                    a.action                                          AS raw_action,
                    a.table_name                                      AS raw_table,
                    a.record_id,
                    COALESCE(a.old_value, '-')                        AS old_value,
                    COALESCE(a.new_value, '-')                        AS new_value,
                    DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p')   AS changed_at,
                    a.changed_at                                      AS changed_at_raw,
                    TRIM(u.full_name)                                 AS changed_by,
                    u.role                                            AS changed_by_role,
                    CASE a.action
                        WHEN 'INSERT' THEN 'Added'
                        WHEN 'UPDATE' THEN 'Updated'
                        WHEN 'DELETE' THEN 'Deleted'
                        ELSE a.action
                    END                                               AS activity_type,
                    CASE a.table_name
                        WHEN 'customers'    THEN 'Customers'
                        WHEN 'lpg_products' THEN 'LPG Products'
                        WHEN 'deliveries'   THEN 'Deliveries'
                        WHEN 'transactions' THEN 'Transactions'
                        WHEN 'users'        THEN 'Users'
                        ELSE a.table_name
                    END                                               AS section_name
                FROM audit_logs a
                INNER JOIN users u ON u.id = a.user_id
                WHERE a.table_name = %s
            """

            params = [raw_table]
            if date_from and date_to:
                query += " AND DATE(a.changed_at) BETWEEN %s AND %s"
                params.extend([date_from, date_to])

            query += " ORDER BY a.changed_at DESC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_distinct_sections():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT DISTINCT
                    CASE table_name
                        WHEN 'customers'    THEN 'Customers'
                        WHEN 'lpg_products' THEN 'LPG Products'
                        WHEN 'deliveries'   THEN 'Deliveries'
                        WHEN 'transactions' THEN 'Transactions'
                        WHEN 'users'        THEN 'Users'
                        ELSE table_name
                    END AS section_name
                FROM audit_logs
                ORDER BY section_name ASC
                """
            )
            return [row["section_name"] for row in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_activity_counts():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    CASE action
                        WHEN 'INSERT' THEN 'Added'
                        WHEN 'UPDATE' THEN 'Updated'
                        WHEN 'DELETE' THEN 'Deleted'
                        ELSE action
                    END AS activity_type,
                    COUNT(*) AS total
                FROM audit_logs
                GROUP BY action
                ORDER BY total DESC
                """
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


AuditLogsModel = AuditLogModel
