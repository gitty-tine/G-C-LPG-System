from database.connection import get_connection


class OwnerProductModel:
    @staticmethod
    def get_all():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id,
                    TRIM(p.name)                                            AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                     AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                            AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                             AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                             AS new_tank_price_fmt,
                    COALESCE(SUM(di.quantity), 0)                           AS total_sold,
                    COUNT(DISTINCT di.delivery_id)                          AS total_deliveries
                FROM lpg_products p
                LEFT JOIN delivery_items di ON di.product_id = p.id
                GROUP BY
                    p.id, p.name, p.cylinder_size,
                    p.refill_price, p.new_tank_price
                ORDER BY p.name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()


    @staticmethod
    def get_by_id(product_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id,
                    TRIM(p.name)                                            AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                     AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                            AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                             AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                             AS new_tank_price_fmt,
                    (
                        SELECT MAX(d.schedule_date)
                        FROM deliveries d
                        INNER JOIN delivery_items di ON di.delivery_id = d.id
                        WHERE di.product_id = p.id
                    )                                                       AS last_ordered,
                    (
                        SELECT COALESCE(SUM(di2.quantity * di2.price_at_delivery), 0)
                        FROM delivery_items di2
                        WHERE di2.product_id = p.id
                    )                                                       AS total_revenue
                FROM lpg_products p
                WHERE p.id = %s
            """, (product_id,))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def search(keyword):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            term = f"%{keyword.strip().lower()}%"
            cursor.execute("""
                SELECT
                    p.id,
                    TRIM(p.name)                                            AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                     AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                            AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                             AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                             AS new_tank_price_fmt
                FROM lpg_products p
                WHERE
                    LOWER(TRIM(p.name))          LIKE %s OR
                    LOWER(TRIM(p.cylinder_size)) LIKE %s OR
                    LOWER(CONCAT(
                        TRIM(p.name), ' ', COALESCE(p.cylinder_size, '')
                    ))                           LIKE %s
                ORDER BY p.name ASC
            """, (term, term, term))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_price_history(product_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    a.id,
                    a.action,
                    a.old_value,
                    a.new_value,
                    a.changed_at,
                    DATE_FORMAT(a.changed_at, '%b %d, %Y %h:%i %p')    AS changed_at_fmt,
                    TRIM(u.full_name)                                   AS changed_by
                FROM audit_logs a
                INNER JOIN users u ON u.id = a.user_id
                WHERE a.table_name = 'lpg_products'
                  AND a.record_id  = %s
                  AND a.action     IN (
                      SELECT DISTINCT action
                      FROM audit_logs
                      WHERE table_name = 'lpg_products'
                        AND action = 'UPDATE'
                  )
                ORDER BY a.changed_at DESC
                LIMIT 20
            """, (product_id,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_revenue_summary():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                AS display_name,
                    COALESCE(SUM(di.quantity * di.price_at_delivery), 0)
                                                                AS product_revenue,
                    ROUND(
                        COALESCE(SUM(di.quantity * di.price_at_delivery), 0)
                        / NULLIF(
                            SUM(SUM(di.quantity * di.price_at_delivery))
                            OVER (), 0
                        ) * 100, 2
                    )                                           AS revenue_percentage,
                    RANK() OVER (
                        ORDER BY
                        COALESCE(SUM(di.quantity * di.price_at_delivery), 0) DESC
                    )                                           AS revenue_rank,
                    COALESCE(SUM(di.quantity), 0)               AS total_qty_sold
                FROM lpg_products p
                LEFT JOIN delivery_items di ON di.product_id = p.id
                GROUP BY p.id, p.name, p.cylinder_size
                ORDER BY revenue_rank ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def exists(name, cylinder_size, exclude_id=None):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            if exclude_id:
                cursor.execute("""
                    SELECT id FROM lpg_products
                    WHERE REGEXP_REPLACE(LOWER(TRIM(name)), '[^a-z0-9 ]', '')
                        = REGEXP_REPLACE(LOWER(TRIM(%s)), '[^a-z0-9 ]', '')
                      AND LOWER(TRIM(cylinder_size)) = LOWER(TRIM(%s))
                      AND id != %s
                    LIMIT 1
                """, (name, cylinder_size, exclude_id))
            else:
                cursor.execute("""
                    SELECT id FROM lpg_products
                    WHERE REGEXP_REPLACE(LOWER(TRIM(name)), '[^a-z0-9 ]', '')
                        = REGEXP_REPLACE(LOWER(TRIM(%s)), '[^a-z0-9 ]', '')
                      AND LOWER(TRIM(cylinder_size)) = LOWER(TRIM(%s))
                    LIMIT 1
                """, (name, cylinder_size))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def add(name, cylinder_size, refill_price, new_tank_price, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc(
                "sp_add_product",
                [name, cylinder_size, float(refill_price), float(new_tank_price)]
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
                raise ValueError(msg.split(":")[-1].strip())
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def update(product_id, name, cylinder_size, refill_price, new_tank_price, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = %s", (user_id,))
            cursor.callproc(
                "sp_update_product",
                [product_id, name, cylinder_size, float(refill_price), float(new_tank_price)]
            )
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

    
    @staticmethod
    def delete(product_id, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SET @current_user_id = %s", (user_id,))

            cursor.execute("""
                SELECT COUNT(*) AS linked_count
                FROM delivery_items
                WHERE product_id = %s
            """, (product_id,))

            row = cursor.fetchone()
            if row and row["linked_count"] > 0:
                raise ValueError(
                    "This product cannot be deleted because it is already linked "
                    "to existing delivery or transaction records."
                )

            cursor.execute(
                "DELETE FROM lpg_products WHERE id = %s",
                (product_id,)
            )

            conn.commit()
            return True

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    @staticmethod
    def get_count():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS total FROM lpg_products")
            row = cursor.fetchone()
            return row["total"] if row else 0
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
