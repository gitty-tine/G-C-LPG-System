CREATE OR REPLACE VIEW vw_delivery_items_details AS
SELECT
    di.id                                                        AS item_id,
    di.delivery_id,
    di.product_id,
    TRIM(p.name)                                                 AS product_base_name,
    COALESCE(TRIM(p.cylinder_size), '')                          AS cylinder_size,
    TRIM(
        CONCAT(
            TRIM(p.name),
            CASE
                WHEN COALESCE(TRIM(p.cylinder_size), '') = '' THEN ''
                ELSE CONCAT(' ', TRIM(p.cylinder_size))
            END
        )
    )                                                            AS product_name,
    di.quantity,
    di.type,
    di.price_at_delivery,
    ROUND(di.quantity * di.price_at_delivery, 2)                  AS subtotal
FROM delivery_items di
INNER JOIN lpg_products p ON p.id = di.product_id;

DROP TRIGGER IF EXISTS before_delivery_insert;
DROP TRIGGER IF EXISTS before_delivery_update;
DROP TRIGGER IF EXISTS before_delivery_item_insert;
DROP TRIGGER IF EXISTS before_delivery_item_update;
DROP TRIGGER IF EXISTS before_delivery_item_delete;

DELIMITER //

CREATE TRIGGER before_delivery_insert
BEFORE INSERT ON deliveries
FOR EACH ROW
BEGIN
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NEW.customer_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM customers WHERE id = NEW.customer_id)
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer.';
    END IF;

    IF NEW.user_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM users WHERE id = NEW.user_id AND role = 'admin')
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only administrators can create deliveries.';
    END IF;

    IF NEW.schedule_date IS NULL OR NEW.schedule_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    IF NEW.status IS NULL THEN
        SET NEW.status = 'pending';
    END IF;

    IF NEW.status <> 'pending' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New deliveries must start as pending.';
    END IF;
END//

CREATE TRIGGER before_delivery_update
BEFORE UPDATE ON deliveries
FOR EACH ROW
BEGIN
    DECLARE v_paid_transaction_count INT DEFAULT 0;

    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery ID cannot be changed.';
    END IF;

    IF NEW.customer_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM customers WHERE id = NEW.customer_id)
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer.';
    END IF;

    IF NEW.user_id IS NULL
       OR NOT EXISTS (SELECT 1 FROM users WHERE id = NEW.user_id AND role = 'admin')
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery user.';
    END IF;

    IF NOT (OLD.schedule_date <=> NEW.schedule_date)
       AND (NEW.schedule_date IS NULL OR NEW.schedule_date < CURDATE())
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    IF NEW.status NOT IN ('pending', 'in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status.';
    END IF;

    IF OLD.status <> NEW.status THEN
        IF OLD.status = 'pending'
           AND NEW.status NOT IN ('in_transit', 'delivered', 'cancelled')
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Pending deliveries can only move to in transit, delivered, or cancelled.';
        END IF;

        IF OLD.status = 'in_transit'
           AND NEW.status NOT IN ('delivered', 'cancelled')
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'In-transit deliveries can only move to delivered or cancelled.';
        END IF;

        IF OLD.status = 'cancelled' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cancelled deliveries cannot be changed.';
        END IF;

        IF OLD.status = 'delivered'
           AND NEW.status <> 'cancelled'
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Delivered deliveries can only be cancelled when unpaid.';
        END IF;

        IF NEW.status = 'delivered'
           AND NOT EXISTS (SELECT 1 FROM delivery_items WHERE delivery_id = OLD.id)
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A delivery must have at least one item before it can be delivered.';
        END IF;

        IF NEW.status = 'delivered'
           AND EXISTS (SELECT 1 FROM transactions WHERE delivery_id = OLD.id)
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'This delivery already has a transaction record.';
        END IF;

        IF NEW.status <> 'delivered' THEN
            SELECT COUNT(*)
            INTO v_paid_transaction_count
            FROM transactions
            WHERE delivery_id = OLD.id
              AND payment_status = 'paid';

            IF v_paid_transaction_count > 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Paid deliveries cannot be cancelled.';
            END IF;
        END IF;
    END IF;
END//

CREATE TRIGGER before_delivery_item_insert
BEFORE INSERT ON delivery_items
FOR EACH ROW
BEGIN
    IF NEW.delivery_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM deliveries
           WHERE id = NEW.delivery_id
             AND status = 'pending'
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be added to pending deliveries.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END//

CREATE TRIGGER before_delivery_item_update
BEFORE UPDATE ON delivery_items
FOR EACH ROW
BEGIN
    IF NOT (OLD.delivery_id <=> NEW.delivery_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item cannot be moved to another delivery.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM deliveries
        WHERE id = OLD.delivery_id
          AND status = 'pending'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be edited while the delivery is pending.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END//

CREATE TRIGGER before_delivery_item_delete
BEFORE DELETE ON delivery_items
FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM deliveries
        WHERE id = OLD.delivery_id
          AND status = 'pending'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery items can only be deleted while the delivery is pending.';
    END IF;
END//

DELIMITER ;
