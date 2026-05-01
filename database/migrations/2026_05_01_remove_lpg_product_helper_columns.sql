-- Remove visible LPG product helper columns.
-- The app and stored procedures now normalize name/size directly from the
-- user-facing columns, so these duplicate-looking columns are no longer needed:
-- normalized_name, normalized_cylinder_size, active_name_key, active_size_key.

DELIMITER $$

DROP TRIGGER IF EXISTS before_product_insert $$
DROP TRIGGER IF EXISTS before_product_update $$

DROP PROCEDURE IF EXISTS _drop_lpg_product_index $$
CREATE PROCEDURE _drop_lpg_product_index()
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'lpg_products'
          AND INDEX_NAME = 'uq_lpg_products_active_name_size'
    ) THEN
        DROP INDEX uq_lpg_products_active_name_size ON lpg_products;
    END IF;
END $$

CALL _drop_lpg_product_index() $$
DROP PROCEDURE IF EXISTS _drop_lpg_product_index $$

DROP PROCEDURE IF EXISTS _drop_lpg_product_column $$
CREATE PROCEDURE _drop_lpg_product_column(IN p_column_name VARCHAR(64))
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'lpg_products'
          AND COLUMN_NAME = p_column_name
    ) THEN
        SET @ddl = CONCAT('ALTER TABLE `lpg_products` DROP COLUMN `', p_column_name, '`');
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END $$

CALL _drop_lpg_product_column('active_name_key') $$
CALL _drop_lpg_product_column('active_size_key') $$
CALL _drop_lpg_product_column('normalized_name') $$
CALL _drop_lpg_product_column('normalized_cylinder_size') $$

DROP PROCEDURE IF EXISTS _drop_lpg_product_column $$

DROP TRIGGER IF EXISTS before_product_insert $$
CREATE TRIGGER before_product_insert
BEFORE INSERT ON lpg_products
FOR EACH ROW
BEGIN
    DECLARE v_size_value DECIMAL(10,2);
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    SET NEW.name = TRIM(COALESCE(NEW.name, ''));
    SET NEW.cylinder_size = TRIM(COALESCE(NEW.cylinder_size, ''));
    SET NEW.is_active = COALESCE(NEW.is_active, 1);

    IF NEW.name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product name cannot be empty.';
    END IF;

    IF NEW.cylinder_size = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size cannot be empty.';
    END IF;

    IF NOT REGEXP_LIKE(NEW.cylinder_size, '^[[:space:]]*[0-9]+(\\.[0-9]+)?[[:space:]]*(kg)?[[:space:]]*$', 'i') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Enter a valid cylinder size like 2.7 or 11kg.';
    END IF;

    SET v_size_value = CAST(REGEXP_REPLACE(NEW.cylinder_size, '[^0-9.]', '') AS DECIMAL(10,2));
    IF v_size_value <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size must be greater than zero.';
    END IF;

    IF NEW.refill_price IS NULL OR NEW.refill_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Refill price must be greater than zero.';
    END IF;

    IF NEW.new_tank_price IS NULL OR NEW.new_tank_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New tank price must be greater than zero.';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product active status must be valid.';
    END IF;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(NEW.name), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(NEW.cylinder_size);

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE is_active = 1
             AND TRIM(
                 REGEXP_REPLACE(
                     REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                     '\\s+',
                     ' '
                 )
             ) = v_normalized_name
             AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = v_normalized_size
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    SET NEW.refill_price = ROUND(NEW.refill_price, 2);
    SET NEW.new_tank_price = ROUND(NEW.new_tank_price, 2);
END $$

DROP TRIGGER IF EXISTS before_product_update $$
CREATE TRIGGER before_product_update
BEFORE UPDATE ON lpg_products
FOR EACH ROW
BEGIN
    DECLARE v_size_value DECIMAL(10,2);
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    SET NEW.name = TRIM(COALESCE(NEW.name, ''));
    SET NEW.cylinder_size = TRIM(COALESCE(NEW.cylinder_size, ''));
    SET NEW.is_active = COALESCE(NEW.is_active, OLD.is_active, 1);

    IF NEW.name = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product name cannot be empty.';
    END IF;

    IF NEW.cylinder_size = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size cannot be empty.';
    END IF;

    IF NOT REGEXP_LIKE(NEW.cylinder_size, '^[[:space:]]*[0-9]+(\\.[0-9]+)?[[:space:]]*(kg)?[[:space:]]*$', 'i') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Enter a valid cylinder size like 2.7 or 11kg.';
    END IF;

    SET v_size_value = CAST(REGEXP_REPLACE(NEW.cylinder_size, '[^0-9.]', '') AS DECIMAL(10,2));
    IF v_size_value <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cylinder size must be greater than zero.';
    END IF;

    IF NEW.refill_price IS NULL OR NEW.refill_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Refill price must be greater than zero.';
    END IF;

    IF NEW.new_tank_price IS NULL OR NEW.new_tank_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'New tank price must be greater than zero.';
    END IF;

    IF NEW.is_active NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product active status must be valid.';
    END IF;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(NEW.name), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(NEW.cylinder_size);

    IF NEW.is_active = 1
       AND EXISTS (
           SELECT 1
           FROM lpg_products
           WHERE is_active = 1
             AND id != OLD.id
             AND TRIM(
                 REGEXP_REPLACE(
                     REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                     '\\s+',
                     ' '
                 )
             ) = v_normalized_name
             AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = v_normalized_size
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    SET NEW.refill_price = ROUND(NEW.refill_price, 2);
    SET NEW.new_tank_price = ROUND(NEW.new_tank_price, 2);
END $$

DROP PROCEDURE IF EXISTS sp_add_product $$
CREATE PROCEDURE sp_add_product(
    IN p_name           VARCHAR(100),
    IN p_cylinder_size  VARCHAR(20),
    IN p_refill_price   DECIMAL(10,2),
    IN p_new_tank_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(TRIM(COALESCE(p_name, ''))), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(TRIM(COALESCE(p_cylinder_size, '')));

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND TRIM(
              REGEXP_REPLACE(
                  REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                  '\\s+',
                  ' '
              )
          ) = v_normalized_name
          AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = v_normalized_size
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    START TRANSACTION;
        INSERT INTO lpg_products (
            name,
            cylinder_size,
            refill_price,
            new_tank_price,
            is_active
        )
        VALUES (
            TRIM(p_name),
            TRIM(p_cylinder_size),
            p_refill_price,
            p_new_tank_price,
            1
        );
    COMMIT;

    SELECT LAST_INSERT_ID() AS new_product_id;
END $$

DROP PROCEDURE IF EXISTS sp_update_product $$
CREATE PROCEDURE sp_update_product(
    IN p_product_id     INT,
    IN p_name           VARCHAR(100),
    IN p_cylinder_size  VARCHAR(20),
    IN p_refill_price   DECIMAL(10,2),
    IN p_new_tank_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_normalized_name = TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(LOWER(TRIM(COALESCE(p_name, ''))), '[^a-z0-9 ]', ''),
            '\\s+',
            ' '
        )
    );
    SET v_normalized_size = LOWER(TRIM(COALESCE(p_cylinder_size, '')));

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND TRIM(
              REGEXP_REPLACE(
                  REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                  '\\s+',
                  ' '
              )
          ) = v_normalized_name
          AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = v_normalized_size
          AND id != p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size already exists.';
    END IF;

    START TRANSACTION;
        UPDATE lpg_products
        SET
            name = TRIM(p_name),
            cylinder_size = TRIM(p_cylinder_size),
            refill_price = p_refill_price,
            new_tank_price = p_new_tank_price
        WHERE id = p_product_id
          AND is_active = 1;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found.';
        END IF;
    COMMIT;
END $$

DROP PROCEDURE IF EXISTS sp_restore_product $$
CREATE PROCEDURE sp_restore_product(IN p_product_id INT)
BEGIN
    DECLARE v_product_count INT DEFAULT 0;
    DECLARE v_is_active TINYINT DEFAULT 0;
    DECLARE v_normalized_name VARCHAR(100);
    DECLARE v_normalized_size VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SELECT
        COUNT(*),
        COALESCE(MAX(is_active), 0),
        MAX(
            TRIM(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                    '\\s+',
                    ' '
                )
            )
        ),
        MAX(LOWER(TRIM(COALESCE(cylinder_size, ''))))
    INTO
        v_product_count,
        v_is_active,
        v_normalized_name,
        v_normalized_size
    FROM lpg_products
    WHERE id = p_product_id;

    IF v_product_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found.';
    END IF;

    IF v_is_active = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product is already active.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM lpg_products
        WHERE is_active = 1
          AND TRIM(
              REGEXP_REPLACE(
                  REGEXP_REPLACE(LOWER(TRIM(COALESCE(name, ''))), '[^a-z0-9 ]', ''),
                  '\\s+',
                  ' '
              )
          ) = v_normalized_name
          AND LOWER(TRIM(COALESCE(cylinder_size, ''))) = v_normalized_size
          AND id != p_product_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A product with this name and cylinder size is already active.';
    END IF;

    START TRANSACTION;
        UPDATE lpg_products
        SET is_active = 1
        WHERE id = p_product_id
          AND is_active = 0;

        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found.';
        END IF;
    COMMIT;
END $$

DELIMITER ;
