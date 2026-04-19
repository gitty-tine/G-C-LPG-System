from database.connection import get_connection


class AdminDashboardModel:
    @staticmethod
    def get_kpi_counts():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    total_today,
                    pending_today,
                    in_transit_today,
                    delivered_today,
                    cancelled_today,
                    COALESCE(sales_today, 0) AS sales_today
                FROM vw_dashboard_today
            """)
            row = cursor.fetchone()

            cursor.execute("""
                SELECT COUNT(*) AS unpaid_count
                FROM transactions t
                INNER JOIN deliveries d ON d.id = t.delivery_id
                WHERE t.payment_status = 'unpaid'
                  AND d.status = 'delivered'
            """)
            unpaid_row = cursor.fetchone()

            if row:
                row["unpaid_count"] = unpaid_row["unpaid_count"] if unpaid_row else 0
            return row
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()


    @staticmethod
    def get_todays_deliveries():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    vd.delivery_id                                          AS id,
                    vd.customer_id,
                    TRIM(vd.customer_name)                                  AS customer_name,
                    vd.customer_contact                                     AS contact,
                    TRIM(vd.customer_address)                               AS address,
                    vd.schedule_date,
                    vd.status,
                    COALESCE(vd.notes, '')                                  AS notes,
                    COALESCE(t.total_amount, 0)                             AS total_amount,
                    COALESCE(t.payment_status, 'unpaid')                   AS payment_status,
                    COALESCE(
                        GROUP_CONCAT(
                            CONCAT(
                                TRIM(p.name), ' ',
                                COALESCE(p.cylinder_size, ''),
                                ' x', di.quantity,
                                ' (', di.type, ')'
                            )
                            ORDER BY p.name ASC
                            SEPARATOR ', '
                        ), '—'
                    )                                                       AS product_summary
                FROM vw_delivery_details vd
                LEFT JOIN delivery_items di ON di.delivery_id = vd.delivery_id
                LEFT JOIN lpg_products   p  ON p.id           = di.product_id
                LEFT JOIN transactions   t  ON t.delivery_id  = vd.delivery_id
                WHERE DATE(vd.schedule_date) = CURDATE()
                GROUP BY
                    vd.delivery_id, vd.customer_id, vd.customer_name,
                    vd.customer_contact, vd.customer_address,
                    vd.schedule_date, vd.status, vd.notes,
                    t.total_amount, t.payment_status
                ORDER BY vd.created_at DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_unpaid_deliveries():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    t.delivery_id,
                    TRIM(vt.customer_name)                                  AS customer_name,
                    vt.customer_contact,
                    t.total_amount,
                    FORMAT(t.total_amount, 2)                               AS total_amount_fmt,
                    COALESCE(
                        GROUP_CONCAT(
                            CONCAT(
                                TRIM(p.name), ' ',
                                COALESCE(p.cylinder_size, ''),
                                ' x', di.quantity
                            )
                            ORDER BY p.name ASC
                            SEPARATOR ', '
                        ), '—'
                    )                                                       AS product_summary
                FROM vw_transaction_summary vt
                INNER JOIN transactions  t  ON t.id           = vt.transaction_id
                LEFT  JOIN delivery_items di ON di.delivery_id = t.delivery_id
                LEFT  JOIN lpg_products   p  ON p.id           = di.product_id
                WHERE t.payment_status = 'unpaid'
                  AND t.delivery_id IN (
                      SELECT id FROM deliveries
                      WHERE status = 'delivered'
                  )
                GROUP BY
                    t.delivery_id, vt.customer_name,
                    vt.customer_contact, t.total_amount
                ORDER BY t.total_amount DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()


    @staticmethod
    def get_all_dashboard_data():
        return {
            "kpi_counts":        AdminDashboardModel.get_kpi_counts(),
            "todays_deliveries": AdminDashboardModel.get_todays_deliveries(),
            "unpaid_deliveries": AdminDashboardModel.get_unpaid_deliveries(),
        }
