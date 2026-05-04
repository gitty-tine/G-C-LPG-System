import datetime
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from mysql.connector import Error

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
    def _coerce_date(value):
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            return datetime.date.fromisoformat(str(value))
        except Exception:
            raise ValueError("Invalid schedule date.")

    @staticmethod
    def _normalize_notes(value):
        value = str(value or "").strip()
        return value or None

    @staticmethod
    def _money(value):
        try:
            return Decimal(str(value if value is not None else "0")).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return Decimal("0.00")

    @staticmethod
    def _format_money(value):
        return f"{DeliveryModel._money(value):,.2f}"

    @staticmethod
    def _format_date(value):
        if isinstance(value, datetime.datetime):
            value = value.date()
        if isinstance(value, datetime.date):
            return value.isoformat()
        return str(value or "-")

    @staticmethod
    def _display_item_type(value):
        return str(value or "").replace("_", " ").title()

    @staticmethod
    def _normalize_items(items):
        normalized = []
        for item in items or []:
            try:
                raw_item_id = item.get("item_id")
                item_id = None if raw_item_id in (None, "", 0, "0") else int(raw_item_id)
                product_id = int(item.get("product_id"))
                quantity = int(item.get("quantity"))
            except Exception:
                raise ValueError("Delivery item product and quantity are required.")

            if item_id is not None and item_id <= 0:
                raise ValueError("Invalid delivery item record.")
            item_type = str(item.get("type") or "").strip().lower().replace(" ", "_")
            if item_type not in ("refill", "new_tank"):
                raise ValueError("Delivery item type must be Refill or New Tank.")
            if quantity <= 0:
                raise ValueError("Quantity must be at least 1.")

            normalized.append({
                "item_id": item_id,
                "product_id": product_id,
                "quantity": quantity,
                "type": item_type,
            })

        if not normalized:
            raise ValueError("Please add at least one product.")
        return normalized

    @staticmethod
    def _item_signature(item):
        return (
            int(item.get("product_id") or 0),
            int(item.get("quantity") or 0),
            str(item.get("type") or "").strip().lower(),
        )

    @staticmethod
    def _attach_exact_existing_item_ids(normalized_items, existing_items):
        used_ids = {
            int(item["item_id"])
            for item in normalized_items
            if item.get("item_id") is not None
        }
        by_signature = defaultdict(list)
        for item in existing_items:
            by_signature[DeliveryModel._item_signature(item)].append(int(item["item_id"]))

        for item in normalized_items:
            if item.get("item_id") is not None:
                continue
            bucket = by_signature.get(DeliveryModel._item_signature(item), [])
            while bucket and bucket[0] in used_ids:
                bucket.pop(0)
            if bucket:
                item["item_id"] = bucket.pop(0)
                used_ids.add(item["item_id"])

    @staticmethod
    def _fetch_delivery_items(cursor, delivery_id, lock=False):
        lock_clause = " FOR UPDATE" if lock else ""
        cursor.execute(f"""
            SELECT
                di.id AS item_id,
                di.product_id,
                di.quantity,
                di.type,
                di.price_at_delivery,
                TRIM(
                    CONCAT(
                        TRIM(p.name),
                        CASE
                            WHEN COALESCE(TRIM(p.cylinder_size), '') = '' THEN ''
                            ELSE CONCAT(' ', TRIM(p.cylinder_size))
                        END
                    )
                ) AS product_name
            FROM delivery_items di
            INNER JOIN lpg_products p ON p.id = di.product_id
            WHERE di.delivery_id = %s
            ORDER BY di.id ASC
            {lock_clause}
        """, (delivery_id,))
        return cursor.fetchall()

    @staticmethod
    def _items_total(items):
        total = Decimal("0.00")
        for item in items:
            total += Decimal(int(item.get("quantity") or 0)) * DeliveryModel._money(item.get("price_at_delivery"))
        return total.quantize(Decimal("0.01"))

    @staticmethod
    def _catalog_price(product, item_type):
        price = product.get("refill_price") if item_type == "refill" else product.get("new_tank_price")
        price = DeliveryModel._money(price)
        if price <= 0:
            raise ValueError("Selected product price is invalid. Please update the product catalog.")
        return price

    @staticmethod
    def _items_changed(normalized_items, existing_items):
        existing_by_id = {int(item["item_id"]): item for item in existing_items}
        incoming_ids = []
        for item in normalized_items:
            if item.get("item_id") is not None:
                item_id = int(item["item_id"])
                if item_id in incoming_ids:
                    raise ValueError("Duplicate delivery item row detected. Please refresh and try again.")
                if item_id not in existing_by_id:
                    raise ValueError("One or more delivery items no longer belong to this delivery. Please refresh and try again.")
                incoming_ids.append(item_id)

        if len(existing_items) != len(normalized_items):
            return True
        if set(existing_by_id.keys()) != set(incoming_ids):
            return True

        for item in normalized_items:
            existing = existing_by_id[int(item["item_id"])]
            if (
                int(existing.get("product_id") or 0) != item["product_id"]
                or int(existing.get("quantity") or 0) != item["quantity"]
                or str(existing.get("type") or "").lower() != item["type"]
            ):
                return True
        return False

    @staticmethod
    def _active_product_ids_required(normalized_items, existing_items):
        existing_by_id = {int(item["item_id"]): item for item in existing_items}
        required = set()
        for item in normalized_items:
            existing = existing_by_id.get(item.get("item_id"))
            if existing is None:
                required.add(item["product_id"])
                continue
            if (
                int(existing.get("product_id") or 0) != item["product_id"]
                or int(existing.get("quantity") or 0) != item["quantity"]
                or str(existing.get("type") or "").lower() != item["type"]
            ):
                required.add(item["product_id"])
        return sorted(required)

    @staticmethod
    def _format_items_for_audit(items):
        if not items:
            return "-"
        parts = []
        for item in items:
            name = item.get("product_name") or f"Product #{item.get('product_id')}"
            quantity = int(item.get("quantity") or 0)
            item_type = DeliveryModel._display_item_type(item.get("type"))
            price = DeliveryModel._format_money(item.get("price_at_delivery"))
            parts.append(f"{name} x{quantity} ({item_type}) @ Php {price}")
        return "; ".join(parts)

    @staticmethod
    def _insert_delivery_edit_audit(
        cursor,
        delivery,
        old_items,
        new_schedule_date,
        new_notes,
        new_items,
        user_id,
        header_changed,
        items_changed,
    ):
        old_parts = []
        new_parts = []

        old_schedule_date = DeliveryModel._coerce_date(delivery.get("schedule_date"))
        old_notes = DeliveryModel._normalize_notes(delivery.get("notes"))

        if old_schedule_date != new_schedule_date:
            old_parts.append(f"Schedule Date: {DeliveryModel._format_date(old_schedule_date)}")
            new_parts.append(f"Schedule Date: {DeliveryModel._format_date(new_schedule_date)}")

        if old_notes != new_notes:
            old_parts.append(f"Notes: {old_notes or '-'}")
            new_parts.append(f"Notes: {new_notes or '-'}")

        if items_changed:
            old_total = DeliveryModel._items_total(old_items)
            new_total = DeliveryModel._items_total(new_items)
            old_parts.append(f"Items: {DeliveryModel._format_items_for_audit(old_items)}")
            new_parts.append(f"Items: {DeliveryModel._format_items_for_audit(new_items)}")
            if old_total != new_total:
                old_parts.append(f"Total Amount: Php {DeliveryModel._format_money(old_total)}")
                new_parts.append(f"Total Amount: Php {DeliveryModel._format_money(new_total)}")

        if not header_changed and not items_changed:
            return

        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
            VALUES (%s, 'UPDATE', 'deliveries', %s, %s, %s)
        """, (
            user_id or delivery.get("user_id") or 1,
            delivery.get("id"),
            ", ".join(old_parts) if old_parts else "-",
            ", ".join(new_parts) if new_parts else "-",
        ))

    @staticmethod
    def _call_update_pending_delivery(cursor, delivery_id, user_id, schedule_date, notes):
        try:
            cursor.callproc("sp_update_pending_delivery", [
                delivery_id,
                user_id,
                schedule_date,
                DeliveryModel._normalize_notes(notes),
            ])
            for result in cursor.stored_results():
                result.fetchall()
        except Error as exc:
            if getattr(exc, "errno", None) != 1305:
                raise
            cursor.execute("""
                UPDATE deliveries
                SET
                    schedule_date = %s,
                    notes = NULLIF(TRIM(COALESCE(%s, '')), '')
                WHERE id = %s
                  AND status = 'pending'
            """, (schedule_date, notes or "", delivery_id))

    @staticmethod
    def update(delivery_id, user_id, schedule_date, notes, items):
        conn   = None
        cursor = None
        try:
            delivery_id = int(delivery_id)
            user_id = int(user_id or 0)
            schedule_date = DeliveryModel._coerce_date(schedule_date)
            notes = DeliveryModel._normalize_notes(notes)
            normalized_items = DeliveryModel._normalize_items(items)

            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)

            conn.start_transaction()
            cursor.execute("SET @current_user_id = %s", (user_id or 0,))

            cursor.execute("SELECT CURDATE() AS today")
            today_row = cursor.fetchone() or {}
            today = today_row.get("today")
            if isinstance(today, datetime.datetime):
                today = today.date()
            if today and schedule_date < today:
                raise ValueError("Schedule date cannot be in the past.")

            cursor.execute("""
                SELECT
                    d.id,
                    d.status,
                    d.schedule_date,
                    d.notes,
                    d.user_id,
                    TRIM(c.full_name) AS customer_name
                FROM deliveries d
                INNER JOIN customers c ON c.id = d.customer_id
                WHERE d.id = %s
                FOR UPDATE
            """, (delivery_id,))
            delivery = cursor.fetchone()
            if delivery is None:
                raise ValueError("Delivery not found.")
            if str(delivery.get("status") or "").lower() != "pending":
                raise ValueError("Only pending deliveries can be edited.")

            cursor.execute("""
                SELECT id
                FROM users
                WHERE id = %s
                  AND role = 'admin'
                LIMIT 1
            """, (user_id,))
            if cursor.fetchone() is None:
                raise ValueError("Only administrators can edit deliveries.")

            existing_items = DeliveryModel._fetch_delivery_items(cursor, delivery_id, lock=True)
            DeliveryModel._attach_exact_existing_item_ids(normalized_items, existing_items)
            items_changed = DeliveryModel._items_changed(normalized_items, existing_items)

            active_product_ids = (
                DeliveryModel._active_product_ids_required(normalized_items, existing_items)
                if items_changed
                else []
            )
            products = {}
            if active_product_ids:
                placeholders = ", ".join(["%s"] * len(active_product_ids))
                cursor.execute(f"""
                    SELECT id, refill_price, new_tank_price
                    FROM lpg_products
                    WHERE is_active = 1
                      AND id IN ({placeholders})
                """, tuple(active_product_ids))
                products = {row["id"]: row for row in cursor.fetchall()}
                if any(product_id not in products for product_id in active_product_ids):
                    raise ValueError("One or more changed products are no longer active. Please refresh the product list.")

            old_schedule_date = DeliveryModel._coerce_date(delivery.get("schedule_date"))
            old_notes = DeliveryModel._normalize_notes(delivery.get("notes"))
            header_changed = old_schedule_date != schedule_date or old_notes != notes

            if header_changed:
                DeliveryModel._call_update_pending_delivery(
                    cursor,
                    delivery_id,
                    user_id,
                    schedule_date,
                    notes,
                )

            if items_changed:
                existing_by_id = {int(item["item_id"]): item for item in existing_items}
                incoming_existing_ids = {
                    int(item["item_id"])
                    for item in normalized_items
                    if item.get("item_id") is not None
                }

                for item_id in sorted(set(existing_by_id.keys()) - incoming_existing_ids):
                    cursor.execute(
                        "DELETE FROM delivery_items WHERE id = %s AND delivery_id = %s",
                        (item_id, delivery_id),
                    )

                for item in normalized_items:
                    existing = existing_by_id.get(item.get("item_id"))

                    if existing is None:
                        product = products[item["product_id"]]
                        price = DeliveryModel._catalog_price(product, item["type"])
                        cursor.execute("""
                            INSERT INTO delivery_items
                                (delivery_id, product_id, quantity, type, price_at_delivery)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            delivery_id,
                            item["product_id"],
                            item["quantity"],
                            item["type"],
                            price,
                        ))
                        continue

                    same_price_basis = (
                        int(existing.get("product_id") or 0) == item["product_id"]
                        and str(existing.get("type") or "").lower() == item["type"]
                    )
                    if same_price_basis:
                        if int(existing.get("quantity") or 0) != item["quantity"]:
                            cursor.execute("""
                                UPDATE delivery_items
                                SET quantity = %s
                                WHERE id = %s
                                  AND delivery_id = %s
                            """, (item["quantity"], item["item_id"], delivery_id))
                    else:
                        product = products[item["product_id"]]
                        price = DeliveryModel._catalog_price(product, item["type"])
                        cursor.execute("""
                            UPDATE delivery_items
                            SET
                                product_id = %s,
                                quantity = %s,
                                type = %s,
                                price_at_delivery = %s
                            WHERE id = %s
                              AND delivery_id = %s
                        """, (
                            item["product_id"],
                            item["quantity"],
                            item["type"],
                            price,
                            item["item_id"],
                            delivery_id,
                        ))

            final_items = (
                DeliveryModel._fetch_delivery_items(cursor, delivery_id, lock=False)
                if items_changed
                else existing_items
            )
            old_total = DeliveryModel._items_total(existing_items)
            final_total = DeliveryModel._items_total(final_items)

            if items_changed and old_total != final_total:
                cursor.execute("""
                    SELECT id, total_amount, payment_status
                    FROM transactions
                    WHERE delivery_id = %s
                    FOR UPDATE
                """, (delivery_id,))
                transaction = cursor.fetchone()
                if transaction and str(transaction.get("payment_status") or "").lower() == "unpaid":
                    transaction_total = DeliveryModel._money(transaction.get("total_amount"))
                    if transaction_total != final_total:
                        cursor.execute("""
                            UPDATE transactions
                            SET total_amount = %s
                            WHERE id = %s
                              AND payment_status = 'unpaid'
                        """, (final_total, transaction.get("id")))

            DeliveryModel._insert_delivery_edit_audit(
                cursor,
                delivery,
                existing_items,
                schedule_date,
                notes,
                final_items,
                user_id,
                header_changed,
                items_changed,
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
