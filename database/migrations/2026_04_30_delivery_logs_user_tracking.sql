DELIMITER $$

DROP PROCEDURE IF EXISTS sp_update_delivery_status $$

CREATE PROCEDURE sp_update_delivery_status(
    IN p_delivery_id INT,
    IN p_new_status VARCHAR(20),
    IN p_user_id INT
)
BEGIN
    DECLARE v_old_status VARCHAR(20);
    DECLARE v_delivery_count INT DEFAULT 0;
    DECLARE v_paid_transaction_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET p_new_status = LOWER(TRIM(p_new_status));
    SET @current_user_id = NULLIF(p_user_id, 0);

    IF p_new_status NOT IN ('pending', 'in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid delivery status.';
    END IF;

    SELECT COUNT(*), MAX(status)
    INTO v_delivery_count, v_old_status
    FROM deliveries
    WHERE id = p_delivery_id;

    IF v_delivery_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivery not found.';
    END IF;

    IF v_old_status = p_new_status THEN
        SELECT v_old_status AS old_status, p_new_status AS new_status;
    ELSEIF v_old_status = 'pending'
          AND p_new_status NOT IN ('in_transit', 'delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Pending deliveries can only move to in transit, delivered, or cancelled.';
    ELSEIF v_old_status = 'in_transit'
          AND p_new_status NOT IN ('delivered', 'cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'In-transit deliveries can only move to delivered or cancelled.';
    ELSEIF v_old_status = 'cancelled' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cancelled deliveries cannot be changed.';
    ELSEIF v_old_status = 'delivered'
          AND p_new_status <> 'cancelled' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Delivered deliveries can only be cancelled when unpaid.';
    ELSE
        START TRANSACTION;

            IF p_new_status <> 'delivered' THEN
                SELECT COUNT(*)
                INTO v_paid_transaction_count
                FROM transactions
                WHERE delivery_id = p_delivery_id
                  AND payment_status = 'paid';

                IF v_paid_transaction_count > 0 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Paid deliveries cannot be cancelled.';
                END IF;

                DELETE FROM transactions
                WHERE delivery_id = p_delivery_id
                  AND payment_status = 'unpaid';
            END IF;

            UPDATE deliveries
            SET status = p_new_status
            WHERE id = p_delivery_id;

        COMMIT;

        SELECT v_old_status AS old_status, p_new_status AS new_status;
    END IF;
END $$

DROP TRIGGER IF EXISTS after_delivery_status_update $$

CREATE TRIGGER after_delivery_status_update
AFTER UPDATE ON deliveries
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO delivery_logs (delivery_id, user_id, old_status, new_status)
        VALUES (
            NEW.id,
            COALESCE(NULLIF(@current_user_id, 0), NEW.user_id),
            OLD.status,
            NEW.status
        );
    END IF;
END $$

DELIMITER ;

SET @idx_delivery_logs_changed_at_id_exists = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'delivery_logs'
      AND index_name = 'idx_delivery_logs_changed_at_id'
);

SET @idx_delivery_logs_changed_at_id_sql = IF(
    @idx_delivery_logs_changed_at_id_exists = 0,
    'CREATE INDEX idx_delivery_logs_changed_at_id ON delivery_logs (changed_at, id)',
    'DO 0'
);

PREPARE idx_delivery_logs_changed_at_id_stmt FROM @idx_delivery_logs_changed_at_id_sql;
EXECUTE idx_delivery_logs_changed_at_id_stmt;
DEALLOCATE PREPARE idx_delivery_logs_changed_at_id_stmt;
