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
                    COUNT(*)                                               AS snapshot_count,
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_in_transit), 0)                      AS total_in_transit,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales,
                    COALESCE(SUM(total_paid), 0)                            AS total_paid,
                    COALESCE(SUM(total_unpaid), 0)                          AS total_unpaid
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
                    COUNT(*)                                               AS snapshot_count,
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_in_transit), 0)                      AS total_in_transit,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales,
                    COALESCE(SUM(total_paid), 0)                            AS total_paid,
                    COALESCE(SUM(total_unpaid), 0)                          AS total_unpaid
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
                    COUNT(*)                                               AS snapshot_count,
                    COALESCE(SUM(total_deliveries), 0)                      AS total_deliveries,
                    COALESCE(SUM(total_delivered), 0)                       AS total_delivered,
                    COALESCE(SUM(total_cancelled), 0)                       AS total_cancelled,
                    COALESCE(SUM(total_pending), 0)                         AS total_pending,
                    COALESCE(SUM(total_in_transit), 0)                      AS total_in_transit,
                    COALESCE(SUM(total_sales), 0)                           AS total_sales,
                    COALESCE(SUM(total_paid), 0)                            AS total_paid,
                    COALESCE(SUM(total_unpaid), 0)                          AS total_unpaid
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
                    COUNT(*)                                                AS total_deliveries,
                    COALESCE(SUM(delivered_count), 0)                       AS total_delivered,
                    COALESCE(SUM(cancelled_count), 0)                       AS total_cancelled,
                    COALESCE(SUM(pending_count), 0)                         AS total_pending,
                    COALESCE(SUM(in_transit_count), 0)                      AS total_in_transit,
                    COALESCE(SUM(recognized_sales), 0)                      AS total_sales,
                    COALESCE(SUM(paid_sales), 0)                            AS total_paid,
                    COALESCE(SUM(unpaid_sales), 0)                          AS total_unpaid,
                    COALESCE(AVG(
                        CASE WHEN delivery_status = 'delivered'
                             THEN recognized_sales END
                    ), 0)                                                   AS avg_transaction_value,
                    DATE_FORMAT(%s, '%b %d, %Y')                          AS date_from_fmt,
                    DATE_FORMAT(%s, '%b %d, %Y')                          AS date_to_fmt
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s
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
                SELECT
                    delivery_id                                             AS id,
                    schedule_date,
                    DATE_FORMAT(schedule_date, '%b %d, %Y')                AS date,
                    customer_name                                           AS customer,
                    product_name                                            AS product,
                    quantity,
                    type,
                    line_amount                                             AS amount,
                    delivery_status                                         AS status,
                    payment_status,
                    line_amount                                             AS total_amount
                FROM vw_report_delivery_lines
                WHERE schedule_date BETWEEN %s AND %s
                ORDER BY schedule_date DESC, delivery_id ASC, product_name ASC
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
                    DATE_FORMAT(dr.report_date, '%b %d, %Y')              AS report_date_fmt,
                    dr.total_deliveries,
                    dr.total_delivered,
                    dr.total_cancelled,
                    dr.total_pending,
                    dr.total_in_transit,
                    ROUND(dr.total_sales, 2)                                AS total_sales,
                    ROUND(dr.total_paid, 2)                                 AS total_paid,
                    ROUND(dr.total_unpaid, 2)                               AS total_unpaid,
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
                    DATE_FORMAT(wr.week_start, '%b %d')                   AS week_start_fmt,
                    DATE_FORMAT(wr.week_end,   '%b %d, %Y')               AS week_end_fmt,
                    wr.total_deliveries,
                    wr.total_delivered,
                    wr.total_cancelled,
                    wr.total_pending,
                    wr.total_in_transit,
                    ROUND(wr.total_sales, 2)                                AS total_sales,
                    ROUND(wr.total_paid, 2)                                 AS total_paid,
                    ROUND(wr.total_unpaid, 2)                               AS total_unpaid,
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
                    DATE_FORMAT(mr.report_month, '%M %Y')                 AS report_month_fmt,
                    mr.total_deliveries,
                    mr.total_delivered,
                    mr.total_cancelled,
                    mr.total_pending,
                    mr.total_in_transit,
                    ROUND(mr.total_sales, 2)                                AS total_sales,
                    ROUND(mr.total_paid, 2)                                 AS total_paid,
                    ROUND(mr.total_unpaid, 2)                               AS total_unpaid,
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
                    customer_id,
                    customer_name,
                    COUNT(*)                                                AS total_deliveries,
                    COALESCE(SUM(delivered_count), 0)                       AS completed_deliveries,
                    COALESCE(SUM(recognized_sales), 0)                      AS total_spent,
                    ROUND(COALESCE(SUM(recognized_sales), 0), 2)            AS total_spent_rounded,
                    RANK() OVER (
                        ORDER BY COALESCE(SUM(recognized_sales), 0) DESC
                    )                                                       AS spending_rank,
                    ROUND(
                        COALESCE(SUM(recognized_sales), 0)
                        / NULLIF((
                            SELECT SUM(recognized_sales)
                            FROM vw_report_delivery_financials
                            WHERE schedule_date BETWEEN %s AND %s
                        ), 0) * 100, 2
                    )                                                       AS revenue_share_pct
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s
                GROUP BY customer_id, customer_name
                HAVING total_spent > 0
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
                    product_id,
                    product_name,
                    SUM(quantity)                                           AS total_quantity,
                    COUNT(DISTINCT delivery_id)                             AS total_orders,
                    ROUND(SUM(recognized_line_sales), 2)                    AS total_revenue,
                    ROUND(
                        SUM(recognized_line_sales)
                        / NULLIF(
                            SUM(SUM(recognized_line_sales))
                            OVER (), 0
                        ) * 100, 2
                    )                                                       AS revenue_share_pct
                FROM vw_report_delivery_lines
                WHERE schedule_date BETWEEN %s AND %s
                  AND delivery_status = 'delivered'
                GROUP BY product_id, product_name
                ORDER BY total_revenue DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_report_insights(date_from, date_to):
        defaults = {
            "peak_sales_day": "",
            "peak_sales_amount": 0,
            "most_sold_product": "",
            "most_sold_product_quantity": 0,
            "most_sold_product_revenue": 0,
        }
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    DAYNAME(schedule_date)                                 AS peak_sales_day,
                    ROUND(COALESCE(SUM(recognized_sales), 0), 2)            AS peak_sales_amount
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s
                  AND delivery_status = 'delivered'
                GROUP BY DAYOFWEEK(schedule_date), DAYNAME(schedule_date)
                HAVING peak_sales_amount > 0
                ORDER BY peak_sales_amount DESC, DAYOFWEEK(schedule_date) ASC
                LIMIT 1
            """, (date_from, date_to))
            peak_day = cursor.fetchone() or {}

            cursor.execute("""
                SELECT
                    product_name                                            AS most_sold_product,
                    COALESCE(SUM(quantity), 0)                              AS most_sold_product_quantity,
                    ROUND(COALESCE(SUM(recognized_line_sales), 0), 2)       AS most_sold_product_revenue
                FROM vw_report_delivery_lines
                WHERE schedule_date BETWEEN %s AND %s
                  AND delivery_status = 'delivered'
                GROUP BY product_id, product_name
                HAVING most_sold_product_quantity > 0
                ORDER BY most_sold_product_quantity DESC,
                         most_sold_product_revenue DESC,
                         product_name ASC
                LIMIT 1
            """, (date_from, date_to))
            most_sold = cursor.fetchone() or {}

            insights = defaults.copy()
            insights.update(peak_day)
            insights.update(most_sold)
            return insights
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


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
                    COUNT(*)                                                AS total_deliveries,
                    COALESCE(SUM(delivered_count), 0)                       AS delivered,
                    ROUND(COALESCE(SUM(recognized_sales), 0), 2)            AS total_sales
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s

                UNION ALL

                SELECT
                    'previous'                                              AS period,
                    COUNT(*)                                                AS total_deliveries,
                    COALESCE(SUM(delivered_count), 0)                       AS delivered,
                    ROUND(COALESCE(SUM(recognized_sales), 0), 2)            AS total_sales
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s
            """, (cf, ct, prev_from, prev_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
