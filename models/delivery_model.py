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
    def get_today():
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
                    vd.status,
                    vd.notes,
                    COALESCE(SUM(di.quantity * di.price_at_delivery), 0)    AS total_amount,
                    COALESCE(COUNT(di.id), 0)                               AS item_count,
                    COALESCE(MAX(t.payment_status), 'unpaid')               AS payment_status
                FROM vw_delivery_details vd
                LEFT JOIN delivery_items di ON di.delivery_id = vd.delivery_id
                LEFT JOIN transactions t    ON t.delivery_id  = vd.delivery_id
                WHERE DATE(vd.schedule_date) = CURDATE()
                GROUP BY
                    vd.delivery_id,
                    vd.customer_id,
                    vd.customer_name,
                    vd.customer_contact,
                    vd.customer_address,
                    vd.schedule_date,
                    vd.status,
                    vd.notes,
                    vd.created_at
                ORDER BY vd.created_at DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_by_id(delivery_id):
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
                    DATE_FORMAT(vd.updated_at, '%b %d, %Y %h:%i %p')      AS updated_at_fmt,
                    (
                        SELECT COALESCE(t.total_amount, 0)
                        FROM transactions t
                        WHERE t.delivery_id = vd.delivery_id
                        LIMIT 1
                    )                                                       AS total_amount,
                    (
                        SELECT COALESCE(t.payment_status, 'unpaid')
                        FROM transactions t
                        WHERE t.delivery_id = vd.delivery_id
                        LIMIT 1
                    )                                                       AS payment_status,
                    (
                        SELECT COUNT(*)
                        FROM delivery_items di
                        WHERE di.delivery_id = vd.delivery_id
                    )                                                       AS item_count
                FROM vw_delivery_details vd
                WHERE vd.delivery_id = %s
            """, (delivery_id,))
            return cursor.fetchone()
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
                    NULL                                                    AS product_id,
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
    def get_summary_counts():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    total_today,
                    delivered_today,
                    pending_today,
                    in_transit_today,
                    cancelled_today,
                    COALESCE(sales_today, 0) AS sales_today
                FROM vw_dashboard_today
            """)
            return cursor.fetchone()
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
                    vd.delivery_id                                          AS id,
                    vd.customer_name,
                    vd.customer_contact                                     AS contact,
                    vd.schedule_date,
                    DATE_FORMAT(vd.schedule_date, '%b %d, %Y')             AS schedule_date_fmt,
                    vd.status,
                    COALESCE(t.total_amount, 0)                             AS total_amount
                FROM vw_delivery_details vd
                LEFT JOIN transactions t ON t.delivery_id = vd.delivery_id
                WHERE vd.status = 'pending'

                UNION ALL

                SELECT
                    vd2.delivery_id                                         AS id,
                    vd2.customer_name,
                    vd2.customer_contact                                    AS contact,
                    vd2.schedule_date,
                    DATE_FORMAT(vd2.schedule_date, '%b %d, %Y')            AS schedule_date_fmt,
                    vd2.status,
                    COALESCE(t2.total_amount, 0)                            AS total_amount
                FROM vw_delivery_details vd2
                LEFT JOIN transactions t2 ON t2.delivery_id = vd2.delivery_id
                WHERE vd2.status = 'in_transit'

                ORDER BY schedule_date ASC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_by_date_range(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                WITH delivery_base AS (
                    SELECT
                        vd.delivery_id                                      AS id,
                        vd.customer_name,
                        vd.customer_contact                                 AS contact,
                        vd.schedule_date,
                        CAST(vd.schedule_date AS CHAR)                     AS schedule_date_str,
                        vd.status,
                        vd.notes
                    FROM vw_delivery_details vd
                    WHERE vd.schedule_date BETWEEN %s AND %s
                ),
                delivery_totals AS (
                    SELECT
                        di.delivery_id,
                        SUM(di.quantity * di.price_at_delivery)             AS computed_total,
                        COUNT(di.id)                                        AS item_count
                    FROM delivery_items di
                    WHERE di.delivery_id IN (SELECT id FROM delivery_base)
                    GROUP BY di.delivery_id
                )
                SELECT
                    db.id,
                    db.customer_name,
                    db.contact,
                    db.schedule_date,
                    db.schedule_date_str,
                    db.status,
                    db.notes,
                    COALESCE(dt.computed_total, 0)                          AS total_amount,
                    COALESCE(dt.item_count, 0)                              AS item_count,
                    COALESCE(t.payment_status, 'unpaid')                   AS payment_status
                FROM delivery_base db
                LEFT JOIN delivery_totals dt ON dt.delivery_id = db.id
                LEFT JOIN transactions t     ON t.delivery_id  = db.id
                ORDER BY db.schedule_date DESC
            """, (date_from, date_to))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_latest_per_customer():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    id,
                    customer_id,
                    customer_name,
                    contact,
                    schedule_date,
                    DATE_FORMAT(schedule_date, '%b %d, %Y')                AS schedule_date_fmt,
                    status,
                    total_amount
                FROM (
                    SELECT
                        vd.delivery_id                                      AS id,
                        vd.customer_id,
                        vd.customer_name,
                        vd.customer_contact                                 AS contact,
                        vd.schedule_date,
                        vd.status,
                        COALESCE(t.total_amount, 0)                         AS total_amount,
                        ROW_NUMBER() OVER (
                            PARTITION BY vd.customer_id
                            ORDER BY vd.schedule_date DESC, vd.delivery_id DESC
                        )                                                   AS rn
                    FROM vw_delivery_details vd
                    LEFT JOIN transactions t ON t.delivery_id = vd.delivery_id
                ) ranked
                WHERE rn = 1
                ORDER BY schedule_date DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_dates_with_deliveries(year, month):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    DATE_FORMAT(d.schedule_date, '%Y-%m-%d')               AS delivery_date,
                    COUNT(d.id)                                             AS delivery_count,
                    SUM(CASE WHEN d.status = 'delivered'  THEN 1 ELSE 0 END) AS delivered_count,
                    SUM(CASE WHEN d.status = 'pending'    THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN d.status = 'in_transit' THEN 1 ELSE 0 END) AS in_transit_count,
                    SUM(CASE WHEN d.status = 'cancelled'  THEN 1 ELSE 0 END) AS cancelled_count
                FROM deliveries d
                WHERE YEAR(d.schedule_date)  = %s
                  AND MONTH(d.schedule_date) = %s
                GROUP BY DATE_FORMAT(d.schedule_date, '%Y-%m-%d')
                ORDER BY delivery_date ASC
            """, (year, month))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_schedule_grid(date_from, date_to):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    cal.cal_date,
                    DATE_FORMAT(cal.cal_date, '%b %d')                     AS cal_date_fmt,
                    COALESCE(d_count.delivery_count, 0)                    AS delivery_count,
                    COALESCE(d_count.pending_count, 0)                     AS pending_count,
                    COALESCE(d_count.delivered_count, 0)                   AS delivered_count
                FROM (
                    SELECT DATE_ADD(%s, INTERVAL seq.n DAY) AS cal_date
                    FROM (
                        SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
                        UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
                        UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
                        UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11
                        UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14
                        UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17
                        UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20
                        UNION ALL SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23
                        UNION ALL SELECT 24 UNION ALL SELECT 25 UNION ALL SELECT 26
                        UNION ALL SELECT 27 UNION ALL SELECT 28 UNION ALL SELECT 29
                        UNION ALL SELECT 30
                    ) seq
                    WHERE DATE_ADD(%s, INTERVAL seq.n DAY) <= %s
                ) cal
                CROSS JOIN (
                    SELECT
                        schedule_date,
                        COUNT(*)                                            AS delivery_count,
                        SUM(CASE WHEN status='pending'   THEN 1 ELSE 0 END) AS pending_count,
                        SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) AS delivered_count
                    FROM deliveries
                    WHERE schedule_date BETWEEN %s AND %s
                    GROUP BY schedule_date
                ) d_count
                ON cal.cal_date = d_count.schedule_date
                ORDER BY cal.cal_date ASC
            """, (date_from, date_from, date_to, date_from, date_to))
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
                    p.new_tank_price
                FROM (SELECT 1) dummy
                RIGHT JOIN lpg_products p ON 1 = 1
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

    
    @staticmethod
    def get_logs(delivery_id):
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    dl.id,
                    dl.old_status,
                    dl.new_status,
                    DATE_FORMAT(dl.changed_at, '%b %d, %Y %h:%i %p')      AS changed_at_fmt,
                    TRIM(u.full_name)                                       AS changed_by,
                    u.role                                                  AS changed_by_role
                FROM delivery_logs dl
                INNER JOIN users u ON u.id = dl.user_id
                WHERE dl.delivery_id = %s
                  AND dl.new_status IN (
                      SELECT DISTINCT status
                      FROM deliveries
                  )
                ORDER BY dl.changed_at ASC
            """, (delivery_id,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    
    @staticmethod
    def get_overdue():
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    vd.delivery_id                                          AS id,
                    vd.customer_name,
                    vd.customer_contact                                     AS contact,
                    vd.schedule_date,
                    DATE_FORMAT(vd.schedule_date, '%b %d, %Y')             AS schedule_date_fmt,
                    vd.status,
                    DATEDIFF(CURDATE(), vd.schedule_date)                  AS days_overdue,
                    (
                        SELECT MIN(d2.schedule_date)
                        FROM deliveries d2
                        WHERE d2.customer_id = vd.customer_id
                          AND d2.status NOT IN ('delivered', 'cancelled')
                          AND d2.schedule_date < CURDATE()
                    )                                                       AS earliest_overdue
                FROM vw_delivery_details vd
                WHERE vd.schedule_date < CURDATE()
                  AND vd.status NOT IN ('delivered', 'cancelled')
                ORDER BY days_overdue DESC
            """)
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
