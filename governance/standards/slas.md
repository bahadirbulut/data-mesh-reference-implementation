# Service Level Agreements (SLAs)

## Purpose
SLAs define the quality commitments that data product owners make to their consumers. They establish trust and accountability in the data mesh.

## SLA Dimensions

Every data product must define SLAs across these dimensions:

### 1. Freshness
**Definition**: How quickly data is updated after source system changes

**Levels**:
- **Real-time**: < 5 minutes
- **Near real-time**: < 1 hour
- **Hourly**: Updated every hour
- **Daily**: Updated once per day at specified time
- **Weekly**: Updated once per week
- **Monthly**: Updated once per month

**Format**:
```yaml
sla:
  freshness: "daily 01:00 Europe/Brussels"
```

**Examples**:
- `"real-time (< 5min)"` - Streaming data
- `"daily 01:00 UTC"` - Daily batch
- `"weekly Sunday 02:00 Europe/Brussels"` - Weekly refresh

### 2. Availability
**Definition**: Percentage of time the data product is accessible and queryable

**Levels**:
- **Critical**: 99.9% (max 8.76 hours downtime/year)
- **High**: 99.5% (max 43.8 hours downtime/year)
- **Standard**: 99.0% (max 87.6 hours downtime/year)
- **Low**: 95.0% (max 438 hours downtime/year)

**Format**:
```yaml
sla:
  availability: "99.5%"
```

**Exclusions**:
- Planned maintenance (communicated 7 days in advance)
- Platform-level outages (Azure downtime)
- Force majeure events

### 3. Completeness
**Definition**: Percentage of expected records that are present

**Minimum**: 99% (max 1% missing records)

**Format**:
```yaml
quality:
  completeness: "99%"
```

**Measurement**:
- Compare row count with source system
- Check for required fields
- Validate time range coverage

### 4. Accuracy
**Definition**: Correctness of data values according to business rules

**Format**:
```yaml
quality:
  expectations:
    - "order_id is unique"
    - "quantity > 0"
    - "unit_price >= 0"
```

**Measurement**:
- Run data quality checks
- Compare with source system samples
- Business rule validation

### 5. Support Hours
**Definition**: When the domain team is available to address issues

**Options**:
- **24/7**: Always available (critical products)
- **Business hours**: Mon-Fri 9AM-5PM local time
- **Best effort**: No guaranteed response time

**Format**:
```yaml
sla:
  support_hours: "business-hours"
```

## SLA Template

```yaml
sla:
  freshness: "daily 01:00 Europe/Brussels"
  availability: "99.5%"
  support_hours: "business-hours"
  response_time:
    critical: "1 hour"
    high: "4 hours"
    normal: "1 business day"

quality:
  completeness: "99%"
  accuracy: "99.9%"
  expectations:
    - "{field} is unique"
    - "{field} is not null"
    - "{condition}"
```

## Measurement & Monitoring

### Freshness Monitoring
```python
# Check last update time
last_update = get_last_modified_time(gold_path)
expected_time = datetime.now().replace(hour=1, minute=0)
is_fresh = last_update >= expected_time
```

### Availability Monitoring
- Track query success rate
- Monitor storage availability
- Alert on access failures
- Calculate monthly uptime percentage

### Quality Monitoring
```python
# Great Expectations, dbt tests, or custom checks
expectations = [
    expect_column_values_to_be_unique("order_id"),
    expect_column_values_to_be_between("quantity", 1, 10000),
]
```

## SLA Breach Handling

### Severity Levels

**P0 - Critical**:
- Data completely unavailable
- Breach affects business decisions
- Response time: 1 hour
- Resolution time: 4 hours

**P1 - High**:
- Freshness SLA missed by >50%
- Availability < 95%
- Response time: 4 hours
- Resolution time: 1 business day

**P2 - Normal**:
- Minor freshness delay
- Quality issues in small subset
- Response time: 1 business day
- Resolution time: 3 business days

### Incident Process

1. **Detection**: Automated monitoring alerts
2. **Notification**: Email/Slack to domain team
3. **Triage**: Assess severity and impact
4. **Communication**: Update status page
5. **Resolution**: Fix root cause
6. **Post-mortem**: Document learnings

### Escalation Path

```
Level 1: Domain Team (data product owner)
   ↓ (if not resolved in SLA time)
Level 2: Domain Lead + Platform Team
   ↓ (if not resolved)
Level 3: Engineering Management
```

## SLA Reporting

### Weekly Report
- Freshness: % of on-time updates
- Availability: Uptime percentage
- Quality: % of passed checks
- Incidents: Count by severity

### Monthly Review
- SLA achievement trends
- Breach analysis
- Consumer satisfaction
- Improvement actions

### Dashboard Metrics
```
┌─────────────────────────────────────┐
│ Sales Orders Daily - SLA Status     │
├─────────────────────────────────────┤
│ Freshness:    ✅ 100% (30/30 days)  │
│ Availability: ✅ 99.7%              │
│ Quality:      ⚠️  98.5% (1 breach)  │
│ Last Update:  2025-12-17 01:05 CET  │
└─────────────────────────────────────┘
```

## SLA Commitments by Domain

### Sales Domain
```yaml
product: sales-orders-daily
sla:
  freshness: "daily 01:00 Europe/Brussels"
  availability: "99.5%"
  support_hours: "business-hours"
```

### Research Ops Domain
```yaml
product: research-experiments-daily
sla:
  freshness: "daily 02:00 Europe/Brussels"
  availability: "99.5%"
  support_hours: "business-hours"
```

## Changing SLAs

### Making SLAs Stricter
- **Version change**: ❌ No (improvement, not breaking)
- **Notice period**: 30 days recommended
- **Consumer impact**: Positive

### Making SLAs Looser
- **Version change**: ✅ Yes (breaking change)
- **Notice period**: 90 days required
- **Consumer impact**: May break consumer assumptions

## Best Practices

✅ **Do**:
- Start with achievable SLAs
- Monitor continuously
- Communicate breaches proactively
- Improve SLAs over time
- Document all incidents

❌ **Don't**:
- Overpromise on SLAs
- Ignore small breaches
- Change SLAs without notice
- Skip post-mortems
- Hide quality issues

## Tooling

### Monitoring Stack
- **Azure Monitor**: Availability tracking
- **Log Analytics**: Freshness queries
- **Great Expectations**: Quality checks
- **Databricks Jobs**: Pipeline monitoring
- **Custom Dashboards**: SLA visualization

### Alerting
```python
# Example: Alert on freshness SLA breach
if hours_since_update > 3:
    send_alert(
        severity="P1",
        message=f"Sales orders {hours_since_update}h late",
        team="sales-analytics@example.com"
    )
```

## Compliance

- SLAs are contractual commitments
- Measured and reported monthly
- Consumer feedback collected quarterly
- SLA achievements affect domain team OKRs
- Platform team reviews all SLA breaches
