# Data Mesh Reference Implementation (DEMO)

**Author:** Bahadir Bulut — Nexence CommV  
**Location:** Belgium (EU)  
**Purpose:** Demo Data Mesh architecture

---

## 📖 What is This?

This repository demonstrates a **Data Mesh architecture** - a modern approach to data management where:
- **Different teams own their data** (not a central data team)
- **Data is treated as a product** (with quality guarantees and documentation)
- **Standards are shared** but execution is distributed
- **Each domain publishes ready-to-use datasets** for others to consume

Think of it like this: Instead of one central kitchen making all the food, each department has its own kitchen, but everyone follows the same food safety standards.

---

## 🎯 What You'll get

By exploring this repo, you'll see:

1. **How to structure domains** - Each business area owns its data
2. **How to create data products** - Datasets with guarantees and documentation
3. **How to enforce quality** - Automated checks ensure standards are met
4. **How to process data in layers** - Raw → Cleaned → Ready for analysis
5. **How to version data contracts** - So changes don't break consumers

---

## 🏗️ Repository Structure

```
data-mesh-reference-implementation/
│
├── 📁 domains/              ← Each business area has its own folder
│   ├── sales/              ← Sales team owns this
│   │   ├── product.yaml    ← "What we publish" (metadata)
│   │   ├── README.md       ← "How to use our data"
│   │   ├── contracts/      ← "What fields exist" (schema)
│   │   ├── pipelines/      ← "How we process data" (code)
│   │   └── sample_data/    ← Examples
│   │
│   └── research_ops/       ← Research team owns this
│       └── (same structure)
│
├── 📁 governance/          ← The "rules everyone follows"
│   ├── checks/            ← Automated validation scripts
│   ├── policies/          ← Access control, PII rules
│   └── standards/         ← Naming, versioning, SLA rules
│
├── 📁 platform/           ← The shared infrastructure
│   └── README.md          ← Azure, Databricks, storage details
│
└── 📁 .github/workflows/  ← Automated quality checks
```

---

## 🔄 How It Works (The Journey of Data)

### Step 1: Raw Data Arrives (Bronze Layer)
```
CSV file → Bronze pipeline → Stored as-is in Bronze layer
```
- **What happens:** Data is copied from source systems without changes
- **Why:** Keep original data for audit/recovery
- **Code:** `domains/*/pipelines/bronze.py`

### Step 2: Data Gets Cleaned (Silver Layer)
```
Bronze → Silver pipeline → Remove duplicates, fix types, validate
```
- **What happens:** Data is cleaned, validated, standardized
- **Why:** Ensure quality before business logic is applied
- **Code:** `domains/*/pipelines/silver.py`

### Step 3: Business Value Created (Gold Layer)
```
Silver → Gold pipeline → Aggregate, calculate, create data product
```
- **What happens:** Apply business logic, create final datasets
- **Why:** This is what consumers actually use
- **Code:** `domains/*/pipelines/gold.py`

---

## 📊 Example: Sales Domain

Let's walk through a real example:

### 1. **The Product** (`product.yaml`)
Says: "We publish daily sales revenue with 99.5% uptime, refreshed at 1 AM"

### 2. **The Contract** (`contracts/sales_orders_v1.schema.json`)
Says: "You'll get these exact fields: order_date and daily_revenue"

### 3. **The Pipeline** (`pipelines/*.py`)
- **Bronze:** Reads CSV files → Saves raw
- **Silver:** Removes duplicates → Validates quantities > 0
- **Gold:** Calculates revenue (quantity × price) → Groups by date

### 4. **The Result**
A clean dataset: Each row is one day with total revenue

```
order_date   | daily_revenue
-------------|-------------
2025-01-01   | 1,350.00
2025-01-02   | 2,100.00
```

---

## 🛡️ Governance (Quality Assurance)

Every domain must follow these rules:

### Automated Checks (Run on Every PR)
✅ **Product Validation:** Does `product.yaml` have all required fields?  
✅ **Schema Validation:** Do schema files exist and are they valid JSON?  
✅ **Code Quality:** Does Python code follow standards?

### Standards Everyone Follows
- **Naming:** How to name tables, columns, files
- **Versioning:** When to create v2, how to deprecate v1
- **SLAs:** What uptime/freshness to promise
- **Access:** Who can see what data

### Policies for Sensitive Data
- **PII Handling:** How to handle personal information (GDPR compliant)
- **Access Control:** Role-based access patterns

---

## 🚀 Quick Start Guide

### For Reviewers (Understanding the Repo)

1. **Start here:** Read this README (you are here! ✓)

2. **Explore a domain:**
   ```bash
   cd domains/sales
   cat product.yaml        # See what they publish
   cat README.md           # Read their documentation
   cat contracts/sales_orders_v1.schema.json  # See the data structure
   ```

3. **Check the pipelines:**
   ```bash
   cat pipelines/bronze.py  # How raw data is ingested
   cat pipelines/silver.py  # How data is cleaned
   cat pipelines/gold.py    # How final product is created
   ```

4. **Review governance:**
   ```bash
   cd governance/standards
   cat naming.md           # Naming conventions
   cat versioning.md       # How versions work
   cat slas.md            # SLA requirements
   ```

5. **Run quality checks:**
   ```bash
   python governance/checks/validate_products.py
   python governance/checks/validate_schemas.py
   ```

### For Contributors (Adding New Domains)

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions.

---

## 🎓 Key Concepts Explained Simply

### What is a "Data Product"?
A dataset that is:
- **Documented** - Clear README and schema
- **Reliable** - Has SLA commitments (uptime, freshness)
- **Discoverable** - Listed in catalog with metadata
- **Quality-assured** - Automated checks ensure accuracy

### What is a "Data Contract"?
A promise about data structure:
```json
{
  "order_date": "string (YYYY-MM-DD)",
  "daily_revenue": "number (>= 0)"
}
```
Like an API contract, but for data!

### What is "Medallion Architecture"?
A pattern with 3 layers:
- 🥉 **Bronze** - Raw data (unchanged from source)
- 🥈 **Silver** - Cleaned data (validated, standardized)
- 🥇 **Gold** - Business data (aggregated, ready to use)

### What is "Federated Governance"?
- **Central team:** Sets standards (naming, security, quality)
- **Domain teams:** Implement their own data products
- **Automated checks:** Ensure compliance

Like building codes: City sets standards, each builder follows them.

---

## 🔗 Related Infrastructure

This data mesh runs on a platform I built separately:

**Platform Repository:** [terraform-azure-data-platform](https://github.com/bahadirbulut/terraform-azure-data-platform)

**What it provides:**
- Azure Data Lake Storage (Bronze/Silver/Gold containers)
- Azure Databricks (for running PySpark pipelines)
- Azure Key Vault (for secrets)
- Networking and security
- Monitoring and logging

**Separation of concerns:**
- **Platform repo:** Infrastructure (Terraform)
- **This repo:** Data products and governance

---

## 📂 What Each Folder Contains

| Folder | Purpose | Who Maintains |
|--------|---------|---------------|
| `domains/sales/` | Sales data products | Sales team |
| `domains/research_ops/` | Experiment data products | Research team |
| `governance/checks/` | Validation scripts | Platform team |
| `governance/policies/` | Security & compliance rules | Platform team |
| `governance/standards/` | Naming, versioning, SLA docs | Platform team |
| `platform/` | Infrastructure documentation | Platform team |
| `.github/workflows/` | CI/CD automation | Platform team |

---

## 🎯 Current Implementation

### ✅ What's Included

**Two Complete Domains:**
- **Sales** - Daily revenue data product
- **Research Ops** - Experiment metrics data product

**Full Governance Framework:**
- ✓ Naming conventions
- ✓ Versioning strategy
- ✓ SLA requirements
- ✓ Access control model
- ✓ PII handling policy
- ✓ Data product template

**Automated Quality:**
- ✓ Product metadata validation
- ✓ Schema validation
- ✓ CI/CD integration
- ✓ Python code linting

### ⚠️ What's Not Included (Portfolio Scope)

This is a **reference implementation**, not production:
- ❌ No live infrastructure (see platform repo for IaC)
- ❌ No actual Azure connections
- ❌ No data catalog UI
- ❌ No Unity Catalog integration
- ❌ No user authentication (IAM examples only)

---

## 🤔 FAQ

**Q: Can I run these pipelines?**  
A: The code is complete but needs Azure infrastructure. You can review the logic and patterns.

**Q: How do I add a new domain?**  
A: Follow the template in `governance/standards/data-product-template.md` and see `CONTRIBUTING.md`.

**Q: Is this production-ready?**  
A: It's a reference implementation showing patterns and architecture. Would need operational tooling for production.

**Q: What's the difference between this and a data warehouse?**  
A: Traditional data warehouse = central team owns all data. Data Mesh = domain teams own their data, central team provides platform.

**Q: Why use this architecture?**  
A: Better for large organizations where:
- Many teams need different data
- Central team becomes bottleneck
- Domain expertise improves data quality
- Scaling requires distributed ownership

---

## 📚 Learn More

**About Data Mesh:**
- Book: "Data Mesh" by Zhamak Dehghani
- Concept: Domain-oriented decentralized data ownership

**Technologies Used:**
- Azure Data Lake Storage Gen2
- Azure Databricks (Apache Spark)
- Delta Lake (ACID transactions)
- JSON Schema (contracts)
- GitHub Actions (CI/CD)

**Standards Referenced:**
- GDPR (privacy compliance)
- JSON Schema Draft 2020-12
- Semantic Versioning concepts

---

## 🤝 Contributing

Want to add a new domain or improve governance?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Step-by-step guide
- Governance requirements
- Code quality standards
- PR process

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

This is a portfolio project for demonstration purposes.

---

## 📧 Contact

**Bahadir Bulut**  
Nexence CommV  
Belgium (EU)

Portfolio project showcasing Data Mesh architecture and governance.

---

## ⭐ Summary

**In one sentence:** This repo shows how to build a Data Mesh where domain teams own their data products, follow shared governance standards, and publish clean, documented datasets for others to use.

**Why it matters:** Solves the "central data team bottleneck" problem in large organizations by distributing data ownership while maintaining quality through federated governance.
