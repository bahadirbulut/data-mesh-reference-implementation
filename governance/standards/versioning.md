# Versioning Strategy

## Purpose
Versioning ensures backward compatibility, enables safe evolution, and provides clear communication about breaking changes.

## Principles

1. **Consumer-Driven**: Version changes are driven by consumer impact
2. **Explicit**: Version is always explicit in contracts and schemas
3. **Immutable**: Once published, a version cannot be modified
4. **Backward Compatible**: Minor changes should not break consumers

## Version Format

**Format**: `v{major}`

We use simple major versioning only:
- **v1** - Initial version
- **v2** - Breaking change
- **v3** - Another breaking change

**Why simple versioning?**
- Easier to understand and communicate
- Reduces complexity in data mesh
- Clear signal: new major version = review your code
- No semantic versioning overhead (no minor/patch)

## What Requires a New Version?

### Breaking Changes (New Major Version Required)

✅ **Schema Changes**:
- Removing a column
- Renaming a column
- Changing column data type
- Changing column constraints (nullable → required)
- Removing a required field

✅ **Data Changes**:
- Changing data format (CSV → Parquet)
- Changing aggregation logic
- Changing business rules
- Dropping historical data

✅ **Contract Changes**:
- Changing SLA (stricter freshness/availability)
- Changing access requirements
- Deprecating the product

### Non-Breaking Changes (No New Version)

❌ These do NOT require a new version:
- Adding optional columns
- Improving data quality
- Adding documentation
- Fixing bugs that correct incorrect behavior
- Performance improvements
- Internal implementation changes

## Version Lifecycle

### 1. Development Phase
- Version is `v1-draft` or `v2-draft`
- Not yet published to consumers
- Can change freely

### 2. Active Phase
- Version is published (e.g., `v1`)
- Consumers depend on it
- Must remain stable and backward compatible
- SLA commitments apply

### 3. Deprecated Phase
- New version released (e.g., `v2`)
- Old version marked deprecated
- Deprecation notice: minimum 90 days
- Consumers should migrate

### 4. Retired Phase
- Old version no longer maintained
- Data still available (archived)
- No SLA guarantees
- Documentation updated

## Version Transition Process

### Announcing a New Version

1. **Create new version files**:
   - `{entity}_v2.schema.json`
   - `{entity}_v2.contract.md`

2. **Document breaking changes**:
   - What changed and why
   - Migration guide for consumers
   - Timeline for deprecation

3. **Update product.yaml**:
   ```yaml
   outputs:
     - name: sales_orders_daily_v1
       version: v1
       deprecated: true
       deprecation_date: "2025-03-01"
       end_of_life: "2025-06-01"
     
     - name: sales_orders_daily_v2
       version: v2
       status: active
   ```

4. **Notify consumers**:
   - Email to all known consumers
   - Update documentation
   - Post in data catalog

### Supporting Multiple Versions

Both versions can run in parallel during transition:

```
gold/
  sales/
    sales_orders_daily_v1/  # Deprecated, runs until EOL
    sales_orders_daily_v2/  # New version, active
```

## Deprecation Policy

### Timeline
- **T+0**: Announce new version, deprecate old version
- **T+30 days**: Reminder to all consumers
- **T+60 days**: Final warning
- **T+90 days**: Old version retired (minimum)

### Extension
- Can extend deprecation if critical consumers need more time
- Maximum extension: 90 additional days
- Must have documented migration plan

### Emergency Breaking Changes
In rare cases (security, compliance, data quality):
- Notify immediately
- Provide 30-day minimum notice
- Offer migration support
- Document incident

## Versioning in File Names

### Schema Files
- `sales_orders_v1.schema.json`
- `sales_orders_v2.schema.json`

### Contract Files
- `sales_orders_v1.contract.md`
- `sales_orders_v2.contract.md`

### Data Paths
Include version in path for clarity:
- `gold/sales/sales_orders_daily_v1/`
- `gold/sales/sales_orders_daily_v2/`

## Version Registry

Maintain a central registry (product.yaml) with:
- All active versions
- Deprecated versions with EOL dates
- Version history and change log

## Best Practices

✅ **Do**:
- Version your schema from day one
- Document all breaking changes
- Give consumers time to migrate
- Test both versions during transition
- Archive old data for compliance

❌ **Don't**:
- Change published versions in-place
- Rush deprecation timelines
- Break compatibility without warning
- Use ambiguous version numbers
- Delete old versions without notice

## Examples

### Example 1: Adding Optional Column (No Version Change)

**v1 Schema** (current):
```json
{
  "properties": {
    "order_date": { "type": "string" },
    "daily_revenue": { "type": "number" }
  }
}
```

**v1 Schema** (updated, same version):
```json
{
  "properties": {
    "order_date": { "type": "string" },
    "daily_revenue": { "type": "number" },
    "order_count": { "type": "number" }  // Added, optional
  }
}
```

✅ No version change needed - added optional field

### Example 2: Removing Column (Version Change Required)

**v1 → v2** (breaking change):

v1 had `currency` field, v2 removes it:

```yaml
# product.yaml
outputs:
  - name: sales_orders_daily
    version: v2
    breaking_changes:
      - "Removed 'currency' field (always EUR)"
    migration_guide: "Update queries to remove currency filter"
```

## Enforcement

- Version consistency checked in CI/CD
- Schema validation enforces version format
- Code reviews verify version changes
- Product validation ensures version in product.yaml matches schema files
