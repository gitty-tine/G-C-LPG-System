import sys
import os
 
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
 
from database.connection import get_connection
 
 
class DeliveryLogsModel:
    _QUERY = """
        WITH base_logs AS (
            SELECT
                dl.id                                                           AS log_id,
 
                CAST(dl.delivery_id AS CHAR)                                    AS delivery_id,
 
                -- Correlated subquery: fetch customer name for this delivery
                (
                    SELECT TRIM(c2.full_name)
                    FROM   customers c2
                    WHERE  c2.id = d.customer_id
                    LIMIT  1
                )                                                               AS customer_name,
 
                -- String: replace underscores for display
                REPLACE(COALESCE(dl.old_status, ''), '_', ' ')                  AS old_status,
                REPLACE(COALESCE(dl.new_status, ''), '_', ' ')                  AS new_status,
 
                TRIM(u.full_name)                                               AS changed_by,
 
                -- Date: human-readable timestamp
                DATE_FORMAT(dl.changed_at, '%b %e, %Y %h:%i %p')               AS changed_at,
                DATE(dl.changed_at)                                             AS changed_on,
 
                -- Math + Date: days since this log entry was recorded
                ABS(DATEDIFF(NOW(), dl.changed_at))                             AS days_since_change,
 
                TRIM(c.address)                                                 AS address,
                DATE_FORMAT(d.schedule_date, '%b %e, %Y')                      AS scheduled_date,
                COALESCE(TRIM(d.notes), '')                                     AS notes,
                d.id                                                            AS delivery_db_id,
 
                -- Window function: rank log entries per delivery, latest first
                ROW_NUMBER() OVER (
                    PARTITION BY dl.delivery_id
                    ORDER BY     dl.changed_at DESC
                )                                                               AS rank_in_delivery
 
            FROM  delivery_logs dl
            INNER JOIN deliveries d  ON dl.delivery_id = d.id
            INNER JOIN customers  c  ON d.customer_id  = c.id
            INNER JOIN users      u  ON dl.user_id     = u.id
        ),
 
        product_lines AS (
            SELECT
                item_agg.delivery_id,
                item_agg.products_str,
 
                -- Scalar subquery: total quantity for this delivery
                (
                    SELECT SUM(di2.quantity)
                    FROM   delivery_items di2
                    WHERE  di2.delivery_id = item_agg.delivery_id
                )                                                               AS total_qty
 
            FROM (
                -- Derived table: one product summary string per delivery
                SELECT
                    di.delivery_id,
                    GROUP_CONCAT(
                        CONCAT(
                            CAST(di.quantity AS CHAR), ' x ',
                            TRIM(p.name),
                            ' (', di.type, ')'
                        )
                        ORDER BY p.name
                        SEPARATOR ', '
                    )                                                           AS products_str
                FROM  delivery_items di
                INNER JOIN lpg_products p ON di.product_id = p.id
                GROUP BY di.delivery_id
            ) AS item_agg
        )
 
        SELECT
            bl.delivery_id,
            bl.customer_name,
            bl.old_status,
            bl.new_status,
            bl.changed_by,
            bl.changed_at,
            bl.changed_on,
            bl.days_since_change,
            bl.address,
            bl.scheduled_date,
            bl.notes,
            bl.rank_in_delivery,
            COALESCE(pl.products_str, '-')              AS products,
            COALESCE(CAST(pl.total_qty AS CHAR), '0')   AS total_qty
 
        FROM  base_logs bl
        LEFT JOIN product_lines pl ON bl.delivery_db_id = pl.delivery_id
        ORDER BY bl.log_id DESC
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
