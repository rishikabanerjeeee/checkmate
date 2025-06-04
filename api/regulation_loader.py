# api/regulation_loader.py
import json
import os

def load_regulations(file_path="data/regulations.json"):
    """Load regulatory frameworks from JSON file"""
    if not os.path.exists(file_path):
        # Create a sample if file doesn't exist
        sample_regulations = {
            "GDPR": {
                "description": "General Data Protection Regulation (EU)",
                "clauses": {
                    "GDPR_1": "Personal data must be processed lawfully, fairly and transparently.",
                    "GDPR_2": "Data must be collected for specified, explicit and legitimate purposes."
                }
            },
            "DPDP": {
                "description": "Digital Personal Data Protection Act (India)",
                "clauses": {
                    "DPDP_1": "Personal data can be processed only for lawful purpose.",
                    "DPDP_2": "Data fiduciaries must ensure accuracy and completeness of data."
                }
            }
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(sample_regulations, f, indent=2)
    
    with open(file_path, 'r') as f:
        return json.load(f)