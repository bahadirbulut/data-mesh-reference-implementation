# Contract: sales_orders_daily (v1)

## Purpose
Daily revenue totals for reporting and analytics.

## Schema
See `sales_orders_v1.schema.json`.

## SLA
- Freshness: daily @ 01:00 (Europe/Brussels)
- Availability: 99.5%

## Quality rules
- No missing order_date
- daily_revenue >= 0
