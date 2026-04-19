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
    def get_sales_kpis():
        conn   = None
        cursor = None
        try:
            today = OwnerDashboardModel._today()
            week_start, week_end = OwnerDashboardModel._week_bounds(today)
            month_start, month_end = OwnerDashboardModel._month_bounds(today)
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    ROUND(COALESCE(SUM(
                        CASE WHEN vt.schedule_date = %s
                             THEN vt.total_amount ELSE 0 END
                    ), 0), 2)                                               AS total_sales_today,
                    ROUND(COALESCE(SUM(
                        CASE WHEN vt.schedule_date BETWEEN %s AND %s
                             THEN vt.total_amount ELSE 0 END
                    ), 0), 2)                                               AS total_sales_this_week,
                    ROUND(COALESCE(SUM(
                        CASE WHEN vt.schedule_date BETWEEN %s AND %s
                             THEN vt.total_amount ELSE 0 END
                    ), 0), 2)                                               AS total_sales_this_month
                FROM vw_transaction_summary vt
            """, (today, week_start, week_end, month_start, month_end))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_delivery_counts_today():
        conn   = None
        cursor = None
        try:
            today = OwnerDashboardModel._today()
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(*)                                                AS total_today,
                    COALESCE(SUM(CASE WHEN vt.delivery_status = 'delivered'
                                      THEN 1 ELSE 0 END), 0)               AS delivered_today,
                    COALESCE(SUM(CASE WHEN vt.delivery_status = 'cancelled'
                                      THEN 1 ELSE 0 END), 0)               AS cancelled_today,
                    COALESCE(SUM(CASE WHEN vt.delivery_status = 'pending'
                                      THEN 1 ELSE 0 END), 0)               AS pending_today,
                    COALESCE(SUM(CASE WHEN vt.delivery_status = 'in_transit'
                                      THEN 1 ELSE 0 END), 0)               AS in_transit_today,
                    ROUND(COALESCE(SUM(
                        CASE WHEN vt.delivery_status = 'delivered'
                             THEN COALESCE(vt.total_amount, 0) ELSE 0 END
                    ), 0), 2)                                               AS sales_today
                FROM vw_transaction_summary vt
                WHERE vt.schedule_date = %s
            """, (today,))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_weekly_chart_data():
        conn   = None
        cursor = None
        try:
            week_start, _ = OwnerDashboardModel._week_bounds()
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    cal.day_label,
                    cal.cal_date,
                    ROUND(COALESCE(SUM(vt.total_amount), 0), 2)            AS daily_sales,
                    COUNT(DISTINCT vt.transaction_id)                       AS delivery_count
                FROM (
                    SELECT
                        DATE_ADD(
                            %s,
                            INTERVAL seq.n DAY
                        )                                                   AS cal_date,
                        CASE seq.n
                            WHEN 0 THEN 'Mon'
                            WHEN 1 THEN 'Tue'
                            WHEN 2 THEN 'Wed'
                            WHEN 3 THEN 'Thu'
                            WHEN 4 THEN 'Fri'
                            WHEN 5 THEN 'Sat'
                            WHEN 6 THEN 'Sun'
                        END                                                 AS day_label
                    FROM (
                        SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
                        UNION ALL SELECT 3 UNION ALL SELECT 4
                        UNION ALL SELECT 5 UNION ALL SELECT 6
                    ) seq
                ) cal
                LEFT JOIN vw_transaction_summary vt
                    ON vt.schedule_date = cal.cal_date
                    AND vt.delivery_status = 'delivered'
                GROUP BY cal.cal_date, cal.day_label
                ORDER BY cal.cal_date ASC
            """, (week_start,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_top_customers(limit=5):
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
                    ROUND(COALESCE(SUM(t.total_amount), 0), 2)              AS total_spent,
                    RANK() OVER (
                        ORDER BY COALESCE(SUM(t.total_amount), 0) DESC
                    )                                                       AS spending_rank,
                    ROUND(
                        COALESCE(SUM(t.total_amount), 0)
                        / NULLIF((
                            SELECT SUM(t2.total_amount)
                            FROM transactions t2
                        ), 0) * 100, 0
                    )                                                       AS revenue_share_pct
                FROM customers c
                INNER JOIN deliveries   d ON d.customer_id = c.id
                LEFT  JOIN transactions t ON t.delivery_id = d.id
                WHERE d.status = 'delivered'
                GROUP BY c.id, c.full_name
                ORDER BY total_spent DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_recent_transactions(limit=5):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    t.id                                                    AS transaction_id,
                    t.delivery_id,
                    TRIM(vt.customer_name)                                  AS customer_name,
                    vt.schedule_date                                        AS delivery_date,
                    DATE_FORMAT(vt.schedule_date, '%b %d, %Y')             AS delivery_date_fmt,
                    t.total_amount,
                    FORMAT(t.total_amount, 2)                               AS total_amount_fmt,
                    t.payment_status,
                    DATE_FORMAT(t.paid_at, '%b %d, %Y')                    AS paid_at_fmt
                FROM vw_transaction_summary vt
                INNER JOIN transactions t ON t.id = vt.transaction_id
                ORDER BY t.created_at DESC, t.id DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_all_dashboard_data():
        return {
            "sales_kpis":          OwnerDashboardModel.get_sales_kpis(),
            "delivery_counts":     OwnerDashboardModel.get_delivery_counts_today(),
            "weekly_chart":        OwnerDashboardModel.get_weekly_chart_data(),
            "top_customers":       OwnerDashboardModel.get_top_customers(limit=5),
            "recent_transactions": OwnerDashboardModel.get_recent_transactions(limit=5),
        }
