from database.connection import get_connection


class CustomerModel:
    ## This is for listing and search results
    @staticmethod
    def get_all():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)                               AS full_name,
                    TRIM(c.address)                                 AS address,
                    c.contact_number,
                    COALESCE(c.notes, '')                           AS notes,
                    DATE_FORMAT(c.created_at, '%b %d, %Y')         AS created_at,
                    COUNT(d.id)                                     AS total_deliveries,
                    COALESCE(MAX(DATE_FORMAT(
                        d.schedule_date, '%b %d, %Y')), '—')        AS last_delivery
                FROM customers c
                LEFT JOIN deliveries d ON d.customer_id = c.id
                GROUP BY
                    c.id, c.full_name, c.address,
                    c.contact_number, c.notes, c.created_at
                ORDER BY c.created_at DESC, c.id DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    ## This is for audit logs
    @staticmethod
    def get_by_id(customer_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)                       AS full_name,
                    TRIM(c.address)                         AS address,
                    c.contact_number,
                    COALESCE(c.notes, '')                   AS notes,
                    DATE_FORMAT(c.created_at, '%b %d, %Y') AS created_at,
                    (
                        SELECT DATE_FORMAT(MAX(d.schedule_date), '%b %d, %Y')
                        FROM deliveries d
                        WHERE d.customer_id = c.id
                    )                                       AS last_delivery,
                    (
                        SELECT COUNT(*)
                        FROM deliveries d
                        WHERE d.customer_id = c.id
                    )                                       AS total_deliveries
                FROM customers c
                WHERE c.id = %s
            """, (customer_id,))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    ## This is for seach results, to show only the customers that match what you typed.
    @staticmethod
    def search(keyword):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            term = f"%{keyword.lower()}%"
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)                               AS full_name,
                    TRIM(c.address)                                 AS address,
                    c.contact_number,
                    COALESCE(c.notes, '')                           AS notes,
                    DATE_FORMAT(c.created_at, '%b %d, %Y')         AS created_at,
                    COUNT(d.id)                                     AS total_deliveries
                FROM customers c
                LEFT JOIN deliveries d ON d.customer_id = c.id
                WHERE
                    LOWER(c.full_name)       LIKE %s OR
                    LOWER(c.address)         LIKE %s OR
                    LOWER(c.contact_number)  LIKE %s OR
                    LOWER(c.notes)           LIKE %s
                GROUP BY
                    c.id, c.full_name, c.address,
                    c.contact_number, c.notes, c.created_at
                ORDER BY c.full_name ASC
            """, (term, term, term, term))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_active():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)   AS full_name,
                    c.contact_number,
                    c.address
                FROM customers c
                WHERE c.id IN (
                    SELECT DISTINCT customer_id
                    FROM deliveries
                    WHERE status = 'delivered'
                )
                ORDER BY c.full_name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    ## this is for dropdown of delivery form to show all list of customers
    @staticmethod
    def get_dropdown_list():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)   AS full_name,
                    c.address,
                    c.contact_number,
                    (
                        SELECT MAX(d.schedule_date)
                        FROM deliveries d
                        WHERE d.customer_id = c.id
                    ) AS last_order_date
                FROM customers c
                ORDER BY c.full_name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def add(full_name, address, contact_number, notes, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc(
                "sp_add_customer",
                [full_name, address, contact_number, notes or '']
            )
            new_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    new_id = row[0]
            conn.commit()
            return new_id
        except Exception as e:
            if conn:
                conn.rollback()
            msg = str(e)
            if "45000" in msg or "1644" in msg:
                clean = msg.split(":")[-1].strip()
                raise ValueError(clean)
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def update(customer_id, full_name, address, contact_number, notes, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))

            cursor.callproc(
                "sp_update_customer",
                [customer_id, full_name, address, contact_number, notes or '']
            )
            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            msg = str(e)
            if "45000" in msg or "1644" in msg:
                clean = msg.split(":")[-1].strip()
                raise ValueError(clean)
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def delete(customer_id, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc("sp_delete_customer", [customer_id])
            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            msg = str(e)
            if "45000" in msg or "1644" in msg:
                raise ValueError(msg.split(":")[-1].strip())
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
