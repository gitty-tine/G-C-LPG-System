import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.connection import get_connection


class DeliveryLogsModel:
    _QUERY = """
        SELECT
            CAST(dl.delivery_id AS CHAR)                                    AS delivery_id,
            TRIM(c.full_name)                                               AS customer_name,
            REPLACE(COALESCE(dl.old_status, ''), '_', ' ')                  AS old_status,
            REPLACE(COALESCE(dl.new_status, ''), '_', ' ')                  AS new_status,
            TRIM(u.full_name)                                               AS changed_by,
            DATE_FORMAT(dl.changed_at, '%b %e, %Y %h:%i %p')                AS changed_at,
            DATE(dl.changed_at)                                             AS changed_on,
            TRIM(c.address)                                                 AS address,
            DATE_FORMAT(d.schedule_date, '%b %e, %Y')                       AS scheduled_date,
            COALESCE(TRIM(d.notes), '')                                     AS notes,
            COALESCE(pl.products, '-')                                      AS products
        FROM delivery_logs dl
        INNER JOIN deliveries d ON dl.delivery_id = d.id
        INNER JOIN customers c ON d.customer_id = c.id
        INNER JOIN users u ON dl.user_id = u.id
        LEFT JOIN (
            SELECT
                di.delivery_id,
                GROUP_CONCAT(
                    CONCAT(
                        CAST(di.quantity AS CHAR), ' x ',
                        TRIM(p.name),
                        ' (', REPLACE(di.type, '_', ' '), ')'
                    )
                    ORDER BY p.name
                    SEPARATOR ', '
                )                                                           AS products
            FROM delivery_items di
            INNER JOIN lpg_products p ON di.product_id = p.id
            GROUP BY di.delivery_id
        ) pl ON pl.delivery_id = d.id
        ORDER BY dl.changed_at DESC, dl.id DESC
    """

    def get_all_logs(self):
        """
        Returns a list of dicts ready for DeliveryLogsView.load_logs().
        """
        conn = get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(self._QUERY)
            rows = cursor.fetchall()
            return [self._to_view_dict(row) for row in rows]
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def _to_view_dict(self, row):
        """Maps a raw DB row to the dict shape DeliveryLogsView expects."""
        return {
            "delivery_id":    row.get("delivery_id", ""),
            "customer_name":  self._title(row.get("customer_name", "")),
            "old_status":     self._title(row.get("old_status", "")),
            "new_status":     self._title(row.get("new_status", "")),
            "changed_by":     row.get("changed_by", ""),
            "changed_at":     row.get("changed_at", ""),
            "changed_on":     row.get("changed_on"),
            "address":        row.get("address", ""),
            "scheduled_date": row.get("scheduled_date", ""),
            "products":       row.get("products", "-"),
            "notes":          row.get("notes", ""),
        }

    @staticmethod
    def _title(text):
        """'in transit' -> 'In Transit'"""
        if not text:
            return ""
        return " ".join(word.capitalize() for word in text.strip().split())
