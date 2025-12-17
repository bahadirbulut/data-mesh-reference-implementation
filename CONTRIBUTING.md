# Contributing to Data Mesh Reference Implementation

## Getting Started

Thank you for your interest in contributing to this Data Mesh reference implementation! This guide will help you add new data products or improve existing ones.

## Prerequisites

- Understanding of Data Mesh principles
- Familiarity with Azure Databricks and PySpark
- Knowledge of medallion architecture (Bronze → Silver → Gold)
- Review of `/governance/standards/` documentation

## Adding a New Domain

1. **Create domain structure**:
   ```bash
   mkdir -p domains/{domain_name}/{contracts,pipelines,sample_data}
   ```

2. **Copy template files**:
   - Use `/governance/standards/data-product-template.md` as reference
   - Create `product.yaml`
   - Create domain `README.md`

3. **Define data contract**:
   - Create `contracts/{entity}_v1.schema.json` (JSON Schema format)
   - Create `contracts/{entity}_v1.contract.md` (human-readable contract)

4. **Implement pipelines**:
   - `pipelines/bronze.py` - Raw data ingestion
   - `pipelines/silver.py` - Data cleaning and validation
   - `pipelines/gold.py` - Business logic and aggregations

5. **Add sample data**:
   - Create `sample_data/{entity}_YYYY-MM-DD.csv`

6. **Update main README**:
   - Add your domain to the domains list

## Governance Compliance

All pull requests must pass automated governance checks:

### 1. Product Validation
Ensures `product.yaml` contains:
- [ ] `name` field
- [ ] `domain` field
- [ ] `owner` with team and email
- [ ] `outputs` with contract references
- [ ] `sla` commitments
- [ ] `privacy` declarations

**Run locally**:
```bash
python governance/checks/validate_products.py
```

### 2. Schema Validation
Ensures:
- [ ] Schema files exist for all outputs
- [ ] Schemas are valid JSON
- [ ] Schemas follow JSON Schema standard

**Run locally**:
```bash
python governance/checks/validate_schemas.py
```

### 3. Python Linting
Ensures code quality:
```bash
pip install flake8
find domains -name "*.py" | xargs flake8 --max-line-length=120
```

## Standards to Follow

### Naming Conventions
See [governance/standards/naming.md](governance/standards/naming.md)

- Data products: `{domain}-{entity}` (e.g., `sales-orders`)
- Tables: `{entity}_{time_grain}` (e.g., `sales_orders_daily`)
- Columns: `snake_case` (e.g., `order_date`, `daily_revenue`)

### Versioning
See [governance/standards/versioning.md](governance/standards/versioning.md)

- Start at `v1`
- Increment for breaking changes only
- Support old version during transition (90 days minimum)

### SLAs
See [governance/standards/slas.md](governance/standards/slas.md)

Commit to realistic SLAs:
- **Freshness**: When data will be updated
- **Availability**: Uptime percentage
- **Support**: When your team is available

## Code Quality

### Python Best Practices

1. **Use PySpark idiomatically**:
   ```python
   # Good
   df.filter(col("quantity") > 0)
   
   # Avoid
   df.filter("quantity > 0")
   ```

2. **Add quality checks**:
   ```python
   assert df.filter(col("id").isNull()).count() == 0, "Null IDs found"
   ```

3. **Use clear variable names**:
   ```python
   # Good
   bronze_path = "abfss://bronze@storage.dfs.core.windows.net/..."
   
   # Avoid
   bp = "abfss://bronze@storage.dfs.core.windows.net/..."
   ```

4. **Add comments for complex logic**:
   ```python
   # Calculate success rate: successful trials / total trials
   .withColumn("success_rate", col("successful") / col("total"))
   ```

### Schema Best Practices

1. **Be explicit**:
   ```json
   {
     "type": "string",
     "description": "Order date in YYYY-MM-DD format",
     "format": "date",
     "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
   }
   ```

2. **Set constraints**:
   ```json
   {
     "type": "number",
     "minimum": 0,
     "maximum": 1
   }
   ```

3. **Use `required` array**:
   ```json
   "required": ["order_date", "daily_revenue"]
   ```

4. **Disable additional properties** (for strict contracts):
   ```json
   "additionalProperties": false
   ```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b add-{domain}-domain
   ```

2. **Make your changes**:
   - Follow templates and standards
   - Test locally if possible
   - Run governance checks

3. **Commit with clear messages**:
   ```bash
   git commit -m "Add marketing domain with campaign data product"
   ```

4. **Push and create PR**:
   ```bash
   git push origin add-{domain}-domain
   ```

5. **PR description should include**:
   - What domain/product you're adding
   - Business use case
   - Any special considerations
   - Checklist confirming standards compliance

6. **Wait for reviews**:
   - Automated governance checks will run
   - Platform team will review
   - Address feedback

7. **Merge**:
   - Requires approval from platform team
   - All checks must pass

## Review Criteria

Platform team will check:
- [ ] Follows governance standards
- [ ] Clear business value
- [ ] Complete documentation
- [ ] Working pipelines (code review)
- [ ] Valid schemas
- [ ] Realistic SLAs
- [ ] Proper PII handling (if applicable)

## Getting Help

- **Questions**: Open a GitHub issue
- **Platform issues**: platform-team@example.com
- **Governance**: data-governance@example.com
- **Examples**: See existing domains in `/domains/`

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Collaborate, don't compete
- Assume good intent
- Help others learn

## Testing Your Changes Locally

Since this is a reference implementation without live infrastructure:

1. **Validate files exist**:
   ```bash
   ls -la domains/{your_domain}/
   ```

2. **Check YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('domains/{domain}/product.yaml'))"
   ```

3. **Validate JSON schema**:
   ```bash
   python -c "import json; json.load(open('domains/{domain}/contracts/{entity}_v1.schema.json'))"
   ```

4. **Run governance checks**:
   ```bash
   python governance/checks/validate_products.py
   python governance/checks/validate_schemas.py
   ```

5. **Lint Python code**:
   ```bash
   flake8 domains/{domain}/pipelines/ --max-line-length=120
   ```

## Common Issues

### Issue: Product validation fails
**Solution**: Ensure all required keys exist in product.yaml

### Issue: Schema validation fails
**Solution**: Check JSON syntax and ensure file referenced in product.yaml exists

### Issue: Missing contract file
**Solution**: Ensure contract path in product.yaml matches actual file location

## License

This is a portfolio/reference project. See LICENSE file for details.

## Questions?

Feel free to open an issue or contact the platform team!
