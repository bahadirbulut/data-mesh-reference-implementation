# Federated Governance

## Overview
Federated governance in a Data Mesh means that **domains own their data products** while following **centralized standards and policies**. This ensures consistency across the mesh without creating bottlenecks.

## Governance Model

### Centralized Components (Platform Team)
- Platform infrastructure and services
- Global standards (naming, versioning, SLAs)
- Security and compliance policies
- Automated governance checks in CI/CD
- Data product templates and tooling

### Federated Components (Domain Teams)
- Domain-specific data products
- Schema definitions and contracts
- Data quality rules and expectations
- SLA commitments for their products
- Documentation and metadata

## Directory Structure

```
governance/
├── checks/             # Automated validation scripts
│   ├── validate_products.py   # Checks product.yaml compliance
│   └── validate_schemas.py    # Validates schema presence & format
├── policies/           # Compliance and security policies
│   ├── access-model.md        # Access control patterns
│   └── pii.md                 # PII handling requirements
└── standards/          # Cross-domain standards
    ├── data-product-template.md  # Template for new products
    ├── naming.md                 # Naming conventions
    ├── slas.md                   # SLA definitions
    └── versioning.md             # Versioning strategy
```

## Automated Governance Checks

All data products must pass automated checks before merge:

### 1. Product Validation (`validate_products.py`)
Ensures each domain has a valid `product.yaml` with:
- Required metadata (name, domain, owner)
- Output definitions with contracts
- SLA commitments
- Privacy declarations

### 2. Schema Validation (`validate_schemas.py`)
Ensures:
- Schema files exist for all outputs
- Schemas follow JSON Schema standard
- Version consistency between product and schema

### 3. CI/CD Integration
These checks run automatically on:
- Pull requests to main/master branch
- Pre-commit hooks (optional)
- Scheduled audits

## Standards

All domain teams must follow these standards:

- **[Naming Conventions](standards/naming.md)** - How to name products, tables, and columns
- **[Versioning Strategy](standards/versioning.md)** - How to version schemas and data products
- **[SLA Requirements](standards/slas.md)** - What SLAs to commit to and how to measure
- **[Data Product Template](standards/data-product-template.md)** - Standard structure for new products

## Policies

All domain teams must comply with these policies:

- **[Access Model](policies/access-model.md)** - How to control access to data products
- **[PII Handling](policies/pii.md)** - Requirements for personal identifiable information

## How to Add a New Data Product

1. Copy the data product template
2. Fill in all required metadata
3. Define schema in JSON Schema format
4. Document contract in markdown
5. Add governance checks to CI/CD
6. Create PR for review
7. Platform team reviews compliance
8. Merge after approval

## Compliance Monitoring

The platform team monitors:
- SLA adherence across all products
- Schema version consistency
- Quality check failures
- Access audit logs
- Cost per domain

## Feedback Loop

Governance standards evolve based on:
- Domain team feedback
- Platform capabilities
- Regulatory changes
- Industry best practices

Submit feedback via:
- GitHub issues in this repo
- Monthly governance council meetings
- Direct communication with platform team
