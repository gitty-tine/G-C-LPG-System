-- Add customer archive support while preserving historical delivery links.

DELIMITER $$

DROP PROCEDURE IF EXISTS _add_customer_is_active_column $$
CREATE PROCEDURE _add_customer_is_active_column()
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'customers'
          AND COLUMN_NAME = 'is_active'
    ) THEN
        ALTER TABLE customers
            ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER notes;
    END IF;
END $$

CALL _add_customer_is_active_column() $$
DROP PROCEDURE IF EXISTS _add_customer_is_active_column $$

UPDATE customers
SET is_active = 1
WHERE is_active IS NULL $$

ALTER TABLE customers
    MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 $$

DROP PROCEDURE IF EXISTS _add_customer_archive_index $$
CREATE PROCEDURE _add_customer_archive_index()
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'customers'
          AND INDEX_NAME = 'idx_customers_is_active_name'
    ) THEN
        CREATE INDEX idx_customers_is_active_name
            ON customers (is_active, full_name);
    END IF;
END $$

CALL _add_customer_archive_index() $$
DROP PROCEDURE IF EXISTS _add_customer_archive_index $$

DROP VIEW IF EXISTS vw_customer_summary $$
CREATE VIEW vw_customer_summary AS
SELECT
    c.id AS id,
    TRIM(c.full_name) AS full_name,
    TRIM(c.address) AS address,
    c.contact_number AS contact_number,
    COALESCE(c.notes, '') AS notes,
    c.is_active AS is_active,
    c.created_at AS created_at,
    DATE_FORMAT(c.created_at, '%b %d, %Y') AS created_at_fmt,
    COALESCE(ds.total_deliveries, 0) AS total_deliveries,
    COALESCE(ds.delivered_deliveries, 0) AS delivered_deliveries,
    ds.last_delivery_date AS last_delivery_date,
    COALESCE(DATE_FORMAT(ds.last_delivery_date, '%b %d, %Y'), '-') AS last_delivery
FROM customers c
LEFT JOIN (
    SELECT
        d.customer_id AS customer_id,
        COUNT(*) AS total_deliveries,
        SUM(CASE WHEN d.status = 'delivered' THEN 1 ELSE 0 END) AS delivered_deliveries,
        MAX(d.schedule_date) AS last_delivery_date
    FROM deliveries d
    GROUP BY d.customer_id
) ds ON ds.customer_id = c.id $$

DROP TRIGGER IF EXISTS before_customer_insert $$
CREATE TRIGGER before_customer_insert
BEFORE INSERT ON customers
FOR EACH ROW
BEGIN
    SET NEW.full_name = TRIM(COALESCE(NEW.full_name, ''));
    SET NEW.address = TRIM(COALESCE(NEW.address, ''));
    SET NEW.contact_number = TRIM(COALESCE(NEW.contact_number, ''));
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');
    SET NEW.is_active = COALESCE(NEW.is_active, 1);

    IF NEW.full_name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF NEW.address = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF NEW.contact_number = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF NEW.contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer active status must be valid.';
    END IF;

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM customers c
           WHERE c.is_active = 1
             AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
                = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
             AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM customers c
           WHERE c.is_active = 1
             AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
                = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
             AND TRIM(c.contact_number) = NEW.contact_number
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END $$

DROP TRIGGER IF EXISTS before_customer_update $$
CREATE TRIGGER before_customer_update
BEFORE UPDATE ON customers
FOR EACH ROW
BEGIN
    IF NOT (OLD.id <=> NEW.id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer ID cannot be changed.';
    END IF;

    SET NEW.full_name = TRIM(COALESCE(NEW.full_name, ''));
    SET NEW.address = TRIM(COALESCE(NEW.address, ''));
    SET NEW.contact_number = TRIM(COALESCE(NEW.contact_number, ''));
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');
    SET NEW.is_active = COALESCE(NEW.is_active, OLD.is_active, 1);

    IF NEW.full_name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF NEW.address = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF NEW.contact_number = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF NEW.contact_number NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer active status must be valid.';
    END IF;

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM customers c
           WHERE c.id <> OLD.id
             AND c.is_active = 1
             AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
                = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
             AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM customers c
           WHERE c.id <> OLD.id
             AND c.is_active = 1
             AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
                = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
             AND TRIM(c.contact_number) = NEW.contact_number
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END $$

DROP TRIGGER IF EXISTS after_customer_insert $$
CREATE TRIGGER after_customer_insert
AFTER INSERT ON customers
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(NULLIF(@current_user_id, 0), 1),
        'INSERT',
        'customers',
        NEW.id,
        NULL,
        CONCAT(
            'Full Name: ', NEW.full_name,
            ', Address: ', NEW.address,
            ', Contact Number: ', NEW.contact_number,
            ', Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-'),
            ', Active: ', IF(NEW.is_active = 1, 'Yes', 'No')
        )
    );
END $$

DROP TRIGGER IF EXISTS after_customer_update $$
CREATE TRIGGER after_customer_update
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    IF NOT (OLD.full_name <=> NEW.full_name)
       OR NOT (OLD.address <=> NEW.address)
       OR NOT (OLD.contact_number <=> NEW.contact_number)
       OR NOT (OLD.notes <=> NEW.notes)
       OR NOT (OLD.is_active <=> NEW.is_active)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(NULLIF(@current_user_id, 0), 1),
            'UPDATE',
            'customers',
            NEW.id,
            CONCAT(
                'Full Name: ', OLD.full_name,
                ', Address: ', OLD.address,
                ', Contact Number: ', OLD.contact_number,
                ', Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-'),
                ', Active: ', IF(OLD.is_active = 1, 'Yes', 'No')
            ),
            CONCAT(
                'Full Name: ', NEW.full_name,
                ', Address: ', NEW.address,
                ', Contact Number: ', NEW.contact_number,
                ', Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-'),
                ', Active: ', IF(NEW.is_active = 1, 'Yes', 'No')
            )
        );
    END IF;
END $$

DROP TRIGGER IF EXISTS after_customer_delete $$
CREATE TRIGGER after_customer_delete
AFTER DELETE ON customers
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(NULLIF(@current_user_id, 0), 1),
        'DELETE',
        'customers',
        OLD.id,
        CONCAT(
            'Full Name: ', OLD.full_name,
            ', Address: ', OLD.address,
            ', Contact Number: ', OLD.contact_number,
            ', Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-'),
            ', Active: ', IF(OLD.is_active = 1, 'Yes', 'No')
        ),
        NULL
    );
END $$

DROP PROCEDURE IF EXISTS sp_add_customer $$
CREATE PROCEDURE sp_add_customer(
    IN p_full_name       VARCHAR(255),
    IN p_address         TEXT,
    IN p_contact_number  VARCHAR(20),
    IN p_notes           TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF TRIM(COALESCE(p_full_name, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_address, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_contact_number, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF TRIM(p_contact_number) NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
             = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(address)) = LOWER(TRIM(p_address))
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
             = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND TRIM(contact_number) = TRIM(p_contact_number)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;

    START TRANSACTION;
        INSERT INTO customers (full_name, address, contact_number, notes, is_active)
        VALUES (
            TRIM(p_full_name),
            TRIM(p_address),
            TRIM(p_contact_number),
            NULLIF(TRIM(COALESCE(p_notes, '')), ''),
            1
        );
    COMMIT;

    SELECT LAST_INSERT_ID() AS new_customer_id;
END $$

DROP PROCEDURE IF EXISTS sp_update_customer $$
CREATE PROCEDURE sp_update_customer(
    IN p_customer_id     INT,
    IN p_full_name       VARCHAR(255),
    IN p_address         TEXT,
    IN p_contact_number  VARCHAR(20),
    IN p_notes           TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF NOT EXISTS (SELECT 1 FROM customers WHERE id = p_customer_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer not found.';
    END IF;

    IF EXISTS (SELECT 1 FROM customers WHERE id = p_customer_id AND is_active = 0) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer is archived. Restore it before editing.';
    END IF;

    IF TRIM(COALESCE(p_full_name, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_address, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Address cannot be empty.';
    END IF;

    IF TRIM(COALESCE(p_contact_number, '')) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number cannot be empty.';
    END IF;

    IF TRIM(p_contact_number) NOT REGEXP '^(09[0-9]{9}|63[0-9]{10}|\\+63[0-9]{10})$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contact number must be a valid PH number (09XXXXXXXXX, 639XXXXXXXXX, or +639XXXXXXXXX).';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
             = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(address)) = LOWER(TRIM(p_address))
          AND id != p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')
             = REGEXP_REPLACE(LOWER(TRIM(p_full_name)), '[^a-z0-9 ]', '')
          AND TRIM(contact_number) = TRIM(p_contact_number)
          AND id != p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;

    START TRANSACTION;
        UPDATE customers
        SET
            full_name      = TRIM(p_full_name),
            address        = TRIM(p_address),
            contact_number = TRIM(p_contact_number),
            notes          = NULLIF(TRIM(COALESCE(p_notes, '')), '')
        WHERE id = p_customer_id
          AND is_active = 1;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Customer not found.';
        END IF;
    COMMIT;
END $$

DROP PROCEDURE IF EXISTS sp_archive_customer $$
CREATE PROCEDURE sp_archive_customer(IN p_customer_id INT)
BEGIN
    DECLARE v_customer_count INT DEFAULT 0;
    DECLARE v_is_active TINYINT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT COUNT(*), COALESCE(MAX(is_active), 0)
    INTO v_customer_count, v_is_active
    FROM customers
    WHERE id = p_customer_id;

    IF v_customer_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer not found.';
    END IF;

    IF v_is_active = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer is already archived.';
    END IF;

    START TRANSACTION;
        UPDATE customers
        SET is_active = 0
        WHERE id = p_customer_id
          AND is_active = 1;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Customer not found.';
        END IF;
    COMMIT;
END $$

DROP PROCEDURE IF EXISTS sp_restore_customer $$
CREATE PROCEDURE sp_restore_customer(IN p_customer_id INT)
BEGIN
    DECLARE v_customer_count INT DEFAULT 0;
    DECLARE v_is_active TINYINT DEFAULT 0;
    DECLARE v_normalized_name VARCHAR(255);
    DECLARE v_address TEXT;
    DECLARE v_contact_number VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT
        COUNT(*),
        COALESCE(MAX(is_active), 0),
        MAX(REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '')),
        MAX(LOWER(TRIM(address))),
        MAX(TRIM(contact_number))
    INTO
        v_customer_count,
        v_is_active,
        v_normalized_name,
        v_address,
        v_contact_number
    FROM customers
    WHERE id = p_customer_id;

    IF v_customer_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer not found.';
    END IF;

    IF v_is_active = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer is already active.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND id != p_customer_id
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '') = v_normalized_name
          AND LOWER(TRIM(address)) = v_address
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address is already active.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers
        WHERE is_active = 1
          AND id != p_customer_id
          AND REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '') = v_normalized_name
          AND TRIM(contact_number) = v_contact_number
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number is already active.';
    END IF;

    START TRANSACTION;
        UPDATE customers
        SET is_active = 1
        WHERE id = p_customer_id
          AND is_active = 0;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Customer not found.';
        END IF;
    COMMIT;
END $$

DROP PROCEDURE IF EXISTS sp_delete_customer $$
CREATE PROCEDURE sp_delete_customer(IN p_customer_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_customer_id IS NULL OR p_customer_id <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer ID.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM customers WHERE id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer not found.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM deliveries
        WHERE customer_id = p_customer_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer has delivery history. Archive instead.';
    END IF;

    START TRANSACTION;
        DELETE FROM customers WHERE id = p_customer_id;
    COMMIT;
END $$

DROP PROCEDURE IF EXISTS sp_create_delivery $$
CREATE PROCEDURE sp_create_delivery(
    IN p_customer_id INT,
    IN p_user_id INT,
    IN p_schedule_date DATE,
    IN p_notes TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_customer_id IS NULL OR NOT EXISTS (
        SELECT 1
        FROM customers
        WHERE id = p_customer_id
          AND is_active = 1
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer or customer is archived.';
    END IF;

    IF p_user_id IS NULL OR NOT EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM users
        WHERE id = p_user_id
          AND role = 'admin'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only administrators can create deliveries.';
    END IF;

    IF p_schedule_date IS NULL OR p_schedule_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Schedule date cannot be in the past.';
    END IF;

    INSERT INTO deliveries (customer_id, user_id, schedule_date, notes)
    VALUES (p_customer_id, p_user_id, p_schedule_date, p_notes);

    SELECT LAST_INSERT_ID() AS new_delivery_id;
END $$

DROP TRIGGER IF EXISTS before_delivery_insert $$
CREATE TRIGGER before_delivery_insert
BEFORE INSERT ON deliveries
FOR EACH ROW
BEGIN
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

    IF NEW.customer_id IS NULL
       OR NOT EXISTS (
           SELECT 1
           FROM customers
           WHERE id = NEW.customer_id
             AND is_active = 1
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid customer or customer is archived.';
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
END $$

DELIMITER ;
