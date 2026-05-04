-- Add a narrow pending-delivery edit routine without changing schemas.

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_update_pending_delivery $$
CREATE PROCEDURE sp_update_pending_delivery(
    IN p_delivery_id INT,
    IN p_user_id INT,
    IN p_schedule_date DATE,
    IN p_notes TEXT
)
BEGIN
    DECLARE v_delivery_count INT DEFAULT 0;
    DECLARE v_status VARCHAR(20);

    SET @current_user_id = NULLIF(p_user_id, 0);

    IF p_user_id IS NULL OR NOT EXISTS (
        SELECT 1
        FROM users
        WHERE id = p_user_id
          AND role = 'admin'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only administrators can edit deliveries.';
    END IF;

    IF p_schedule_date IS NULL OR p_schedule_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    SELECT COUNT(*), MAX(status)
    INTO v_delivery_count, v_status
    FROM deliveries
    WHERE id = p_delivery_id;

    IF v_delivery_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery not found.';
    END IF;

    IF v_status <> 'pending' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only pending deliveries can be edited.';
    END IF;

    UPDATE deliveries
    SET
        schedule_date = p_schedule_date,
        notes = NULLIF(TRIM(COALESCE(p_notes, '')), '')
    WHERE id = p_delivery_id
      AND status = 'pending';
END $$

DROP TRIGGER IF EXISTS before_delivery_item_insert $$
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

    IF NEW.product_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE id = NEW.product_id
             AND is_active = 1
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Please select an active product.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END $$

DROP TRIGGER IF EXISTS before_delivery_item_update $$
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

    IF NEW.product_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE id = NEW.product_id
             AND is_active = 1
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Please select an active product.';
    END IF;

    IF NEW.quantity IS NULL OR NEW.quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be at least 1.';
    END IF;

    IF NEW.price_at_delivery IS NULL OR NEW.price_at_delivery <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery item price must be greater than zero.';
    END IF;
END $$

DROP TRIGGER IF EXISTS before_delivery_item_delete $$
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
END $$

DELIMITER ;
