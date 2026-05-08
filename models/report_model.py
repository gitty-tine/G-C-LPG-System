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
            # Stored procedure: returns aggregate totals from daily report snapshots.
            cursor.callproc("sp_get_daily_snapshot_summary", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchone()
            return None
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
            # Stored procedure: returns aggregate totals from weekly report snapshots.
            cursor.callproc("sp_get_weekly_snapshot_summary", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchone()
            return None
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
            # Stored procedure: returns aggregate totals from monthly report snapshots.
            cursor.callproc("sp_get_monthly_snapshot_summary", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchone()
            return None
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
            # Stored procedure: returns the main delivery financial summary for a date range.
            cursor.callproc("sp_get_report_summary", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchone()
            return None
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
            # Stored procedure: returns one financial row per delivery for the report range.
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
            # Stored procedure: returns product-level delivery report line items.
            cursor.callproc("sp_get_report_lines", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: returns saved daily report snapshot rows.
            cursor.callproc("sp_get_daily_reports", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: returns saved weekly report snapshot rows.
            cursor.callproc("sp_get_weekly_reports", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: returns saved monthly report snapshot rows.
            cursor.callproc("sp_get_monthly_reports", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: ranks customers by spending in the report range.
            cursor.callproc("sp_get_top_customers", [date_from, date_to, limit])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: groups delivered sales by product in the report range.
            cursor.callproc("sp_get_sales_by_product", [date_from, date_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
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
            # Stored procedure: returns highlight metrics such as peak day and most-sold product.
            cursor.callproc("sp_get_report_insights", [date_from, date_to])
            for result in cursor.stored_results():
                insights = defaults.copy()
                insights.update(result.fetchone() or {})
                return insights
            return defaults
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
            # Stored procedure: compares the selected period with the previous matching period.
            cursor.callproc("sp_get_period_comparison", [current_from, current_to])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
