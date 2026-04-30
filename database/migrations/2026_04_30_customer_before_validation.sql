DROP TRIGGER IF EXISTS before_customer_insert;
DROP TRIGGER IF EXISTS before_customer_update;

DELIMITER //

CREATE TRIGGER before_customer_insert
BEFORE INSERT ON customers
FOR EACH ROW
BEGIN
    SET NEW.full_name = TRIM(COALESCE(NEW.full_name, ''));
    SET NEW.address = TRIM(COALESCE(NEW.address, ''));
    SET NEW.contact_number = TRIM(COALESCE(NEW.contact_number, ''));
    SET NEW.notes = NULLIF(TRIM(COALESCE(NEW.notes, '')), '');

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

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND TRIM(c.contact_number) = NEW.contact_number
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END//

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

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE c.id <> OLD.id
          AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND LOWER(TRIM(c.address)) = LOWER(NEW.address)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and address already exists.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM customers c
        WHERE c.id <> OLD.id
          AND REGEXP_REPLACE(LOWER(TRIM(c.full_name)), '[^a-z0-9 ]', '')
            = REGEXP_REPLACE(LOWER(NEW.full_name), '[^a-z0-9 ]', '')
          AND TRIM(c.contact_number) = NEW.contact_number
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A customer with the same name and contact number already exists.';
    END IF;
END//

DELIMITER ;