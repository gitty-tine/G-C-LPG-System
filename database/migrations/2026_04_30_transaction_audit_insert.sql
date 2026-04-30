DROP TRIGGER IF EXISTS after_transaction_insert;

DELIMITER //

CREATE TRIGGER after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
    VALUES (
        COALESCE(
            NULLIF(@current_user_id, 0),
            (SELECT d.user_id FROM deliveries d WHERE d.id = NEW.delivery_id),
            1
        ),
        'INSERT',
        'transactions',
        NEW.id,
        NULL,
        CONCAT(
            'Payment Status: ', NEW.payment_status,
            ', Customer: ', COALESCE((
                SELECT c.full_name
                FROM deliveries d
                INNER JOIN customers c ON c.id = d.customer_id
                WHERE d.id = NEW.delivery_id
            ), '-'),
            ', Total Amount: ', NEW.total_amount,
            ', Delivery ID: ', NEW.delivery_id
        )
    );
END//

DELIMITER ;
