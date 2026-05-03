from database.connection import get_connection


class DeliveryModel:
    @staticmethod
    def get_all():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    vd.delivery_id                                          AS id,
                    vd.customer_id,
                    vd.customer_name,
                    vd.customer_contact                                     AS contact,
                    vd.customer_address                                     AS address,
                    vd.schedule_date,
                    DATE_FORMAT(vd.schedule_date, '%b %d, %Y')             AS schedule_date_fmt,
                    vd.status,
                    vd.notes,
                    vd.encoded_by,
                    DATE_FORMAT(vd.created_at, '%b %d, %Y %h:%i %p')      AS created_at_fmt,
                    COALESCE(SUM(di.quantity * di.price_at_delivery), 0)    AS total_amount,
                    COALESCE(COUNT(di.id), 0)                               AS item_count,
                    COALESCE(
                        GROUP_CONCAT(
                            CONCAT(
                                TRIM(p.name),
                                CASE
                                    WHEN COALESCE(TRIM(p.cylinder_size), '') = '' THEN ''
                                    ELSE CONCAT(' ', TRIM(p.cylinder_size))
                                END,
                                ' x', di.quantity,
                                ' (', REPLACE(di.type, '_', ' '), ')'
                            )
                            ORDER BY p.name ASC
                            SEPARATOR ', '
                        ),
                        ''
                    )                                                       AS item_summary,
                    COALESCE(MAX(t.payment_status), 'unpaid')               AS payment_status,
                    DATEDIFF(CURDATE(), vd.schedule_date)                  AS days_since_scheduled,
                    CASE
                        WHEN vd.schedule_date  < CURDATE()
                         AND vd.status NOT IN ('delivered', 'cancelled')
                        THEN 'overdue'
                        WHEN vd.schedule_date = CURDATE()
                        THEN 'today'
                        WHEN vd.schedule_date > CURDATE()
                        THEN 'upcoming'
                        ELSE 'closed'
                    END                                                     AS urgency
                FROM vw_delivery_details vd
                LEFT JOIN delivery_items di ON di.delivery_id = vd.delivery_id
                LEFT JOIN lpg_products p    ON p.id           = di.product_id
                LEFT JOIN transactions t    ON t.delivery_id  = vd.delivery_id
                GROUP BY
                    vd.delivery_id,
                    vd.customer_id,
                    vd.customer_name,
                    vd.customer_contact,
                    vd.customer_address,
                    vd.schedule_date,
                    vd.status,
                    vd.notes,
                    vd.encoded_by,
                    vd.created_at
                ORDER BY vd.schedule_date DESC, vd.created_at DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
    @staticmethod
    def get_items(delivery_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    vid.item_id,
                    vid.delivery_id,
                    vid.product_id,
                    vid.product_name,
                    vid.quantity,
                    vid.type,
                    vid.price_at_delivery                                   AS unit_price,
                    FORMAT(vid.price_at_delivery, 2)                        AS unit_price_fmt,
                    vid.subtotal,
                    FORMAT(vid.subtotal, 2)                                 AS subtotal_fmt,
                    CONCAT(
                        vid.product_name, ' x', vid.quantity,
                        ' (', REPLACE(vid.type, '_', ' '), ')'
                    )                                                       AS item_summary
                FROM vw_delivery_items_details vid
                WHERE vid.delivery_id = %s
                ORDER BY vid.product_name ASC
            """, (delivery_id,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_customer_dropdown():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    c.id,
                    TRIM(c.full_name)                                       AS name,
                    c.contact_number                                        AS contact,
                    TRIM(c.address)                                         AS address,
                    (
                        SELECT MAX(d.schedule_date)
                        FROM deliveries d
                        WHERE d.customer_id = c.id
                    )                                                       AS last_order_date
                FROM customers c
                WHERE c.is_active = 1
                ORDER BY c.full_name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_product_dropdown():
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
                    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size,''))
                                                                            AS display_name,
                    p.refill_price,
                    p.new_tank_price,
                    p.is_active
                FROM lpg_products p
                WHERE p.is_active = 1
                ORDER BY p.name ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def create(customer_id, user_id, schedule_date, notes, items):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)

            conn.start_transaction()

            cursor.execute("""
                SELECT id
                FROM customers
                WHERE id = %s
                  AND is_active = 1
                LIMIT 1
            """, (customer_id,))
            if cursor.fetchone() is None:
                raise ValueError("Selected customer is archived or no longer exists. Please refresh the customer list.")

            product_ids = sorted({item["product_id"] for item in items})
            if not product_ids:
                raise ValueError("Please add at least one product.")
            placeholders = ", ".join(["%s"] * len(product_ids))
            cursor.execute(f"""
                SELECT id
                FROM lpg_products
                WHERE is_active = 1
                  AND id IN ({placeholders})
            """, tuple(product_ids))
            active_ids = {row["id"] for row in cursor.fetchall()}
            if any(product_id not in active_ids for product_id in product_ids):
                raise ValueError("One or more selected products are no longer active. Please refresh the product list.")

            cursor.callproc("sp_create_delivery", [
                customer_id,
                user_id,
                schedule_date,
                notes or None,
            ])

            
            new_delivery_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    new_delivery_id = row.get("new_delivery_id") or row.get(0)

            if not new_delivery_id:
                conn.rollback()
                raise ValueError("Failed to create delivery record.")

            for item in items:
                cursor.execute("""
                    INSERT INTO delivery_items
                        (delivery_id, product_id, quantity, type, price_at_delivery)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    new_delivery_id,
                    item["product_id"],
                    item["quantity"],
                    item["type"].lower().replace(" ", "_"),
                    float(item["unit_price"]),
                ))

            conn.commit()
            return new_delivery_id

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def update_status(delivery_id, new_status, user_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.callproc("sp_update_delivery_status", [
                delivery_id,
                new_status,
                user_id,
            ])

            conn.commit()
            return True

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
