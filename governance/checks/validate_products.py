"""Product Metadata Validation Script

This script validates that all domains have a properly formatted product.yaml file
with all required metadata fields. This ensures governance compliance across the mesh.

Required fields:
- name: Data product name
- domain: Domain ownership
- owner: Team and contact information
- outputs: Data product outputs with contracts
- sla: SLA commitments
- privacy: PII declarations

Usage:
    python governance/checks/validate_products.py

Exit codes:
    0: All validations passed
    1: Validation failures found
"""

import os, sys, json

# Define required keys that must exist in every product.yaml
REQUIRED_KEYS = ["name", "domain", "owner", "outputs", "sla", "privacy"]

def fail(msg):
    """Print error message and exit with failure code.
    
    Args:
        msg (str): Error message to display
    """
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    """Main validation logic.
    
    Iterates through all domains and validates their product.yaml files.
    Checks for:
    1. Existence of product.yaml file
    2. Presence of all required keys
    """
    # Get the domains directory path
    root = os.path.join(os.getcwd(), "domains")
    if not os.path.isdir(root):
        fail("domains/ folder not found")

    # Iterate through each domain folder
    for domain in os.listdir(root):
        dpath = os.path.join(root, domain)
        if not os.path.isdir(dpath):
            continue  # Skip non-directory items

        # Check if product.yaml exists
        product = os.path.join(dpath, "product.yaml")
        if not os.path.isfile(product):
            fail(f"Missing product.yaml for domain: {domain}")

        # Read and validate product.yaml content
        # Using simple text search instead of YAML parser to avoid dependencies
        text = open(product, "r", encoding="utf-8").read()
        
        # Check for each required key
        for k in REQUIRED_KEYS:
            if f"{k}:" not in text:
                fail(f"{product} missing required key: {k}")

    # All validations passed
    print("OK: product.yaml checks passed")

# Entry point - run validation when script is executed directly
if __name__ == "__main__":
    main()
