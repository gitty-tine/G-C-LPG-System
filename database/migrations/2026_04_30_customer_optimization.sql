CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT
    c.id,
    TRIM(c.full_name)                                      AS full_name,
    TRIM(c.address)                                        AS address,
    c.contact_number,
    COALESCE(c.notes, '')                                  AS notes,
    c.created_at,
    DATE_FORMAT(c.created_at, '%b %d, %Y')                 AS created_at_fmt,
    COALESCE(ds.total_deliveries, 0)                       AS total_deliveries,
    COALESCE(ds.delivered_deliveries, 0)                   AS delivered_deliveries,
    ds.last_delivery_date,
    COALESCE(DATE_FORMAT(ds.last_delivery_date, '%b %d, %Y'), '-') AS last_delivery
FROM customers c
LEFT JOIN (
    SELECT
        d.customer_id,
        COUNT(*)                                           AS total_deliveries,
        SUM(CASE WHEN d.status = 'delivered' THEN 1 ELSE 0 END) AS delivered_deliveries,
        MAX(d.schedule_date)                               AS last_delivery_date
    FROM deliveries d
    GROUP BY d.customer_id
) ds ON ds.customer_id = c.id;

SET @idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'customers'
      AND INDEX_NAME = 'idx_customers_created_at_id'
);
SET @sql := IF(
    @idx_exists = 0,
    'CREATE INDEX idx_customers_created_at_id ON customers (created_at, id)',
    'SELECT ''idx_customers_created_at_id already exists'' AS info'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'customers'
      AND INDEX_NAME = 'idx_customers_full_name'
);
SET @sql := IF(
    @idx_exists = 0,
    'CREATE INDEX idx_customers_full_name ON customers (full_name)',
    'SELECT ''idx_customers_full_name already exists'' AS info'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'deliveries'
      AND INDEX_NAME = 'idx_deliveries_customer_schedule_date'
);
SET @sql := IF(
    @idx_exists = 0,
    'CREATE INDEX idx_deliveries_customer_schedule_date ON deliveries (customer_id, schedule_date)',
    'SELECT ''idx_deliveries_customer_schedule_date already exists'' AS info'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

DROP TRIGGER IF EXISTS after_customer_insert;
DROP TRIGGER IF EXISTS after_customer_update;
DROP TRIGGER IF EXISTS after_customer_delete;

DELIMITER //

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
        CONCAT_WS(', ',
            CONCAT('Full Name: ', NEW.full_name),
            CONCAT('Address: ', NEW.address),
            CONCAT('Contact Number: ', NEW.contact_number),
            CONCAT('Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-'))
        )
    );
END//

CREATE TRIGGER after_customer_update
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    IF NOT (OLD.full_name <=> NEW.full_name)
       OR NOT (OLD.address <=> NEW.address)
       OR NOT (OLD.contact_number <=> NEW.contact_number)
       OR NOT (OLD.notes <=> NEW.notes)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(NULLIF(@current_user_id, 0), 1),
            'UPDATE',
            'customers',
            NEW.id,
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', OLD.full_name), NULL),
                IF(NOT (OLD.address <=> NEW.address), CONCAT('Address: ', OLD.address), NULL),
                IF(NOT (OLD.contact_number <=> NEW.contact_number), CONCAT('Contact Number: ', OLD.contact_number), NULL),
                IF(NOT (OLD.notes <=> NEW.notes), CONCAT('Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-')), NULL)
            ),
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', NEW.full_name), NULL),
                IF(NOT (OLD.address <=> NEW.address), CONCAT('Address: ', NEW.address), NULL),
                IF(NOT (OLD.contact_number <=> NEW.contact_number), CONCAT('Contact Number: ', NEW.contact_number), NULL),
                IF(NOT (OLD.notes <=> NEW.notes), CONCAT('Notes: ', COALESCE(NULLIF(NEW.notes, ''), '-')), NULL)
            )
        );
    END IF;
END//

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
        CONCAT_WS(', ',
            CONCAT('Full Name: ', OLD.full_name),
            CONCAT('Address: ', OLD.address),
            CONCAT('Contact Number: ', OLD.contact_number),
            CONCAT('Notes: ', COALESCE(NULLIF(OLD.notes, ''), '-'))
        ),
        NULL
    );
END//

DELIMITER ;
