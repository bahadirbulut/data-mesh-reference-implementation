# PII (Personal Identifiable Information) Policy

## Purpose
Define requirements for handling Personal Identifiable Information (PII) across all data products in the mesh to ensure GDPR compliance and data privacy.

## Scope
This policy applies to:
- All data products containing PII
- All domain teams processing personal data
- All consumers accessing PII data
- Platform infrastructure storing PII

## What is PII?

### Direct Identifiers (High Risk)
Information that directly identifies an individual:
- Full name
- Email address
- Phone number
- National ID number
- Passport number
- Social security number
- IP address (in some contexts)
- Biometric data
- Government-issued IDs

### Indirect Identifiers (Medium Risk)
Information that can identify someone when combined:
- Date of birth + ZIP code
- Job title + company + location
- Demographic combinations (age, gender, location)
- Device IDs + usage patterns
- Transaction patterns

### Not PII (Low Risk)
Aggregated or anonymized data where individuals cannot be re-identified:
- Aggregated statistics (counts, averages)
- Properly anonymized datasets
- Synthetic data
- Public data from official sources

## PII Classification

| Classification | Examples | Requirements |
|----------------|----------|--------------|
| **Sensitive PII** | Health data, biometrics, financial data, political opinions | High security, encryption, strict access |
| **Standard PII** | Name, email, phone, address | Encryption, access controls, audit logs |
| **Pseudonymized** | Hashed/tokenized PII | Access controls, key management |
| **Anonymized** | Irreversibly de-identified data | Standard security controls |

## Requirements by Layer

### Bronze Layer (Raw Data)
If PII exists in source:
- ✅ Encrypt at rest (default via ADLS Gen2)
- ✅ Encrypt in transit (HTTPS/TLS)
- ✅ Access restricted to domain team only
- ✅ Retention: Max 90 days
- ✅ Mark as containing PII in product.yaml

```yaml
privacy:
  pii: true
  pii_fields: ["customer_email", "customer_phone", "customer_name"]
  bronze_retention_days: 90
```

### Silver Layer (Cleaned Data)
**Options**:

1. **Retain PII** (if required for business logic):
   - Access restricted to domain team
   - Encryption at rest
   - Audit all access
   - Document justification

2. **Pseudonymize** (recommended):
   ```python
   from hashlib import sha256
   
   # One-way hash for pseudonymization
   df = df.withColumn(
       "customer_id_hash",
       sha256(col("customer_email"))
   ).drop("customer_email")
   ```

3. **Tokenize** (for reversible pseudonymization):
   - Use Azure Key Vault for token mapping
   - Store tokens separately from data
   - Require additional approval to de-tokenize

### Gold Layer (Data Products)
**Default**: No PII in Gold products

**If PII is required**:
- Explicit approval from Privacy Team
- Consumer training required
- Enhanced audit logging
- Annual access recertification

```yaml
outputs:
  - name: customer_profiles
    layer: gold
    privacy:
      pii: true
      pii_fields: ["email_hash"]  # Pseudonymized
      approval_required: privacy_team
      consumer_training: required
```

## Data Minimization

### Principle
Collect and retain only PII that is **necessary** for the stated purpose.

### Application
- ❌ Don't copy full customer profiles if you only need aggregates
- ❌ Don't retain email addresses if customer_id is sufficient
- ✅ Drop PII fields in Silver if not needed for Gold
- ✅ Use aggregation to eliminate individual identifiers
- ✅ Apply pseudonymization when possible

### Example
```python
# Bad: Keeping unnecessary PII
df_gold = df_silver.select("customer_name", "total_orders")

# Good: Use pseudonymized ID
df_gold = df_silver.select("customer_id_hash", "total_orders")

# Better: Aggregate to remove individuals
df_gold = df_silver.groupBy("region").agg(sum("total_orders"))
```

## Pseudonymization Techniques

### 1. One-Way Hashing
Use for non-reversible pseudonymization:

```python
from pyspark.sql.functions import sha2

df = df.withColumn(
    "email_hash",
    sha2(col("email"), 256)  # SHA-256 hash
).drop("email")
```

**Pros**: Irreversible, consistent
**Cons**: Cannot recover original value

### 2. Tokenization
Use for reversible pseudonymization:

```python
# Store mapping in Azure Key Vault or separate secure DB
token = generate_token(email)
df = df.withColumn("email_token", lit(token)).drop("email")
```

**Pros**: Reversible with key
**Cons**: Key management complexity

### 3. Masking
Partial masking for display:

```python
# Email: user@example.com → u***@example.com
# Phone: +32 123 456 789 → +32 *** *** 789
```

**Use case**: UI display, logging

## Access Controls for PII

### Additional Requirements
1. **Business justification** documented
2. **Privacy team approval** required
3. **Consumer training** completed
4. **Enhanced audit logging** enabled
5. **Annual recertification** required

### Access Request Template
```
Data Product: {name}
PII Fields Requested: {list}
Business Justification: {why is PII needed?}
Alternatives Considered: {what non-PII options explored?}
Data Minimization: {how will you minimize PII exposure?}
Retention Period: {how long will you keep the data?}
Privacy Training: {completed? certificate}
```

### Approval Workflow
```
Consumer Request
  ↓
Domain Owner Review
  ↓
Privacy Team Approval ← Required for PII
  ↓
Access Granted
  ↓
Enhanced Audit Logging Enabled
```

## Audit & Logging

### Enhanced Logging for PII
Log all access to PII fields:

```json
{
  "timestamp": "2025-12-17T10:30:00Z",
  "user": "analyst@example.com",
  "data_product": "customer-profiles",
  "pii_fields_accessed": ["email_hash", "phone_masked"],
  "action": "SELECT",
  "rows_accessed": 100,
  "query": "SELECT email_hash, phone_masked FROM ...",
  "ip_address": "10.0.1.5",
  "business_justification": "Marketing campaign analysis"
}
```

### Retention of Audit Logs
- PII access logs: **7 years** (GDPR requirement)
- Regular access logs: 2 years

### Monitoring
Alert on:
- Unusual volume of PII access
- Access outside business hours
- New users accessing PII
- Failed access attempts

## Retention & Deletion

### Retention Limits
| Layer | Default Retention | PII Retention |
|-------|------------------|---------------|
| Bronze | 90 days | 30 days |
| Silver | 2 years | 1 year |
| Gold | Indefinite | Based on legal requirements |

### Right to Erasure (GDPR Article 17)
Process for deleting individual's data:

1. **Request received** (via privacy team)
2. **Identify data locations** (all domains)
3. **Delete from all layers** (bronze, silver, gold)
4. **Delete from backups** (or mark for exclusion)
5. **Confirm deletion** (within 30 days)
6. **Log deletion** (audit trail)

### Deletion Script Example
```python
# Delete individual from all layers
customer_id = "customer_123"

# Bronze
delete_from_bronze(customer_id)

# Silver
spark.sql(f"""
  DELETE FROM silver.sales.orders 
  WHERE customer_id = '{customer_id}'
""")

# Gold
spark.sql(f"""
  DELETE FROM gold.sales.sales_orders_daily 
  WHERE customer_id_hash = hash('{customer_id}')
""")

log_deletion(customer_id, timestamp, requester)
```

## Data Breach Response

### If PII is compromised:

1. **Immediate Actions** (within 1 hour):
   - Revoke all access to affected data product
   - Isolate affected storage
   - Notify security team

2. **Assessment** (within 24 hours):
   - Determine scope of breach
   - Identify affected individuals
   - Assess risk level

3. **Notification** (within 72 hours):
   - Notify privacy team
   - Notify affected individuals (if high risk)
   - Report to data protection authority (GDPR requirement)

4. **Remediation**:
   - Fix security gap
   - Review access controls
   - Conduct post-mortem
   - Update policies

## PII in Product Metadata

### Mark PII in product.yaml
```yaml
name: customer-profiles
domain: sales

privacy:
  pii: true
  pii_classification: standard  # standard | sensitive
  pii_fields:
    - name: email_hash
      type: pseudonymized
      original_field: email
      method: sha256
    - name: phone_masked
      type: masked
      original_field: phone
      method: partial_mask
  
  legal_basis: legitimate_interest  # consent | contract | legal_obligation | legitimate_interest
  retention_period: "1 year"
  deletion_process: "automated_30_days"
```

## Training Requirements

### For Domain Teams
- GDPR fundamentals
- PII identification
- Pseudonymization techniques
- Data minimization
- Breach response

### For Consumers
- PII handling best practices
- Access restrictions
- Reporting incidents
- Data retention rules

**Certification**: Required before accessing PII

## Best Practices

✅ **Do**:
- Minimize PII in data products
- Use pseudonymization when possible
- Encrypt PII at rest and in transit
- Log all PII access
- Review PII access quarterly
- Document legal basis for processing
- Train all users handling PII
- Implement automated retention policies

❌ **Don't**:
- Copy PII unnecessarily
- Share PII in logs or error messages
- Store PII in non-encrypted storage
- Grant PII access without justification
- Forget to delete PII when required
- Mix PII with non-PII without marking
- Skip privacy team approval
- Use PII in test environments

## Compliance Checklist

For each data product with PII:

- [ ] PII marked in product.yaml
- [ ] PII fields documented
- [ ] Data minimization applied
- [ ] Pseudonymization implemented (if applicable)
- [ ] Access controls configured
- [ ] Enhanced audit logging enabled
- [ ] Privacy team approval obtained
- [ ] Consumer training completed
- [ ] Retention policy defined
- [ ] Deletion process documented
- [ ] Breach response plan exists

## Tools

- **Azure Key Vault**: Token/key storage
- **Azure Purview** (optional): PII discovery and cataloging
- **ADLS Gen2**: Encryption at rest
- **Azure Monitor**: Enhanced audit logging
- **Microsoft Compliance Manager**: GDPR compliance tracking

## Support

- Privacy questions: privacy-team@example.com
- Technical implementation: platform-team@example.com
- Policy exceptions: data-governance@example.com

## References

- GDPR: https://gdpr.eu/
- Azure data protection: https://docs.microsoft.com/azure/compliance/
- Data minimization: https://ico.org.uk/for-organisations/data-protection-principles/
