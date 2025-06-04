# api/regulation_loader.py
import json
import os
from datetime import datetime

def validate_regulation_structure(regulations):
    """Check if loaded regulations have correct format"""
    required_keys = ['description', 'clauses']
    for reg_name, reg_data in regulations.items():
        if not all(key in reg_data for key in required_keys):
            raise ValueError(f"Invalid structure for regulation {reg_name}")
        if not isinstance(reg_data['clauses'], dict):
            raise ValueError(f"Clauses for {reg_name} must be a dictionary")

def check_for_updates(file_path):
    """Check if regulations file is older than 30 days"""
    if os.path.exists(file_path):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_age.days > 30:
            print(f"Warning: Regulations file '{file_path}' is over 30 days old - consider updating")

def load_regulations(file_path="data/regulations.json"):
    """Load regulatory frameworks from JSON file with validation"""
    # Create sample file if it doesn't exist
    if not os.path.exists(file_path):
        sample_regulations = {
            "GDPR": {
                "description": "General Data Protection Regulation (EU)",
                "clauses": {
                    "GDPR_1": "Personal data must be processed lawfully, fairly and transparently.",
                    "GDPR_2": "Data must be collected for specified, explicit and legitimate purposes.",
                    "GDPR_3": "Data minimization: Only collect what's necessary."
                }
            },
            "DPDP": {
                "description": "Digital Personal Data Protection Act (India)",
                "clauses": {
                    "DPDP_1": "Personal data can be processed only for lawful purpose.",
                    "DPDP_2": "Data fiduciaries must ensure accuracy and completeness of data.",
                    "DPDP_3": "Requirement for data breach notification."
                }
            },
            "HIPAA": {
                "description": "Health Insurance Portability and Accountability Act (US)",
                "clauses": {
                    "HIPAA_1": "Protected health information must be kept confidential.",
                    "HIPAA_2": "Patients must be able to access their health records.",
                    "HIPAA_3": "Required safeguards for electronic protected health information."
                }
            },
            "CCPA": {
                "description": "California Consumer Privacy Act (US)",
                "clauses": {
                    "CCPA_1": "Consumers have the right to know what personal data is collected.",
                    "CCPA_2": "Consumers have the right to delete personal data.",
                    "CCPA_3": "Businesses cannot discriminate against consumers who exercise their rights."
                }
            }
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(sample_regulations, f, indent=2)
        print(f"Created new regulations file at {file_path} with sample data")
    
    # Check if file needs updating
    check_for_updates(file_path)
    
    # Load and validate the regulations
    with open(file_path, 'r') as f:
        regulations = json.load(f)
    
    try:
        validate_regulation_structure(regulations)
        return regulations
    except ValueError as e:
        print(f"Error in regulations file: {str(e)}")
        print("Falling back to empty regulations")
        return {}