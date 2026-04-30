DROP TRIGGER IF EXISTS after_user_update;

DELIMITER //

CREATE TRIGGER after_user_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF NOT (OLD.full_name <=> NEW.full_name)
       OR NOT (OLD.username <=> NEW.username)
       OR NOT (OLD.email <=> NEW.email)
       OR NOT (OLD.role <=> NEW.role)
       OR NOT (OLD.password <=> NEW.password)
    THEN
        INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
        VALUES (
            COALESCE(NULLIF(@current_user_id, 0), NEW.id),
            'UPDATE',
            'users',
            NEW.id,
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', OLD.full_name), NULL),
                IF(NOT (OLD.username <=> NEW.username), CONCAT('Username: ', OLD.username), NULL),
                IF(NOT (OLD.email <=> NEW.email), CONCAT('Email: ', COALESCE(OLD.email, '-')), NULL),
                IF(NOT (OLD.role <=> NEW.role), CONCAT('Role: ', OLD.role), NULL),
                IF(NOT (OLD.password <=> NEW.password), 'Password: Previous password', NULL)
            ),
            CONCAT_WS(', ',
                IF(NOT (OLD.full_name <=> NEW.full_name), CONCAT('Full Name: ', NEW.full_name), NULL),
                IF(NOT (OLD.username <=> NEW.username), CONCAT('Username: ', NEW.username), NULL),
                IF(NOT (OLD.email <=> NEW.email), CONCAT('Email: ', COALESCE(NEW.email, '-')), NULL),
                IF(NOT (OLD.role <=> NEW.role), CONCAT('Role: ', NEW.role), NULL),
                IF(NOT (OLD.password <=> NEW.password), 'Password: New password', NULL)
            )
        );
    END IF;
END//

DELIMITER ;
