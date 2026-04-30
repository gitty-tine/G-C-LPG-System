from database.connection import get_connection


class CustomerModel:
    CUSTOMER_SUMMARY_COLUMNS = """
        id,
        full_name,
        address,
        contact_number,
        notes,
        created_at_fmt AS created_at,
        total_deliveries,
        last_delivery
    """

    @staticmethod
    def get_all():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"""
                SELECT {CustomerModel.CUSTOMER_SUMMARY_COLUMNS}
                FROM vw_customer_summary v
                ORDER BY v.created_at DESC, id DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_id(customer_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"""
                SELECT {CustomerModel.CUSTOMER_SUMMARY_COLUMNS}
                FROM vw_customer_summary
                WHERE id = %s
            """, (customer_id,))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def search(keyword):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            term = f"%{keyword.lower()}%"
            cursor.execute(f"""
                SELECT {CustomerModel.CUSTOMER_SUMMARY_COLUMNS}
                FROM vw_customer_summary
                WHERE
                    LOWER(full_name)       LIKE %s OR
                    LOWER(address)         LIKE %s OR
                    LOWER(contact_number)  LIKE %s OR
                    LOWER(notes)           LIKE %s
                ORDER BY full_name ASC
            """, (term, term, term, term))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_active():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    contact_number,
                    address
                FROM vw_customer_summary
                WHERE delivered_deliveries > 0
                ORDER BY full_name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_dropdown_list():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    address,
                    contact_number,
                    last_delivery_date AS last_order_date
                FROM vw_customer_summary
                ORDER BY full_name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add(full_name, address, contact_number, notes, user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_add_customer", [full_name, address, contact_number, notes or ""])
            new_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    new_id = row[0]
            conn.commit()
            return new_id
        except Exception as exc:
            if conn:
                conn.rollback()
            msg = str(exc)
            if "45000" in msg or "1644" in msg:
                raise ValueError(msg.split(":")[-1].strip())
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update(customer_id, full_name, address, contact_number, notes, user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_update_customer", [customer_id, full_name, address, contact_number, notes or ""])
            conn.commit()
            return True
        except Exception as exc:
            if conn:
                conn.rollback()
            msg = str(exc)
            if "45000" in msg or "1644" in msg:
                raise ValueError(msg.split(":")[-1].strip())
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete(customer_id, user_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_delete_customer", [customer_id])
            conn.commit()
            return True
        except Exception as exc:
            if conn:
                conn.rollback()
            msg = str(exc)
            if "45000" in msg or "1644" in msg:
                raise ValueError(msg.split(":")[-1].strip())
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
