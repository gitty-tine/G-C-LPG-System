-- Reporting consistency migration
-- Goal: make report/dashboard sales count only delivered deliveries, while
-- keeping cancelled/pending/in-transit rows visible for operational reporting.

-- 1) Snapshot tables: store the full summary shape used by the report UI.
ALTER TABLE daily_reports
    ADD COLUMN total_in_transit INT NOT NULL DEFAULT 0 AFTER total_pending,
    ADD COLUMN total_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_sales,
    ADD COLUMN total_unpaid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_paid;

ALTER TABLE weekly_reports
    ADD COLUMN total_in_transit INT NOT NULL DEFAULT 0 AFTER total_pending,
    ADD COLUMN total_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_sales,
    ADD COLUMN total_unpaid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_paid;

ALTER TABLE monthly_reports
    ADD COLUMN total_in_transit INT NOT NULL DEFAULT 0 AFTER total_pending,
    ADD COLUMN total_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_sales,
    ADD COLUMN total_unpaid DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER total_paid;

-- 2) Helpful composite indexes for report date/status scans.
CREATE INDEX idx_deliveries_status_date ON deliveries (status, schedule_date, id);
CREATE INDEX idx_delivery_items_product_delivery ON delivery_items (product_id, delivery_id);

-- 3) One-row-per-delivery report source of truth.
CREATE OR REPLACE VIEW vw_report_delivery_financials AS
SELECT
    d.id                                                       AS delivery_id,
    d.customer_id,
    TRIM(c.full_name)                                         AS customer_name,
    c.contact_number                                          AS customer_contact,
    c.address                                                 AS customer_address,
    d.user_id,
    d.schedule_date,
    d.status                                                   AS delivery_status,
    d.notes,
    d.created_at,
    d.updated_at,
    t.id                                                       AS transaction_id,
    t.payment_status                                           AS transaction_payment_status,
    CASE
        WHEN d.status = 'delivered'
            THEN COALESCE(t.payment_status, 'unpaid')
        ELSE 'not_applicable'
    END                                                        AS report_payment_status,
    t.paid_at,
    COALESCE(it.total_quantity, 0)                             AS total_quantity,
    COALESCE(it.item_total, 0)                                 AS item_total,
    COALESCE(t.total_amount, it.item_total, 0)                 AS gross_amount,
    CASE WHEN d.status = 'delivered' THEN 1 ELSE 0 END         AS delivered_count,
    CASE WHEN d.status = 'cancelled' THEN 1 ELSE 0 END         AS cancelled_count,
    CASE WHEN d.status = 'pending' THEN 1 ELSE 0 END           AS pending_count,
    CASE WHEN d.status = 'in_transit' THEN 1 ELSE 0 END        AS in_transit_count,
    CASE
        WHEN d.status = 'delivered'
            THEN COALESCE(t.total_amount, it.item_total, 0)
        ELSE 0
    END                                                        AS recognized_sales,
    CASE
        WHEN d.status = 'delivered'
             AND COALESCE(t.payment_status, 'unpaid') = 'paid'
            THEN COALESCE(t.total_amount, it.item_total, 0)
        ELSE 0
    END                                                        AS paid_sales,
    CASE
        WHEN d.status = 'delivered'
             AND COALESCE(t.payment_status, 'unpaid') = 'unpaid'
            THEN COALESCE(t.total_amount, it.item_total, 0)
        ELSE 0
    END                                                        AS unpaid_sales
FROM deliveries d
INNER JOIN customers c ON c.id = d.customer_id
LEFT JOIN transactions t ON t.delivery_id = d.id
LEFT JOIN (
    SELECT
        di.delivery_id,
        SUM(di.quantity)                                      AS total_quantity,
        SUM(di.quantity * di.price_at_delivery)               AS item_total
    FROM delivery_items di
    GROUP BY di.delivery_id
) it ON it.delivery_id = d.id;

-- 4) One-row-per-delivery-item report source of truth.
CREATE OR REPLACE VIEW vw_report_delivery_lines AS
SELECT
    f.delivery_id,
    f.customer_id,
    f.customer_name,
    f.customer_contact,
    f.customer_address,
    f.schedule_date,
    f.delivery_status,
    f.report_payment_status                                   AS payment_status,
    f.transaction_id,
    f.paid_at,
    di.id                                                      AS delivery_item_id,
    di.product_id,
    CONCAT(TRIM(p.name), ' ', COALESCE(p.cylinder_size, ''))   AS product_name,
    di.quantity,
    di.type,
    di.price_at_delivery,
    ROUND(di.quantity * di.price_at_delivery, 2)               AS line_amount,
    CASE
        WHEN f.delivery_status = 'delivered'
            THEN ROUND(di.quantity * di.price_at_delivery, 2)
        ELSE 0
    END                                                        AS recognized_line_sales
FROM vw_report_delivery_financials f
INNER JOIN delivery_items di ON di.delivery_id = f.delivery_id
INNER JOIN lpg_products p ON p.id = di.product_id;

-- 5) Dashboard today must share the same delivered-sales rule.
CREATE OR REPLACE VIEW vw_dashboard_today AS
SELECT
    COUNT(*)                                                   AS total_today,
    COALESCE(SUM(delivered_count), 0)                          AS delivered_today,
    COALESCE(SUM(pending_count), 0)                            AS pending_today,
    COALESCE(SUM(in_transit_count), 0)                         AS in_transit_today,
    COALESCE(SUM(cancelled_count), 0)                          AS cancelled_today,
    COALESCE(SUM(recognized_sales), 0)                         AS sales_today
FROM vw_report_delivery_financials
WHERE schedule_date = CURDATE();

-- 6) Existing delivery-report procedure now reads from the report source view.
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_get_delivery_report $$
CREATE PROCEDURE sp_get_delivery_report(
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN
    SELECT
        f.delivery_id,
        f.schedule_date,
        f.delivery_status                                     AS status,
        f.customer_name,
        f.customer_address,
        f.total_quantity,
        f.gross_amount                                        AS computed_total,
        f.report_payment_status                               AS payment_status,
        f.paid_at
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN p_date_from AND p_date_to
    ORDER BY f.schedule_date DESC, f.delivery_id DESC;
END $$
DELIMITER ;

-- 7) Existing sales-summary procedure now excludes cancelled/non-delivered money.
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_get_sales_summary $$
CREATE PROCEDURE sp_get_sales_summary(
    IN p_period VARCHAR(10)
)
BEGIN
    DECLARE v_date_from DATE;

    SET v_date_from = CASE p_period
        WHEN 'daily'   THEN CURDATE()
        WHEN 'weekly'  THEN DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        WHEN 'monthly' THEN DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ELSE CURDATE()
    END;

    SELECT
        f.schedule_date                                        AS delivery_date,
        COUNT(*)                                               AS total_deliveries,
        COALESCE(SUM(f.delivered_count), 0)                    AS delivered,
        COALESCE(SUM(f.cancelled_count), 0)                    AS cancelled,
        COALESCE(SUM(f.pending_count), 0)                      AS pending,
        COALESCE(SUM(f.in_transit_count), 0)                   AS in_transit,
        COALESCE(SUM(f.recognized_sales), 0)                   AS total_sales,
        COALESCE(SUM(f.paid_sales), 0)                         AS paid_sales,
        COALESCE(SUM(f.unpaid_sales), 0)                       AS unpaid_sales
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN v_date_from AND CURDATE()
    GROUP BY f.schedule_date
    ORDER BY delivery_date DESC;
END $$
DELIMITER ;

-- 8) Guard status transitions and keep non-delivered deliveries transaction-free.
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
DELIMITER ;

-- 9) Clean safe transaction anomalies before rebuilding snapshots.
-- Paid non-delivered transactions are intentionally not deleted.
DELETE t
FROM transactions t
INNER JOIN deliveries d ON d.id = t.delivery_id
WHERE d.status <> 'delivered'
  AND t.payment_status = 'unpaid';

-- 10) Rebuild report snapshots from the same source view.
INSERT INTO daily_reports (
    report_date,
    total_deliveries,
    total_delivered,
    total_cancelled,
    total_pending,
    total_in_transit,
    total_sales,
    total_paid,
    total_unpaid
)
SELECT
    f.schedule_date,
    COUNT(*),
    COALESCE(SUM(f.delivered_count), 0),
    COALESCE(SUM(f.cancelled_count), 0),
    COALESCE(SUM(f.pending_count), 0),
    COALESCE(SUM(f.in_transit_count), 0),
    COALESCE(SUM(f.recognized_sales), 0),
    COALESCE(SUM(f.paid_sales), 0),
    COALESCE(SUM(f.unpaid_sales), 0)
FROM vw_report_delivery_financials f
WHERE f.schedule_date < CURDATE()
GROUP BY f.schedule_date
ON DUPLICATE KEY UPDATE
    total_deliveries  = VALUES(total_deliveries),
    total_delivered   = VALUES(total_delivered),
    total_cancelled   = VALUES(total_cancelled),
    total_pending     = VALUES(total_pending),
    total_in_transit  = VALUES(total_in_transit),
    total_sales       = VALUES(total_sales),
    total_paid        = VALUES(total_paid),
    total_unpaid      = VALUES(total_unpaid),
    generated_at      = CURRENT_TIMESTAMP;

INSERT INTO weekly_reports (
    week_start,
    week_end,
    total_deliveries,
    total_delivered,
    total_cancelled,
    total_pending,
    total_in_transit,
    total_sales,
    total_paid,
    total_unpaid
)
SELECT
    DATE_SUB(f.schedule_date, INTERVAL WEEKDAY(f.schedule_date) DAY) AS week_start,
    DATE_ADD(
        DATE_SUB(f.schedule_date, INTERVAL WEEKDAY(f.schedule_date) DAY),
        INTERVAL 6 DAY
    ) AS week_end,
    COUNT(*),
    COALESCE(SUM(f.delivered_count), 0),
    COALESCE(SUM(f.cancelled_count), 0),
    COALESCE(SUM(f.pending_count), 0),
    COALESCE(SUM(f.in_transit_count), 0),
    COALESCE(SUM(f.recognized_sales), 0),
    COALESCE(SUM(f.paid_sales), 0),
    COALESCE(SUM(f.unpaid_sales), 0)
FROM vw_report_delivery_financials f
WHERE f.schedule_date < DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
GROUP BY
    DATE_SUB(f.schedule_date, INTERVAL WEEKDAY(f.schedule_date) DAY),
    DATE_ADD(
        DATE_SUB(f.schedule_date, INTERVAL WEEKDAY(f.schedule_date) DAY),
        INTERVAL 6 DAY
    )
ON DUPLICATE KEY UPDATE
    week_end          = VALUES(week_end),
    total_deliveries  = VALUES(total_deliveries),
    total_delivered   = VALUES(total_delivered),
    total_cancelled   = VALUES(total_cancelled),
    total_pending     = VALUES(total_pending),
    total_in_transit  = VALUES(total_in_transit),
    total_sales       = VALUES(total_sales),
    total_paid        = VALUES(total_paid),
    total_unpaid      = VALUES(total_unpaid),
    generated_at      = CURRENT_TIMESTAMP;

INSERT INTO monthly_reports (
    report_month,
    total_deliveries,
    total_delivered,
    total_cancelled,
    total_pending,
    total_in_transit,
    total_sales,
    total_paid,
    total_unpaid
)
SELECT
    DATE_FORMAT(f.schedule_date, '%Y-%m-01') AS report_month,
    COUNT(*),
    COALESCE(SUM(f.delivered_count), 0),
    COALESCE(SUM(f.cancelled_count), 0),
    COALESCE(SUM(f.pending_count), 0),
    COALESCE(SUM(f.in_transit_count), 0),
    COALESCE(SUM(f.recognized_sales), 0),
    COALESCE(SUM(f.paid_sales), 0),
    COALESCE(SUM(f.unpaid_sales), 0)
FROM vw_report_delivery_financials f
WHERE f.schedule_date < DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY DATE_FORMAT(f.schedule_date, '%Y-%m-01')
ON DUPLICATE KEY UPDATE
    total_deliveries  = VALUES(total_deliveries),
    total_delivered   = VALUES(total_delivered),
    total_cancelled   = VALUES(total_cancelled),
    total_pending     = VALUES(total_pending),
    total_in_transit  = VALUES(total_in_transit),
    total_sales       = VALUES(total_sales),
    total_paid        = VALUES(total_paid),
    total_unpaid      = VALUES(total_unpaid),
    generated_at      = CURRENT_TIMESTAMP;

-- 11) Events now populate snapshots using the source view.
DROP EVENT IF EXISTS generate_daily_summary;
CREATE EVENT generate_daily_summary
ON SCHEDULE EVERY 1 DAY STARTS '2026-04-30 00:00:00'
ON COMPLETION NOT PRESERVE ENABLE
DO
INSERT INTO daily_reports (
    report_date,
    total_deliveries,
    total_delivered,
    total_cancelled,
    total_pending,
    total_in_transit,
    total_sales,
    total_paid,
    total_unpaid
)
SELECT
    CURDATE() - INTERVAL 1 DAY,
    COUNT(*),
    COALESCE(SUM(f.delivered_count), 0),
    COALESCE(SUM(f.cancelled_count), 0),
    COALESCE(SUM(f.pending_count), 0),
    COALESCE(SUM(f.in_transit_count), 0),
    COALESCE(SUM(f.recognized_sales), 0),
    COALESCE(SUM(f.paid_sales), 0),
    COALESCE(SUM(f.unpaid_sales), 0)
FROM vw_report_delivery_financials f
WHERE f.schedule_date = CURDATE() - INTERVAL 1 DAY
ON DUPLICATE KEY UPDATE
    total_deliveries  = VALUES(total_deliveries),
    total_delivered   = VALUES(total_delivered),
    total_cancelled   = VALUES(total_cancelled),
    total_pending     = VALUES(total_pending),
    total_in_transit  = VALUES(total_in_transit),
    total_sales       = VALUES(total_sales),
    total_paid        = VALUES(total_paid),
    total_unpaid      = VALUES(total_unpaid),
    generated_at      = CURRENT_TIMESTAMP;

DROP EVENT IF EXISTS generate_weekly_summary;
DELIMITER $$
CREATE EVENT generate_weekly_summary
ON SCHEDULE EVERY 1 WEEK STARTS '2026-03-30 00:00:00'
ON COMPLETION NOT PRESERVE ENABLE
DO
BEGIN
    INSERT INTO weekly_reports (
        week_start,
        week_end,
        total_deliveries,
        total_delivered,
        total_cancelled,
        total_pending,
        total_in_transit,
        total_sales,
        total_paid,
        total_unpaid
    )
    SELECT
        CURDATE() - INTERVAL 7 DAY,
        CURDATE() - INTERVAL 1 DAY,
        COUNT(*),
        COALESCE(SUM(f.delivered_count), 0),
        COALESCE(SUM(f.cancelled_count), 0),
        COALESCE(SUM(f.pending_count), 0),
        COALESCE(SUM(f.in_transit_count), 0),
        COALESCE(SUM(f.recognized_sales), 0),
        COALESCE(SUM(f.paid_sales), 0),
        COALESCE(SUM(f.unpaid_sales), 0)
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date BETWEEN CURDATE() - INTERVAL 7 DAY
                              AND CURDATE() - INTERVAL 1 DAY
    ON DUPLICATE KEY UPDATE
        week_end          = VALUES(week_end),
        total_deliveries  = VALUES(total_deliveries),
        total_delivered   = VALUES(total_delivered),
        total_cancelled   = VALUES(total_cancelled),
        total_pending     = VALUES(total_pending),
        total_in_transit  = VALUES(total_in_transit),
        total_sales       = VALUES(total_sales),
        total_paid        = VALUES(total_paid),
        total_unpaid      = VALUES(total_unpaid),
        generated_at      = CURRENT_TIMESTAMP;
END $$
DELIMITER ;

DROP EVENT IF EXISTS generate_monthly_summary;
DELIMITER $$
CREATE EVENT generate_monthly_summary
ON SCHEDULE EVERY 1 MONTH STARTS '2026-04-01 00:00:00'
ON COMPLETION NOT PRESERVE ENABLE
DO
BEGIN
    INSERT INTO monthly_reports (
        report_month,
        total_deliveries,
        total_delivered,
        total_cancelled,
        total_pending,
        total_in_transit,
        total_sales,
        total_paid,
        total_unpaid
    )
    SELECT
        DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01'),
        COUNT(*),
        COALESCE(SUM(f.delivered_count), 0),
        COALESCE(SUM(f.cancelled_count), 0),
        COALESCE(SUM(f.pending_count), 0),
        COALESCE(SUM(f.in_transit_count), 0),
        COALESCE(SUM(f.recognized_sales), 0),
        COALESCE(SUM(f.paid_sales), 0),
        COALESCE(SUM(f.unpaid_sales), 0)
    FROM vw_report_delivery_financials f
    WHERE f.schedule_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
      AND f.schedule_date <  DATE_FORMAT(CURDATE(), '%Y-%m-01')
    ON DUPLICATE KEY UPDATE
        total_deliveries  = VALUES(total_deliveries),
        total_delivered   = VALUES(total_delivered),
        total_cancelled   = VALUES(total_cancelled),
        total_pending     = VALUES(total_pending),
        total_in_transit  = VALUES(total_in_transit),
        total_sales       = VALUES(total_sales),
        total_paid        = VALUES(total_paid),
        total_unpaid      = VALUES(total_unpaid),
        generated_at      = CURRENT_TIMESTAMP;
END $$
DELIMITER ;
