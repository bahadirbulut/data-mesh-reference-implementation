# Naming Conventions

## Purpose
Consistent naming ensures discoverability, clarity, and reduces cognitive load across the data mesh.

## Data Product Names

**Format**: `{domain}-{entity}-{aggregation_optional}`

**Rules**:
- Use lowercase with hyphens
- Be descriptive but concise
- Domain name comes first
- Avoid abbreviations unless widely known

**Examples**:
- `sales-orders-daily` ✅
- `research-experiment-runs` ✅
- `sales_orders` ❌ (use hyphens, not underscores)
- `ord` ❌ (too abbreviated)

## Table/Dataset Names

**Format**: `{entity}_{time_grain_optional}`

**Rules**:
- Use snake_case for tables
- Include time grain if aggregated (daily, weekly, monthly)
- Be explicit about what the table contains

**Examples**:
- `sales_orders_daily` ✅
- `experiment_runs` ✅
- `customer_profiles` ✅
- `data` ❌ (too vague)

## Column Names

**Format**: `{descriptor}_{type_optional}`

**Rules**:
- Use snake_case
- Be specific and self-documenting
- Add suffix for data type if needed (`_id`, `_date`, `_amount`, `_count`)
- Avoid generic names like `value`, `data`, `info`

**Examples**:
- `order_id` ✅
- `customer_email` ✅
- `total_revenue_amount` ✅
- `created_date` ✅
- `val` ❌ (unclear)

## File Names

**Format**: Depends on file type

### Data Files
`{entity}_{YYYY-MM-DD}.{extension}`

Example: `orders_2025-01-01.csv`

### Code Files
- Pipelines: `{layer}.py` (bronze.py, silver.py, gold.py)
- Utilities: `{function}.py` (validate.py, transform.py)

### Contract Files
`{entity}_v{version}.{extension}`

Examples:
- `sales_orders_v1.schema.json`
- `sales_orders_v1.contract.md`

## Storage Paths

**Format**: `{layer}/{domain}/{entity}/`

**Rules**:
- Use lowercase
- Keep hierarchy shallow (max 4 levels)
- Include partition columns in path when applicable

**Examples**:
- `bronze/sales/orders/`
- `silver/sales/orders/`
- `gold/sales/sales_orders_daily/`
- `gold/research_ops/experiment_runs_daily/`

## Version Numbers

**Format**: `v{major}`

**Rules**:
- Start at v1
- Increment major version for breaking changes
- Document breaking changes in contract

**Examples**:
- `v1` - Initial version
- `v2` - Breaking schema change
- `v1.1` ❌ (no minor versions, keep it simple)

## Prohibited Patterns

❌ Do NOT use:
- Special characters (@, #, $, %, etc.)
- Spaces in names
- Reserved keywords (select, from, where, etc.)
- Inconsistent casing (camelCase mixed with snake_case)
- Ambiguous abbreviations

## Enforcement

- Naming conventions are checked in CI/CD
- Product validation script checks product names
- Code reviews ensure compliance
- Platform team can reject non-compliant names
