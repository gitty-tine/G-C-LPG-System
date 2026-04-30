from datetime import date, timedelta

from database.connection import get_connection


class OwnerDashboardModel:
    @staticmethod
    def _today():
        return date.today()

    @staticmethod
    def _week_bounds(day_value=None):
        current_day = day_value or OwnerDashboardModel._today()
        week_start = current_day - timedelta(days=current_day.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    @staticmethod
    def _month_bounds(day_value=None):
        current_day = day_value or OwnerDashboardModel._today()
        month_start = current_day.replace(day=1)
        if month_start.month == 12:
            next_month_start = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month_start = month_start.replace(month=month_start.month + 1)
        month_end = next_month_start - timedelta(days=1)
        return month_start, month_end

    @staticmethod
    def _previous_month_bounds(day_value=None):
        month_start, _ = OwnerDashboardModel._month_bounds(day_value)
        previous_month_end = month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)
        return previous_month_start, previous_month_end

    @staticmethod
    def _sales_kpi_defaults():
        return {
            "total_sales_today": 0,
            "total_sales_this_week": 0,
            "total_sales_this_month": 0,
            "total_sales_last_month": 0,
            "month_sales_change_pct": 0,
            "total_receivables": 0,
        }

    @staticmethod
    def _delivery_count_defaults():
        return {
            "total_today": 0,
            "delivered_today": 0,
            "cancelled_today": 0,
            "pending_today": 0,
            "in_transit_today": 0,
            "delivery_success_rate": 0,
            "cancellation_rate": 0,
        }

    @staticmethod
    def _merge_defaults(defaults, row):
        merged = defaults.copy()
        if row:
            merged.update(row)
        return merged

    @staticmethod
    def _fetch_sales_kpis(cursor, today=None):
        today = today or OwnerDashboardModel._today()
        week_start, week_end = OwnerDashboardModel._week_bounds(today)
        month_start, month_end = OwnerDashboardModel._month_bounds(today)
        previous_month_start, previous_month_end = OwnerDashboardModel._previous_month_bounds(today)
        range_start = min(today, week_start, month_start, previous_month_start)
        range_end = max(today, week_end, month_end, previous_month_end)

        cursor.execute("""
            SELECT
                ROUND(today_sales, 2)                                  AS total_sales_today,
                ROUND(week_sales, 2)                                   AS total_sales_this_week,
                ROUND(month_sales, 2)                                  AS total_sales_this_month,
                ROUND(last_month_sales, 2)                             AS total_sales_last_month,
                ROUND(
                    COALESCE(
                        (month_sales - last_month_sales)
                        / NULLIF(last_month_sales, 0) * 100,
                        0
                    ),
                    2
                )                                                       AS month_sales_change_pct,
                (
                    SELECT ROUND(COALESCE(SUM(unpaid_sales), 0), 2)
                    FROM vw_owner_dashboard_daily
                )                                                       AS total_receivables
            FROM (
                SELECT
                    COALESCE(SUM(
                        CASE WHEN schedule_date = %s
                             THEN recognized_sales ELSE 0 END
                    ), 0)                                               AS today_sales,
                    COALESCE(SUM(
                        CASE WHEN schedule_date BETWEEN %s AND %s
                             THEN recognized_sales ELSE 0 END
                    ), 0)                                               AS week_sales,
                    COALESCE(SUM(
                        CASE WHEN schedule_date BETWEEN %s AND %s
                             THEN recognized_sales ELSE 0 END
                    ), 0)                                               AS month_sales,
                    COALESCE(SUM(
                        CASE WHEN schedule_date BETWEEN %s AND %s
                             THEN recognized_sales ELSE 0 END
                    ), 0)                                               AS last_month_sales
                FROM vw_owner_dashboard_daily
                WHERE schedule_date BETWEEN %s AND %s
            ) totals
        """, (
            today,
            week_start,
            week_end,
            month_start,
            month_end,
            previous_month_start,
            previous_month_end,
            range_start,
            range_end,
        ))
        return OwnerDashboardModel._merge_defaults(
            OwnerDashboardModel._sales_kpi_defaults(),
            cursor.fetchone(),
        )

    @staticmethod
    def _fetch_delivery_counts_today(cursor, today=None):
        today = today or OwnerDashboardModel._today()
        cursor.execute("""
            SELECT
                COALESCE(SUM(total_deliveries), 0)                         AS total_today,
                COALESCE(SUM(delivered_deliveries), 0)                     AS delivered_today,
                COALESCE(SUM(cancelled_deliveries), 0)                     AS cancelled_today,
                COALESCE(SUM(pending_deliveries), 0)                       AS pending_today,
                COALESCE(SUM(in_transit_deliveries), 0)                    AS in_transit_today,
                ROUND(
                    COALESCE(
                        SUM(delivered_deliveries)
                        / NULLIF(SUM(total_deliveries), 0) * 100,
                        0
                    ),
                    0
                )                                                          AS delivery_success_rate,
                ROUND(
                    COALESCE(
                        SUM(cancelled_deliveries)
                        / NULLIF(SUM(total_deliveries), 0) * 100,
                        0
                    ),
                    0
                )                                                          AS cancellation_rate
            FROM vw_owner_dashboard_daily
            WHERE schedule_date = %s
        """, (today,))
        return OwnerDashboardModel._merge_defaults(
            OwnerDashboardModel._delivery_count_defaults(),
            cursor.fetchone(),
        )

    @staticmethod
    def _fetch_weekly_chart_data(cursor, week_start=None):
        week_start = week_start or OwnerDashboardModel._week_bounds()[0]
        cursor.execute("""
            SELECT
                cal.day_label,
                cal.cal_date,
                ROUND(COALESCE(od.recognized_sales, 0), 2)                 AS daily_sales
            FROM (
                SELECT
                    DATE_ADD(%s, INTERVAL seq.n DAY)                       AS cal_date,
                    CASE seq.n
                        WHEN 0 THEN 'Mon'
                        WHEN 1 THEN 'Tue'
                        WHEN 2 THEN 'Wed'
                        WHEN 3 THEN 'Thu'
                        WHEN 4 THEN 'Fri'
                        WHEN 5 THEN 'Sat'
                        WHEN 6 THEN 'Sun'
                    END                                                    AS day_label
                FROM (
                    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
                    UNION ALL SELECT 3 UNION ALL SELECT 4
                    UNION ALL SELECT 5 UNION ALL SELECT 6
                ) seq
            ) cal
            LEFT JOIN vw_owner_dashboard_daily od
                ON od.schedule_date = cal.cal_date
            ORDER BY cal.cal_date ASC
        """, (week_start,))
        return cursor.fetchall()

    @staticmethod
    def _fetch_top_customers(cursor, limit=5, month_start=None, month_end=None):
        if month_start is None or month_end is None:
            month_start, month_end = OwnerDashboardModel._month_bounds()

        cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                total_spent,
                ROUND(
                    COALESCE(
                        total_spent / NULLIF(SUM(total_spent) OVER (), 0) * 100,
                        0
                    ),
                    0
                )                                                          AS revenue_share_pct
            FROM (
                SELECT
                    customer_id,
                    customer_name,
                    ROUND(COALESCE(SUM(recognized_sales), 0), 2)            AS total_spent
                FROM vw_report_delivery_financials
                WHERE schedule_date BETWEEN %s AND %s
                GROUP BY customer_id, customer_name
                HAVING total_spent > 0
            ) customer_totals
            ORDER BY total_spent DESC, customer_name ASC
            LIMIT %s
        """, (month_start, month_end, limit))
        return cursor.fetchall()

    @staticmethod
    def _fetch_recent_transactions(cursor, limit=5):
        cursor.execute("""
            SELECT
                t.id                                                        AS transaction_id,
                t.delivery_id,
                TRIM(vt.customer_name)                                      AS customer_name,
                vt.schedule_date                                            AS delivery_date,
                DATE_FORMAT(vt.schedule_date, '%b %d, %Y')                  AS delivery_date_fmt,
                t.total_amount,
                FORMAT(t.total_amount, 2)                                   AS total_amount_fmt,
                COALESCE(t.payment_status, 'unpaid')                        AS payment_status,
                DATE_FORMAT(t.paid_at, '%b %d, %Y')                         AS paid_at_fmt
            FROM vw_transaction_summary vt
            INNER JOIN transactions t ON t.id = vt.transaction_id
            ORDER BY t.created_at DESC, t.id DESC
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()

    @staticmethod
    def get_all_dashboard_data():
        today = OwnerDashboardModel._today()
        week_start, _ = OwnerDashboardModel._week_bounds(today)
        month_start, month_end = OwnerDashboardModel._month_bounds(today)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            return {
                "sales_kpis": OwnerDashboardModel._fetch_sales_kpis(cursor, today=today),
                "delivery_counts": OwnerDashboardModel._fetch_delivery_counts_today(cursor, today=today),
                "weekly_chart": OwnerDashboardModel._fetch_weekly_chart_data(cursor, week_start=week_start),
                "top_customers": OwnerDashboardModel._fetch_top_customers(
                    cursor,
                    limit=5,
                    month_start=month_start,
                    month_end=month_end,
                ),
                "recent_transactions": OwnerDashboardModel._fetch_recent_transactions(cursor, limit=5),
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
