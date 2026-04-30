import re

from database.connection import get_connection


_AUDIT_FIELD_PATTERN = re.compile(r"(?:(?<=^)|(?<=, ))([A-Za-z][A-Za-z ]{0,40}):\s*")


def _audit_field_names(*values):
    names = []
    for value in values:
        if not value:
            continue
        for match in _AUDIT_FIELD_PATTERN.finditer(str(value)):
            name = match.group(1).strip()
            if name and name not in names:
                names.append(name)
    return names


def _human_join(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


class AuditLogModel:
    ACTION_LABEL_TO_RAW = {
        "Added": "INSERT",
        "Updated": "UPDATE",
        "Deleted": "DELETE",
    }

    SECTION_LABEL_TO_RAW = {
        "Customers": "customers",
        "LPG Products": "lpg_products",
        "Deliveries": "deliveries",
        "Transactions": "transactions",
        "Users": "users",
    }

    @staticmethod
    def get_logs(action=None, section=None, date_from=None, date_to=None):
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

            clauses = []
            params = []

            raw_action = AuditLogModel.ACTION_LABEL_TO_RAW.get(action, action)
            if raw_action and str(raw_action).lower() != "all activities":
                clauses.append("a.action = %s")
                params.append(raw_action)

            raw_section = AuditLogModel.SECTION_LABEL_TO_RAW.get(section, section)
            if raw_section and str(raw_section).lower() != "all sections":
                clauses.append("a.table_name = %s")
                params.append(str(raw_section).lower())

            if date_from and date_to:
                clauses.append("a.changed_at >= %s AND a.changed_at < DATE_ADD(%s, INTERVAL 1 DAY)")
                params.extend([date_from, date_to])

            if clauses:
                query += " WHERE " + " AND ".join(clauses)

            query += " ORDER BY a.changed_at DESC, a.id DESC"
            cursor.execute(query, tuple(params) if params else None)
            rows = cursor.fetchall()
            AuditLogModel._apply_change_summaries(rows)
            return rows
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all(date_from=None, date_to=None):
        return AuditLogModel.get_logs(date_from=date_from, date_to=date_to)

    @staticmethod
    def _apply_change_summaries(rows):
        for row in rows:
            if row.get("raw_action") != "UPDATE":
                continue

            fields = _audit_field_names(row.get("old_value"), row.get("new_value"))
            if not fields:
                continue

            row["changed_fields"] = fields
            row["description"] = f"{_human_join(fields)} changed"


AuditLogsModel = AuditLogModel
