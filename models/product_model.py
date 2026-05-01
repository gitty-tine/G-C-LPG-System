from decimal import Decimal

from database.connection import get_connection


class ProductModel:
    @staticmethod
    def _price(value):
        return Decimal(str(value))

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
                    TRIM(p.name)                                        AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                 AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                        AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                         AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                         AS new_tank_price_fmt,
                    p.is_active,
                    COALESCE(SUM(di.quantity), 0)                       AS total_sold,
                    COUNT(DISTINCT di.delivery_id)                      AS total_deliveries,
                    COUNT(di.id)                                        AS times_ordered
                FROM lpg_products p
                LEFT JOIN delivery_items di ON di.product_id = p.id
                WHERE p.is_active = 1
                GROUP BY
                    p.id, p.name, p.cylinder_size,
                    p.refill_price, p.new_tank_price,
                    p.is_active
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
                    TRIM(p.name)                                        AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                 AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                        AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                         AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                         AS new_tank_price_fmt,
                    p.is_active,
                    (
                        SELECT MAX(d.schedule_date)
                        FROM deliveries d
                        INNER JOIN delivery_items di ON di.delivery_id = d.id
                        WHERE di.product_id = p.id
                    )                                                   AS last_ordered
                FROM lpg_products p
                WHERE p.id = %s
                  AND p.is_active = 1
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
                    TRIM(p.name)                                        AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                 AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                        AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    FORMAT(p.refill_price,   2)                         AS refill_price_fmt,
                    FORMAT(p.new_tank_price, 2)                         AS new_tank_price_fmt,
                    p.is_active,
                    COALESCE(SUM(di.quantity), 0)                       AS total_sold,
                    COUNT(DISTINCT di.delivery_id)                      AS total_deliveries,
                    COUNT(di.id)                                        AS times_ordered
                FROM lpg_products p
                LEFT JOIN delivery_items di ON di.product_id = p.id
                WHERE
                    p.is_active = 1
                    AND (
                        LOWER(TRIM(p.name))          LIKE %s OR
                        LOWER(TRIM(p.cylinder_size)) LIKE %s OR
                        LOWER(CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))) LIKE %s
                    )
                GROUP BY
                    p.id, p.name, p.cylinder_size,
                    p.refill_price, p.new_tank_price,
                    p.is_active
                ORDER BY p.name ASC
            """, (term, term, term))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_summary():
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
                    p.refill_price,
                    p.new_tank_price,
                    COUNT(di.id)                                AS total_items_ordered,
                    COALESCE(SUM(di.quantity), 0)               AS total_quantity_sold,
                    COALESCE(SUM(di.quantity * di.price_at_delivery), 0)
                                                                AS total_revenue,
                    COALESCE(AVG(di.price_at_delivery), 0)      AS avg_price_sold,
                    RANK() OVER (
                        ORDER BY COALESCE(SUM(di.quantity * di.price_at_delivery), 0) DESC
                    )                                           AS revenue_rank
                FROM lpg_products p
                LEFT JOIN delivery_items di ON di.product_id = p.id
                GROUP BY
                    p.id, p.name, p.cylinder_size,
                    p.refill_price, p.new_tank_price
                ORDER BY revenue_rank ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_by_delivery(delivery_id):
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
                    di.quantity,
                    di.type,
                    di.price_at_delivery,
                    FORMAT(di.price_at_delivery, 2)         AS price_fmt,
                    ROUND(di.quantity * di.price_at_delivery, 2)
                                                            AS subtotal,
                    FORMAT(di.quantity * di.price_at_delivery, 2)
                                                            AS subtotal_fmt
                FROM delivery_items di
                INNER JOIN lpg_products p ON p.id = di.product_id
                WHERE di.delivery_id = %s
                ORDER BY p.name ASC
            """, (delivery_id,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_dropdown_list():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id,
                    TRIM(p.name)                                        AS name,
                    COALESCE(TRIM(p.cylinder_size), '')                 AS cylinder_size,
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))
                                                                        AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    p.is_active,
                    (
                        SELECT COALESCE(AVG(di.price_at_delivery), p.refill_price)
                        FROM delivery_items di
                        WHERE di.product_id = p.id
                          AND di.type = 'refill'
                    )                                                   AS avg_refill_price
                FROM lpg_products p
                WHERE p.is_active = 1
                ORDER BY p.name ASC
            """)
            return cursor.fetchall()
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
            cursor.execute("SELECT COUNT(*) AS total FROM lpg_products WHERE is_active = 1")
            row = cursor.fetchone()
            return row["total"] if row else 0
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
                    WHERE is_active = 1
                      AND TRIM(
                          REGEXP_REPLACE(
                              REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                              '\\s+',
                              ' '
                          )
                      ) = TRIM(
                          REGEXP_REPLACE(
                              REGEXP_REPLACE(LOWER(TRIM(%s)), '[^a-z0-9 ]', ''),
                              '\\s+',
                              ' '
                          )
                      )
                      AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = LOWER(TRIM(%s))
                      AND id != %s
                    LIMIT 1
                """, (name, cylinder_size, exclude_id))
            else:
                cursor.execute("""
                    SELECT id FROM lpg_products
                    WHERE is_active = 1
                      AND TRIM(
                          REGEXP_REPLACE(
                              REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                              '\\s+',
                              ' '
                          )
                      ) = TRIM(
                          REGEXP_REPLACE(
                              REGEXP_REPLACE(LOWER(TRIM(%s)), '[^a-z0-9 ]', ''),
                              '\\s+',
                              ' '
                          )
                      )
                      AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = LOWER(TRIM(%s))
                    LIMIT 1
                """, (name, cylinder_size))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def add(name, cylinder_size, refill_price, new_tank_price):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()

            cursor.execute("SET @current_user_id = 0")
            cursor.callproc(
                "sp_add_product",
                [
                    name,
                    cylinder_size,
                    ProductModel._price(refill_price),
                    ProductModel._price(new_tank_price),
                ],
            )
            new_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    new_id = row[0]
            conn.commit()
            return new_id

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def update(product_id, name, cylinder_size, refill_price, new_tank_price):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()

            cursor.execute("SET @current_user_id = 0")
            cursor.callproc(
                "sp_update_product",
                [
                    product_id,
                    name,
                    cylinder_size,
                    ProductModel._price(refill_price),
                    ProductModel._price(new_tank_price),
                ],
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
    def delete(product_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SET @current_user_id = 0")
            cursor.callproc("sp_delete_product", [product_id])
            conn.commit()
            return True

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
