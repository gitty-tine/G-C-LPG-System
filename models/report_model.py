from datetime import datetime

from database.connection import get_connection


class ReportModel:
    @staticmethod
    def _month_start(day_value):
        if isinstance(day_value, datetime):
            day_value = day_value.date()
        elif not hasattr(day_value, "year"):
            day_value = datetime.strptime(str(day_value), "%Y-%m-%d").date()
        return day_value.replace(day=1)

    @staticmethod
    def get_daily_snapshot_summary(date_from, date_to):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales
                FROM daily_reports
                WHERE report_date BETWEEN %s AND %s
                """,
                (date_from, date_to),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_weekly_snapshot_summary(date_from, date_to):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales
                FROM weekly_reports
                WHERE week_start >= %s
                  AND week_end <= %s
                """,
                (date_from, date_to),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_monthly_snapshot_summary(date_from, date_to):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales
                FROM monthly_reports
                WHERE report_month BETWEEN %s AND %s
                """,
                (ReportModel._month_start(date_from), ReportModel._month_start(date_to)),
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    
    @staticmethod
    def get_summary(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(d.id)                                             AS total_deliveries,
                    SUM(CASE WHEN d.status = 'delivered'
                             THEN 1 ELSE 0 END)                            AS total_delivered,
                    SUM(CASE WHEN d.status = 'cancelled'
                             THEN 1 ELSE 0 END)                            AS total_cancelled,
                    SUM(CASE WHEN d.status = 'pending'
                             THEN 1 ELSE 0 END)                            AS total_pending,
                    SUM(CASE WHEN d.status = 'in_transit'
                             THEN 1 ELSE 0 END)                            AS total_in_transit,
                    COALESCE(SUM(t.total_amount), 0)                        AS total_sales,
                    COALESCE(SUM(
                        CASE WHEN t.payment_status = 'paid'
                             THEN t.total_amount ELSE 0 END
                    ), 0)                                                   AS total_paid,
                    COALESCE(SUM(
                        CASE WHEN t.payment_status = 'unpaid'
                             THEN t.total_amount ELSE 0 END
                    ), 0)                                                   AS total_unpaid,
                    COALESCE(AVG(t.total_amount), 0)                        AS avg_transaction_value,
                    DATE_FORMAT(%s, '%%b %%d, %%Y')                        AS date_from_fmt,
                    DATE_FORMAT(%s, '%%b %%d, %%Y')                        AS date_to_fmt
                FROM deliveries d
                LEFT JOIN transactions t ON t.delivery_id = d.id
                WHERE d.schedule_date BETWEEN %s AND %s
            """, (date_from, date_to, date_from, date_to))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_breakdown(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("sp_get_delivery_report", [date_from, date_to])

            rows = []
            for result in cursor.stored_results():
                rows = result.fetchall()
            return rows
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_detailed_breakdown(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                WITH delivery_base AS (
                    SELECT
                        d.id                                                AS delivery_id,
                        d.schedule_date,
                        DATE_FORMAT(d.schedule_date, '%%b %%d, %%Y')       AS date_fmt,
                        TRIM(c.full_name)                                   AS customer,
                        d.status                                            AS delivery_status,
                        COALESCE(t.payment_status, 'unpaid')                AS payment_status,
                        COALESCE(t.total_amount, 0)                         AS total_amount
                    FROM deliveries d
                    INNER JOIN customers c ON c.id = d.customer_id
                    LEFT  JOIN transactions t ON t.delivery_id = d.id
                    WHERE d.schedule_date BETWEEN %s AND %s
                )
                SELECT
                    db.delivery_id                                          AS id,
                    db.schedule_date,
                    db.date_fmt                                             AS date,
                    db.customer,
                    CONCAT(
                        TRIM(p.name), ' ',
                        COALESCE(p.cylinder_size, '')
                    )                                                       AS product,
                    di.quantity,
                    di.type,
                    ROUND(di.quantity * di.price_at_delivery, 2)            AS amount,
                    db.delivery_status                                      AS status,
                    db.payment_status,
                    db.total_amount
                FROM delivery_base db
                INNER JOIN delivery_items di ON di.delivery_id = db.delivery_id
                INNER JOIN lpg_products   p  ON p.id           = di.product_id
                ORDER BY db.schedule_date DESC, db.delivery_id ASC, p.name ASC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_daily_reports(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    dr.report_date,
                    DATE_FORMAT(dr.report_date, '%%b %%d, %%Y')            AS report_date_fmt,
                    dr.total_deliveries,
                    dr.total_delivered,
                    dr.total_cancelled,
                    dr.total_pending,
                    ROUND(dr.total_sales, 2)                                AS total_sales,
                    DATEDIFF(CURDATE(), dr.report_date)                    AS days_ago,
                    ROUND(
                        SUM(dr.total_sales) OVER (
                            ORDER BY dr.report_date ASC
                        ), 2
                    )                                                       AS running_sales_total
                FROM daily_reports dr
                WHERE dr.report_date BETWEEN %s AND %s
                ORDER BY dr.report_date DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_weekly_reports(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    wr.week_start,
                    wr.week_end,
                    DATE_FORMAT(wr.week_start, '%%b %%d')                  AS week_start_fmt,
                    DATE_FORMAT(wr.week_end,   '%%b %%d, %%Y')             AS week_end_fmt,
                    wr.total_deliveries,
                    wr.total_delivered,
                    wr.total_cancelled,
                    wr.total_pending,
                    ROUND(wr.total_sales, 2)                                AS total_sales,
                    RANK() OVER (
                        ORDER BY wr.total_sales DESC
                    )                                                       AS sales_rank
                FROM weekly_reports wr
                WHERE wr.week_start >= %s
                  AND wr.week_end   <= %s
                ORDER BY wr.week_start DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_monthly_reports(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    mr.report_month,
                    DATE_FORMAT(mr.report_month, '%%M %%Y')                AS report_month_fmt,
                    mr.total_deliveries,
                    mr.total_delivered,
                    mr.total_cancelled,
                    mr.total_pending,
                    ROUND(mr.total_sales, 2)                                AS total_sales,
                    ROUND(
                        SUM(mr.total_sales) OVER (
                            PARTITION BY YEAR(mr.report_month)
                            ORDER BY mr.report_month ASC
                        ), 2
                    )                                                       AS ytd_sales
                FROM monthly_reports mr
                WHERE mr.report_month BETWEEN %s AND %s
                ORDER BY mr.report_month DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_top_customers(date_from, date_to, limit=5):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id                                                    AS customer_id,
                    TRIM(c.full_name)                                       AS customer_name,
                    COUNT(DISTINCT d.id)                                    AS total_deliveries,
                    SUM(CASE WHEN d.status = 'delivered'
                             THEN 1 ELSE 0 END)                            AS completed_deliveries,
                    COALESCE(SUM(t.total_amount), 0)                        AS total_spent,
                    ROUND(COALESCE(SUM(t.total_amount), 0), 2)              AS total_spent_rounded,
                    RANK() OVER (
                        ORDER BY COALESCE(SUM(t.total_amount), 0) DESC
                    )                                                       AS spending_rank,
                    ROUND(
                        COALESCE(SUM(t.total_amount), 0)
                        / NULLIF((
                            SELECT SUM(t2.total_amount)
                            FROM transactions t2
                            INNER JOIN deliveries d2 ON d2.id = t2.delivery_id
                            WHERE d2.schedule_date BETWEEN %s AND %s
                        ), 0) * 100, 2
                    )                                                       AS revenue_share_pct
                FROM customers c
                INNER JOIN deliveries d   ON d.customer_id  = c.id
                LEFT  JOIN transactions t ON t.delivery_id  = d.id
                WHERE d.schedule_date BETWEEN %s AND %s
                GROUP BY c.id, c.full_name
                ORDER BY total_spent DESC
                LIMIT %s
            """, (date_from, date_to, date_from, date_to, limit))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_sales_by_product(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id                                                    AS product_id,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size,''))
                                                                            AS product_name,
                    SUM(di.quantity)                                        AS total_quantity,
                    COUNT(DISTINCT di.delivery_id)                          AS total_orders,
                    ROUND(SUM(di.quantity * di.price_at_delivery), 2)       AS total_revenue,
                    ROUND(
                        SUM(di.quantity * di.price_at_delivery)
                        / NULLIF(
                            SUM(SUM(di.quantity * di.price_at_delivery))
                            OVER (), 0
                        ) * 100, 2
                    )                                                       AS revenue_share_pct
                FROM lpg_products p
                INNER JOIN delivery_items di ON di.product_id  = p.id
                INNER JOIN deliveries     d  ON d.id           = di.delivery_id
                WHERE d.schedule_date BETWEEN %s AND %s
                  AND d.status = 'delivered'
                GROUP BY p.id, p.name, p.cylinder_size
                ORDER BY total_revenue DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_period_comparison(current_from, current_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)

            from datetime import date as dt_date
            if isinstance(current_from, str):
                from datetime import datetime
                cf = datetime.strptime(current_from, "%Y-%m-%d").date()
                ct = datetime.strptime(current_to,   "%Y-%m-%d").date()
            else:
                cf = current_from
                ct = current_to

            from datetime import timedelta
            delta       = (ct - cf).days + 1
            prev_to     = cf - timedelta(days=1)
            prev_from   = prev_to - timedelta(days=delta - 1)

            cursor.execute("""
                SELECT
                    'current'                                               AS period,
                    COUNT(d.id)                                             AS total_deliveries,
                    SUM(CASE WHEN d.status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
                    ROUND(COALESCE(SUM(t.total_amount), 0), 2)              AS total_sales
                FROM deliveries d
                LEFT JOIN transactions t ON t.delivery_id = d.id
                WHERE d.schedule_date BETWEEN %s AND %s

                UNION ALL

                SELECT
                    'previous'                                              AS period,
                    COUNT(d2.id)                                            AS total_deliveries,
                    SUM(CASE WHEN d2.status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
                    ROUND(COALESCE(SUM(t2.total_amount), 0), 2)             AS total_sales
                FROM deliveries d2
                LEFT JOIN transactions t2 ON t2.delivery_id = d2.id
                WHERE d2.schedule_date BETWEEN %s AND %s
            """, (cf, ct, prev_from, prev_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
