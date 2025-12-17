# Sales Domain

## Overview
The Sales domain owns all order-related data products. It provides daily revenue metrics and order analytics to support business reporting, forecasting, and operational decision-making.

## Data Products

### Sales Orders Daily
- **Purpose**: Aggregated daily revenue for reporting and analytics
- **Consumers**: Finance team, Sales leadership, BI dashboards
- **Refresh**: Daily at 01:00 Europe/Brussels timezone
- **Owner**: Sales Analytics Team (sales-analytics@example.com)

## Data Flow

```
Operational System → CSV Export → Bronze (raw) → Silver (cleaned) → Gold (aggregated)
```

### Bronze Layer
- **Path**: `bronze/sales/orders/`
- **Format**: CSV (raw files from operational system)
- **Partitioning**: By ingestion date
- **Retention**: 90 days
- **Content**: Raw order data as received from source

### Silver Layer
- **Path**: `silver/sales/orders/`
- **Format**: Delta
- **Transformations**:
  - Remove duplicate order_id
  - Convert date strings to proper date types
  - Clean text fields (trim whitespace)
  - Validate quantity > 0 and unit_price >= 0
  - Filter out null order_id
- **Retention**: 2 years

### Gold Layer
- **Path**: `gold/sales/sales_orders_daily/`
- **Format**: Delta
- **Transformations**:
  - Calculate revenue: quantity * unit_price
  - Aggregate by order_date
  - Sum daily_revenue
- **Retention**: Indefinite (with archival)

## Schema

See [contracts/sales_orders_v1.schema.json](contracts/sales_orders_v1.schema.json)

## SLA

- **Freshness**: daily 01:00 Europe/Brussels
- **Availability**: 99.5%
- **Support**: business-hours (Mon-Fri 9AM-5PM CET)

## Quality Checks

- `order_id` is unique in silver layer
- `quantity` > 0
- `unit_price` >= 0
- No missing `order_date`
- `daily_revenue` >= 0

## Access

To request access to this data product:
1. Submit request via email to sales-analytics@example.com
2. Include business justification and use case
3. Approval from Sales Analytics team
4. Access granted within 2 business days

## Known Issues

- None

## Changelog

### v1 - 2025-01-01
- Initial release
- Daily revenue aggregation
- CSV source integration
