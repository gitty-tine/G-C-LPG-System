-- 2026-04-30 Owner dashboard query optimization
-- Goal: centralize owner dashboard daily aggregates and speed recent transactions.

-- 1) One-row-per-day owner dashboard source.
--    This keeps dashboard KPI/chart queries from repeating daily SUM logic.
CREATE OR REPLACE VIEW vw_owner_dashboard_daily AS
SELECT
    f.schedule_date,
    COUNT(*)                                           AS total_deliveries,
    COALESCE(SUM(f.delivered_count), 0)                AS delivered_deliveries,
    COALESCE(SUM(f.pending_count), 0)                  AS pending_deliveries,
    COALESCE(SUM(f.in_transit_count), 0)               AS in_transit_deliveries,
    COALESCE(SUM(f.cancelled_count), 0)                AS cancelled_deliveries,
    ROUND(COALESCE(SUM(f.recognized_sales), 0), 2)     AS recognized_sales,
    ROUND(COALESCE(SUM(f.paid_sales), 0), 2)           AS paid_sales,
    ROUND(COALESCE(SUM(f.unpaid_sales), 0), 2)         AS unpaid_sales
FROM vw_report_delivery_financials f
GROUP BY f.schedule_date;

-- 2) Keep the shared today dashboard view compatible with existing screens,
--    while exposing paid/unpaid sales for screens that need them later.
CREATE OR REPLACE VIEW vw_dashboard_today AS
SELECT
    COALESCE(SUM(total_deliveries), 0)                 AS total_today,
    COALESCE(SUM(delivered_deliveries), 0)             AS delivered_today,
    COALESCE(SUM(pending_deliveries), 0)               AS pending_today,
    COALESCE(SUM(in_transit_deliveries), 0)            AS in_transit_today,
    COALESCE(SUM(cancelled_deliveries), 0)             AS cancelled_today,
    ROUND(COALESCE(SUM(recognized_sales), 0), 2)       AS sales_today,
    ROUND(COALESCE(SUM(paid_sales), 0), 2)             AS paid_today,
    ROUND(COALESCE(SUM(unpaid_sales), 0), 2)           AS unpaid_today
FROM vw_owner_dashboard_daily
WHERE schedule_date = CURDATE();

-- 3) Speed the owner dashboard recent transactions card.
--    Idempotent index creation for MySQL versions without CREATE INDEX IF NOT EXISTS.
SET @idx_exists := (
    SELECT COUNT(1)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'transactions'
      AND INDEX_NAME = 'idx_transactions_created_at_id'
);

SET @idx_sql := IF(
    @idx_exists = 0,
    'CREATE INDEX idx_transactions_created_at_id ON transactions (created_at, id)',
    'SELECT ''idx_transactions_created_at_id already exists'' AS info'
);

PREPARE idx_stmt FROM @idx_sql;
EXECUTE idx_stmt;
DEALLOCATE PREPARE idx_stmt;
