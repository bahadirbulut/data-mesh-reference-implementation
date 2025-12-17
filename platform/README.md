# Platform Services

## Overview
This Data Mesh assumes a **self-serve data platform** that provides foundational capabilities to all domain teams. The platform is provisioned separately via Infrastructure as Code (IaC) and provides:

## Core Platform Capabilities

### 1. Storage Layer
- **Azure Data Lake Storage Gen2 (ADLS Gen2)**
  - Bronze container: raw ingestion layer
  - Silver container: cleaned/validated data
  - Gold container: domain-owned data products
  - Hierarchical namespace enabled
  - Zone redundancy for production

### 2. Compute Layer
- **Azure Databricks**
  - Separate workspaces per environment (dev, staging, prod)
  - Job clusters for production workloads
  - Interactive clusters for development
  - Unity Catalog integration (optional for production)
  - Auto-scaling enabled

### 3. Observability & Monitoring
- **Azure Log Analytics**
  - Centralized logging for all platform services
  - Diagnostic settings enabled on:
    - ADLS Gen2
    - Databricks workspaces
    - Key Vault
  - Custom dashboards for SLA monitoring

### 4. Security & Identity
- **Azure Key Vault**
  - Secret management for connection strings
  - Service principal credentials
  - API keys and tokens
- **Azure Active Directory**
  - Service principals for pipeline authentication
  - RBAC for resource access
  - Conditional access policies

### 5. Networking
- **Virtual Network (VNet)**
  - Private endpoints for ADLS Gen2
  - Databricks VNet injection (optional)
  - NSG rules for traffic control
- **Azure Private Link**
  - Private connectivity to storage accounts

### 6. Infrastructure as Code
- **Terraform**
  - All infrastructure defined as code
  - State stored in Azure Storage with lock
  - Modular design for reusability
  - CI/CD integration for deployment

## Platform Reference
The full platform baseline is provisioned by:
**https://github.com/bahadirbulut/terraform-azure-data-platform**

## Platform Team Responsibilities
- Provision and maintain infrastructure
- Ensure 99.9% uptime SLA
- Provide documentation and onboarding
- Support domain teams with platform issues
- Manage costs and governance
- Security patches and updates

## Domain Team Responsibilities
- Build and own data products
- Follow platform standards and policies
- Monitor their pipelines and data quality
- Manage their domain-specific configurations
- Collaborate with platform team for issues

## Getting Started
1. Request access from platform team
2. Review governance standards in `/governance/standards/`
3. Use data product template for new products
4. Follow naming conventions
5. Set up CI/CD for governance checks
