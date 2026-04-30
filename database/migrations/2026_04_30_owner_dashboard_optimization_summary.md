# Owner Dashboard Query Optimization - April 30, 2026

## Purpose

This migration improves the owner dashboard by centralizing daily dashboard totals and adding an index for the recent transactions card.

The changes are additive and compatible with the existing dashboard queries.

## Database Objects Added Or Updated

### `vw_owner_dashboard_daily`

New daily summary view for owner dashboard KPIs and the weekly chart.

It groups `vw_report_delivery_financials` by `schedule_date` and returns:

```sql
schedule_date
total_deliveries
delivered_deliveries
pending_deliveries
in_transit_deliveries
cancelled_deliveries
recognized_sales
paid_sales
unpaid_sales
```

Important rule:

```sql
recognized_sales
paid_sales
unpaid_sales
```

still come from `vw_report_delivery_financials`, so cancelled and non-delivered deliveries are not counted as sales.

### `vw_dashboard_today`

Updated to read from `vw_owner_dashboard_daily`.

Existing columns were preserved:

```sql
total_today
delivered_today
pending_today
in_transit_today
cancelled_today
sales_today
```

New optional columns were added:

```sql
paid_today
unpaid_today
```

Existing admin and delivery dashboard queries remain compatible because their selected columns still exist.

### `idx_transactions_created_at_id`

New index:

```sql
CREATE INDEX idx_transactions_created_at_id
ON transactions (created_at, id);
```

Reason:

The owner dashboard recent transactions card orders by:

```sql
ORDER BY t.created_at DESC, t.id DESC
```

This index helps the database find recent transactions faster as the table grows.

## Owner Dashboard Query Changes

### Sales KPIs

Before:

The model summed directly from `vw_report_delivery_financials`.

After:

The model sums from `vw_owner_dashboard_daily` and filters the needed date range first.

This reduces repeated aggregation logic for:

```sql
total_sales_today
total_sales_this_week
total_sales_this_month
total_sales_last_month
month_sales_change_pct
total_receivables
```

### Today's Delivery Counts

Before:

The owner model read from `vw_dashboard_today`, which used `CURDATE()`.

After:

The owner model reads from `vw_owner_dashboard_daily` using a Python-supplied `today` parameter.

This keeps date logic consistent inside the owner model.

### Weekly Chart

Before:

The weekly chart joined each calendar day to `vw_report_delivery_financials`.

After:

The weekly chart joins each calendar day to `vw_owner_dashboard_daily`.

### Top Customers

Before:

Top customers were all-time.

After:

Top customers are for the current month, matching the dashboard's current-period focus.

The query still uses delivered-only recognized sales.

### Recent Transactions

The query still reads from `vw_transaction_summary` and `transactions`, but the new index supports its ordering.
