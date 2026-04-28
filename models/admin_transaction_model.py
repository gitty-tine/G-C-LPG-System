from database.connection import get_connection


class TransactionModel:
    @staticmethod
    def get_all(date_from=None, date_to=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            base_query = """
                SELECT
                    vt.transaction_id,
                    t.delivery_id,
                    vt.customer_name,
                    vt.customer_contact                                     AS customer_contact,
                    vt.schedule_date                                        AS delivery_date,
                    DATE_FORMAT(vt.schedule_date, '%b %d, %Y')             AS delivery_date_fmt,
                    vt.total_amount,
                    FORMAT(vt.total_amount, 2)                              AS total_amount_fmt,
                    vt.payment_status,
                    vt.paid_at,
                    DATE_FORMAT(vt.paid_at, '%b %d, %Y')                   AS paid_at_fmt,
                    DATE_FORMAT(vt.created_at, '%b %d, %Y %h:%i %p')       AS created_at_fmt,
                    vt.delivery_status,
                    COALESCE(
                        GROUP_CONCAT(
                            CONCAT(
                                TRIM(p.name),
                                CASE
                                    WHEN COALESCE(TRIM(p.cylinder_size), '') = '' THEN ''
                                    ELSE CONCAT(' ', TRIM(p.cylinder_size))
                                END,
                                ' ',
                                REPLACE(di.type, '_', ' '),
                                ' x ',
                                di.quantity
                            )
                            ORDER BY p.name ASC
                            SEPARATOR ', '
                        ),
                        '-'
                    )                                                       AS product_summary
                FROM vw_transaction_summary vt
                LEFT JOIN transactions t  ON t.id = vt.transaction_id
                LEFT  JOIN delivery_items di ON di.delivery_id = t.delivery_id
                LEFT  JOIN lpg_products p    ON p.id           = di.product_id
            """

            if date_from and date_to:
                base_query += """
                WHERE vt.schedule_date BETWEEN %s AND %s
                """
                base_query += """
                GROUP BY
                    vt.transaction_id, t.delivery_id, vt.customer_name, vt.customer_contact,
                    vt.schedule_date, vt.total_amount, vt.payment_status,
                    vt.paid_at, vt.created_at, vt.delivery_status
                ORDER BY vt.schedule_date DESC, vt.created_at DESC
                """
                cursor.execute(base_query, (date_from, date_to))
            else:
                base_query += """
                GROUP BY
                    vt.transaction_id, t.delivery_id, vt.customer_name, vt.customer_contact,
                    vt.schedule_date, vt.total_amount, vt.payment_status,
                    vt.paid_at, vt.created_at, vt.delivery_status
                ORDER BY vt.schedule_date DESC, vt.created_at DESC
                """
                cursor.execute(base_query)

            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_delivery_id(delivery_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    vt.transaction_id,
                    t.delivery_id,
                    vt.customer_name,
                    vt.customer_contact,
                    vt.schedule_date                                        AS delivery_date,
                    DATE_FORMAT(vt.schedule_date, '%b %d, %Y')             AS delivery_date_fmt,
                    vt.total_amount,
                    FORMAT(vt.total_amount, 2)                              AS total_amount_fmt,
                    vt.payment_status,
                    vt.paid_at,
                    DATE_FORMAT(vt.paid_at, '%b %d, %Y')                   AS paid_at_fmt,
                    DATE_FORMAT(vt.created_at, '%b %d, %Y %h:%i %p')       AS created_at_fmt,
                    vt.delivery_status,
                    (
                        SELECT COUNT(*)
                        FROM delivery_items di
                        WHERE di.delivery_id = t.delivery_id
                    )                                                       AS item_count,
                    (
                        SELECT COALESCE(SUM(di2.quantity * di2.price_at_delivery), 0)
                        FROM delivery_items di2
                        WHERE di2.delivery_id = t.delivery_id
                    )                                                       AS computed_total
                FROM vw_transaction_summary vt
                INNER JOIN transactions t ON t.id = vt.transaction_id
                WHERE t.delivery_id = %s
                """,
                (delivery_id,),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_totals(date_from=None, date_to=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if date_from and date_to:
                cursor.execute(
                    """
                    SELECT
                        ROUND(COALESCE(SUM(
                            CASE WHEN t.payment_status = 'paid'
                                 THEN t.total_amount ELSE 0 END
                        ), 0), 2)                                           AS total_paid,
                        ROUND(COALESCE(SUM(
                            CASE WHEN t.payment_status = 'unpaid'
                                 THEN t.total_amount ELSE 0 END
                        ), 0), 2)                                           AS total_unpaid,
                        COUNT(*)                                            AS total_transactions,
                        SUM(CASE WHEN t.payment_status = 'paid'
                                 THEN 1 ELSE 0 END)                        AS paid_count,
                        SUM(CASE WHEN t.payment_status = 'unpaid'
                                 THEN 1 ELSE 0 END)                        AS unpaid_count
                    FROM transactions t
                    INNER JOIN deliveries d ON d.id = t.delivery_id
                    WHERE d.schedule_date BETWEEN %s AND %s
                    """,
                    (date_from, date_to),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        ROUND(COALESCE(SUM(
                            CASE WHEN payment_status = 'paid'
                                 THEN total_amount ELSE 0 END
                        ), 0), 2)                                           AS total_paid,
                        ROUND(COALESCE(SUM(
                            CASE WHEN payment_status = 'unpaid'
                                 THEN total_amount ELSE 0 END
                        ), 0), 2)                                           AS total_unpaid,
                        COUNT(*)                                            AS total_transactions,
                        SUM(CASE WHEN payment_status = 'paid'
                                 THEN 1 ELSE 0 END)                        AS paid_count,
                        SUM(CASE WHEN payment_status = 'unpaid'
                                 THEN 1 ELSE 0 END)                        AS unpaid_count
                    FROM transactions
                    """
                )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_running_totals(date_from, date_to):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    vt.transaction_id,
                    vt.customer_name,
                    vt.schedule_date                                        AS delivery_date,
                    DATE_FORMAT(vt.schedule_date, '%b %d, %Y')             AS delivery_date_fmt,
                    vt.total_amount,
                    vt.payment_status,
                    ROUND(
                        SUM(vt.total_amount) OVER (
                            ORDER BY vt.schedule_date ASC, vt.transaction_id ASC
                        ), 2
                    )                                                       AS running_total,
                    ROUND(
                        SUM(
                            CASE WHEN vt.payment_status = 'paid'
                                 THEN vt.total_amount ELSE 0 END
                        ) OVER (
                            ORDER BY vt.schedule_date ASC, vt.transaction_id ASC
                        ), 2
                    )                                                       AS running_paid_total
                FROM vw_transaction_summary vt
                WHERE vt.schedule_date BETWEEN %s AND %s
                ORDER BY vt.schedule_date ASC, vt.transaction_id ASC
                """,
                (date_from, date_to),
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    @staticmethod
    def get_overdue_unpaid(days_threshold=3):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    vt.transaction_id,
                    t.delivery_id,
                    vt.customer_name,
                    vt.customer_contact,
                    vt.schedule_date                                        AS delivery_date,
                    DATE_FORMAT(vt.schedule_date, '%b %d, %Y')             AS delivery_date_fmt,
                    vt.total_amount,
                    FORMAT(vt.total_amount, 2)                              AS total_amount_fmt,
                    DATEDIFF(CURDATE(), vt.schedule_date)                  AS days_since_delivery
                FROM vw_transaction_summary vt
                INNER JOIN transactions t ON t.id = vt.transaction_id
                WHERE vt.payment_status = 'unpaid'
                  AND vt.delivery_status = 'delivered'
                  AND DATEDIFF(CURDATE(), vt.schedule_date) > %s
                ORDER BY days_since_delivery DESC
                """,
                (days_threshold,),
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    @staticmethod
    def get_daily_summary(date_from, date_to):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                WITH daily_base AS (
                    SELECT
                        DATE(d.schedule_date)                               AS sale_date,
                        t.total_amount,
                        t.payment_status
                    FROM transactions t
                    INNER JOIN deliveries d ON d.id = t.delivery_id
                    WHERE d.schedule_date BETWEEN %s AND %s
                )
                SELECT
                    sale_date,
                    DATE_FORMAT(sale_date, '%b %d, %Y')                    AS sale_date_fmt,
                    COUNT(*)                                                AS transaction_count,
                    ROUND(COALESCE(SUM(total_amount), 0), 2)               AS total_sales,
                    ROUND(COALESCE(SUM(
                        CASE WHEN payment_status = 'paid'
                             THEN total_amount ELSE 0 END
                    ), 0), 2)                                               AS paid_sales,
                    ROUND(COALESCE(SUM(
                        CASE WHEN payment_status = 'unpaid'
                             THEN total_amount ELSE 0 END
                    ), 0), 2)                                               AS unpaid_sales,
                    ROUND(COALESCE(AVG(total_amount), 0), 2)               AS avg_transaction,
                    ROUND(
                        COALESCE(SUM(
                            CASE WHEN payment_status = 'paid'
                                 THEN total_amount ELSE 0 END
                        ), 0)
                        / NULLIF(COALESCE(SUM(total_amount), 0), 0) * 100,
                    2)                                                      AS collection_rate
                FROM daily_base
                GROUP BY sale_date
                ORDER BY sale_date ASC
                """,
                (date_from, date_to),
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    @staticmethod
    def mark_paid(delivery_id, user_id=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_mark_payment", [delivery_id])
            conn.commit()
            return True
        except Exception:
            if conn: conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    
    @staticmethod
    def is_paid(delivery_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    (
                        SELECT LOWER(payment_status)
                        FROM transactions
                        WHERE delivery_id = %s
                        LIMIT 1
                    ) AS payment_status
                """,
                (delivery_id,),
            )
            row = cursor.fetchone()
            if row and row["payment_status"]:
                return row["payment_status"] == "paid"
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
