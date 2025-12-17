"""Schema Validation Script

This script validates that all data products have valid schema files.
It checks for:
1. Existence of contracts directory
2. Schema files referenced in product.yaml exist
3. JSON schemas are valid JSON
4. JSON schemas follow JSON Schema standard

This ensures that all data products have well-defined contracts.

Usage:
    python governance/checks/validate_schemas.py

Exit codes:
    0: All validations passed
    1: Validation failures found
"""

import os, sys, json

def fail(msg):
    """Print error message and exit with failure code.
    
    Args:
        msg (str): Error message to display
    """
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    """Main validation logic.
    
    Validates schema files for all domains:
    1. Checks contracts directory exists
    2. Parses product.yaml to find contract references
    3. Validates each schema file exists and is valid JSON
    4. Ensures JSON schemas have required fields
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

        # Check for product.yaml (or legacy products.yaml)
        product_file = os.path.join(dpath, "product.yaml")
        if not os.path.isfile(product_file):
            # Try legacy naming
            product_file = os.path.join(dpath, "products.yaml")
            if not os.path.isfile(product_file):
                fail(f"Missing product.yaml for domain: {domain}")

        # Check contracts directory exists
        contracts_dir = os.path.join(dpath, "contracts")
        if not os.path.isdir(contracts_dir):
            fail(f"Missing contracts/ directory for domain: {domain}")

        # Parse product.yaml to find contract references
        with open(product_file, "r", encoding="utf-8") as f:
            product_content = f.read()

        # Simple YAML parsing - look for contract: path references
        contract_files = []
        for line in product_content.split("\n"):
            line = line.strip()
            if line.startswith("contract:"):
                # Extract path like: contract: contracts/sales_orders_v1.schema.json
                contract_path = line.split("contract:")[1].strip().strip('"').strip("'")
                contract_files.append(contract_path)

        # Validate each contract file
        for contract_file in contract_files:
            full_path = os.path.join(dpath, contract_file)
            
            # Check file exists
            if not os.path.isfile(full_path):
                fail(f"Missing contract file for domain '{domain}': {contract_file}")

            # If it's a JSON schema file, validate JSON format and structure
            if contract_file.endswith(".json"):
                try:
                    # Read and parse JSON
                    with open(full_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)
                    
                    # Basic JSON Schema validation - root must be an object
                    if not isinstance(schema, dict):
                        fail(f"Invalid JSON schema in {contract_file}: root must be an object")
                    
                    # Check for required JSON Schema fields
                    if "type" not in schema and "properties" not in schema:
                        fail(f"Invalid JSON schema in {contract_file}: missing 'type' or 'properties'")
                    
                    # Log success
                    print(f"✓ Valid schema: {domain}/{contract_file}")
                
                except json.JSONDecodeError as e:
                    fail(f"Invalid JSON in {contract_file}: {e}")
                except Exception as e:
                    fail(f"Error reading {contract_file}: {e}")

    # All validations passed
    print("OK: schema validation checks passed")

# Entry point - run validation when script is executed directly
if __name__ == "__main__":
    main()
