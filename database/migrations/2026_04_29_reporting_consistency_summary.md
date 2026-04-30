# Reporting Consistency Migration Summary

Date applied: April 29, 2026

## Main Rule

Sales are now recognized only when a delivery status is `delivered`.

Cancelled, pending, and in-transit deliveries can still appear in reports, but their amounts are not counted in:

- total sales
- total paid
- total unpaid
- dashboard sales
- product revenue
- customer spending
- period comparisons

## Database Objects Added

### `vw_report_delivery_financials`

One row per delivery. This is now the main source of truth for report and dashboard totals.

Important computed columns:

- `gross_amount`: transaction amount if available, otherwise computed delivery item total
- `recognized_sales`: amount counted only when `delivery_status = 'delivered'`
- `paid_sales`: delivered sales with `payment_status = 'paid'`
- `unpaid_sales`: delivered sales with `payment_status = 'unpaid'`
- `report_payment_status`: `paid`, `unpaid`, or `not_applicable` for non-delivered deliveries
- status count columns: `delivered_count`, `cancelled_count`, `pending_count`, `in_transit_count`

### `vw_report_delivery_lines`

One row per delivery item/product line. Used for detailed report breakdowns and product revenue reports.

Important computed columns:

- `line_amount`
- `recognized_line_sales`, counted only when the delivery is delivered

## Database Objects Updated

### `vw_dashboard_today`

Changed from summing paid transaction rows directly to using `vw_report_delivery_financials`.

Fixed rule:

```sql
COALESCE(SUM(recognized_sales), 0) AS sales_today
```

### `sp_get_delivery_report`

Changed to read from `vw_report_delivery_financials`.

Cancelled deliveries now show `payment_status = 'not_applicable'` instead of looking unpaid.

### `sp_get_sales_summary`

Changed from summing all transaction amounts to summing only delivered sales.

Fixed rule:

```sql
COALESCE(SUM(f.recognized_sales), 0) AS total_sales
COALESCE(SUM(f.paid_sales), 0) AS paid_sales
COALESCE(SUM(f.unpaid_sales), 0) AS unpaid_sales
```

### `sp_update_delivery_status`

Added status validation and transition rules:

- `pending` can move to `in_transit`, `delivered`, or `cancelled`
- `in_transit` can move to `delivered` or `cancelled`
- `cancelled` cannot be changed
- `delivered` can only be cancelled if it has no paid transaction
- paid deliveries cannot be cancelled
- unpaid transaction rows are deleted when a delivery moves to a non-delivered status

## Snapshot Tables Updated

Added these columns to:

- `daily_reports`
- `weekly_reports`
- `monthly_reports`

New columns:

```sql
total_in_transit INT NOT NULL DEFAULT 0
total_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00
total_unpaid DECIMAL(10,2) NOT NULL DEFAULT 0.00
```

Historical snapshot rows were backfilled from `vw_report_delivery_financials`.

## Events Updated

Updated these scheduled events:

- `generate_daily_summary`
- `generate_weekly_summary`
- `generate_monthly_summary`

They now populate snapshot tables using:

```sql
recognized_sales
paid_sales
unpaid_sales
in_transit_count
```

instead of raw transaction totals.

## Indexes Added

```sql
CREATE INDEX idx_deliveries_status_date
ON deliveries (status, schedule_date, id);
```

```sql
CREATE INDEX idx_delivery_items_product_delivery
ON delivery_items (product_id, delivery_id);
```

## Application Queries Updated

### `models/report_model.py`

Changed report queries to use:

- `vw_report_delivery_financials`
- `vw_report_delivery_lines`

This affects:

- report summary
- detailed breakdown
- daily/weekly/monthly snapshot summaries
- top customers
- sales by product
- period comparison

### `controllers/report_controller.py`

Snapshot summaries are now used only when the expected snapshot rows exist. If snapshots are missing, the controller falls back to live report data.

### `views/report_view.py`

Report card wording changed from "All paid transactions" to "Delivered sales".

PDF/Excel/generated summaries count only delivered rows for:

- total sales
- total paid
- total unpaid

### `models/owner_dashboard_model.py`

Owner dashboard sales KPIs, weekly chart, and top customers now use `vw_report_delivery_financials`.

## Validation Result

Validation on April 29, 2026 showed:

```text
total_deliveries: 4
total_delivered: 3
total_cancelled: 1
total_sales: 8650.00
total_paid: 8650.00
total_unpaid: 0.00
```

The cancelled delivery remained visible in the report, but it was not counted as sales.
