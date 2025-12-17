# Access Control Model

## Purpose
Define how access to data products is granted, managed, and audited across the data mesh.

## Principles

1. **Domain Ownership**: Domain teams control access to their data products
2. **Least Privilege**: Users get minimum access needed for their role
3. **Explicit Grants**: No implicit or inherited access
4. **Auditable**: All access requests and grants are logged
5. **Time-Bound**: Access is reviewed periodically

## Access Layers

### Layer-Based Access Control

Each layer has different access requirements:

| Layer | Purpose | Default Access | Approval Required |
|-------|---------|----------------|-------------------|
| Bronze | Raw ingestion | Domain team only | Platform team |
| Silver | Cleaned data | Domain team + read-only consumers | Domain owner |
| Gold | Data products | Consumers (via catalog) | Domain owner |

### Why Layer Restrictions?

- **Bronze**: Raw, unvalidated data; may contain errors or PII
- **Silver**: Domain-internal layer; may change frequently
- **Gold**: Published products with SLA commitments; stable for consumers

## Access Roles

### 1. Data Product Owner
**Scope**: Specific domain

**Permissions**:
- Read/write to all layers (bronze, silver, gold)
- Grant access to consumers
- Deploy pipelines
- Modify product metadata
- View audit logs

**Example**: Sales Analytics team owns `sales-orders` product

### 2. Data Consumer (Read-Only)
**Scope**: Specific data product(s)

**Permissions**:
- Read access to Gold layer only
- View contract and documentation
- Submit access requests
- Report data quality issues

**Example**: Finance team reads `sales_orders_daily` for reporting

### 3. Platform Team
**Scope**: All infrastructure

**Permissions**:
- Provision infrastructure
- Grant domain team access
- Monitor all pipelines
- Audit access logs
- Emergency read access (with logging)

**Example**: Platform engineers managing Azure resources

### 4. Data Steward
**Scope**: Cross-domain governance

**Permissions**:
- Read access to all Gold products
- Review access requests
- Audit compliance
- No write access to data

**Example**: Compliance officer reviewing PII handling

## Access Request Process

### For Consumers Requesting Access

1. **Discover** the data product in catalog
2. **Review** contract and SLA
3. **Submit** access request:
   ```
   - Data product name
   - Business justification
   - Required scope (tables/columns)
   - Time period needed
   ```
4. **Approval** from domain owner (2 business days SLA)
5. **Provisioning** via Azure AD group (automated)
6. **Notification** when access is granted
7. **Usage** tracked and audited

### For Domain Owners Granting Access

1. **Receive** access request notification
2. **Validate** business justification
3. **Check** if requester needs PII fields
4. **Approve/Deny** request
5. **Add** user to Azure AD group
6. **Notify** requester
7. **Document** in access log

## Technical Implementation

### Azure AD Groups

Each data product has dedicated Azure AD groups:

```
- dp-{domain}-{product}-owner     # Read/write to all layers
- dp-{domain}-{product}-consumer  # Read-only to Gold
```

**Example**:
- `dp-sales-orders-owner`
- `dp-sales-orders-consumer`

### ADLS Gen2 ACLs

Access Control Lists (ACLs) on storage:

```
gold/sales/sales_orders_daily/
  ├── Owner: dp-sales-orders-owner (rwx)
  └── Reader: dp-sales-orders-consumer (r-x)

silver/sales/orders/
  └── Owner: dp-sales-orders-owner (rwx)

bronze/sales/orders/
  └── Owner: dp-sales-orders-owner (rwx)
```

### Databricks Access

Unity Catalog (if enabled) or table ACLs:

```sql
-- Grant read access to Gold
GRANT SELECT ON TABLE gold.sales.sales_orders_daily 
TO `dp-sales-orders-consumer`;

-- Domain team full access
GRANT ALL PRIVILEGES ON SCHEMA silver.sales 
TO `dp-sales-orders-owner`;
```

## Access Patterns

### Self-Service Access (Recommended)

Consumers request access via:
1. Data catalog UI
2. ServiceNow/Jira ticket
3. Email to domain owner

Automated workflow:
```
Request → Approval → AD Group Update → Notification
```

### Programmatic Access

Service principals for automated pipelines:

```yaml
# Service principal for pipeline
service_principal:
  name: sp-finance-reporting
  access:
    - data_product: sales-orders-daily
      scope: read
      expiry: 2026-12-31
```

### Temporary Access

For audits or troubleshooting:

```
- Duration: Max 30 days
- Approval: Domain owner + security team
- Logging: All queries logged
- Notification: Domain owner notified of all access
```

## Access Auditing

### Audit Logs

All access is logged:

```json
{
  "timestamp": "2025-12-17T10:30:00Z",
  "user": "user@example.com",
  "data_product": "sales-orders-daily",
  "action": "SELECT",
  "rows_accessed": 1000,
  "query": "SELECT order_date, daily_revenue FROM ...",
  "ip_address": "10.0.1.5"
}
```

### Quarterly Access Review

Domain owners review all access:
- Who has access?
- Is it still needed?
- Any suspicious activity?
- Revoke unused access

### Compliance Reporting

Platform team generates monthly reports:
- Access by user
- Access by data product
- PII access logs
- Failed access attempts
- Denied requests

## Special Cases

### PII Data Access

Additional requirements for PII:
- [ ] Business justification documented
- [ ] Privacy team approval
- [ ] Data minimization applied
- [ ] Access logged separately
- [ ] Annual recertification

```yaml
privacy:
  pii: true
  pii_fields: ["customer_email", "customer_phone"]
  access_approval:
    - domain_owner
    - privacy_team
```

### Cross-Domain Access

When one domain needs another domain's data:

```
Domain A (Consumer) → Access Request → Domain B (Owner)
  ↓
Domain B reviews and approves
  ↓
Domain A granted read access to Gold
  ↓
Domain A builds on top (creates new Gold product)
```

### Emergency Access

Platform team can grant temporary emergency access:
- Triggered by: Critical incident
- Approval: VP Engineering
- Duration: Max 24 hours
- Logging: Detailed audit trail
- Post-mortem: Required

## Best Practices

✅ **Do**:
- Request minimum necessary access
- Document business justification
- Review access quarterly
- Revoke access when no longer needed
- Use service principals for automation
- Log all access for audit

❌ **Don't**:
- Share credentials
- Grant overly broad access
- Use personal accounts for pipelines
- Skip access request process
- Grant access without justification
- Forget to remove access for departed employees

## Access Denial Reasons

Valid reasons to deny access:
- Insufficient business justification
- Alternative data source available
- PII without privacy approval
- Consumer not trained on data handling
- Data quality too low for use case
- License or compliance restrictions

## Revocation

Access can be revoked:
- User leaves organization
- Project completed
- Access unused for 90 days
- Policy violation
- At domain owner discretion

**Process**:
1. Notification 7 days before revocation
2. Remove from Azure AD group
3. Update access log
4. Notify user

## Tools

- **Azure AD**: User and group management
- **ADLS Gen2**: Storage ACLs
- **Databricks**: Unity Catalog or table ACLs
- **Azure Monitor**: Access logging
- **ServiceNow/Jira**: Access request workflow
- **Data Catalog**: Self-service discovery

## Support

For access issues:
- Domain-specific: Contact domain owner (in product.yaml)
- Platform issues: platform-team@example.com
- Policy questions: data-governance@example.com
