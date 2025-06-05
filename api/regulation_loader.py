# api/regulation_loader.py
import json
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RegulationLoader:
    def __init__(self):
        self.regulations_path = os.getenv('REGULATIONS_PATH', 'data/regulations.json')

    def _validate_structure(self, regulations: Dict[str, Any]) -> None:
        """Validate regulation structure matches expected format"""
        required_keys = ['description', 'clauses']
        for reg_name, reg_data in regulations.items():
            if not all(key in reg_data for key in required_keys):
                raise ValueError(f"Regulation {reg_name} missing required fields")
            if not isinstance(reg_data['clauses'], dict):
                raise ValueError(f"Clauses for {reg_name} must be key-value pairs")
            for clause_id in reg_data['clauses']:
                if '_' not in clause_id:
                    raise ValueError(f"Clause ID {clause_id} must contain underscore (e.g., GDPR_1)")

    def _create_sample_file(self) -> None:
        """Generate sample regulations file"""
        sample = {
            "GDPR": {
                "description": "General Data Protection Regulation (EU)",
                "clauses": {
                    "GDPR_1": "Process data lawfully and transparently",
                    "GDPR_2": "Collect only necessary data",
                    "GDPR_3": "Keep data accurate and up-to-date"
                }
            },
            "HIPAA": {
                "description": "Health Insurance Portability Act (US)",
                "clauses": {
                    "HIPAA_1": "Protect patient health information",
                    "HIPAA_2": "Allow patients to access their records"
                }
            }
        }
        os.makedirs(os.path.dirname(self.regulations_path), exist_ok=True)
        with open(self.regulations_path, 'w') as f:
            json.dump(sample, f, indent=2)

    def load(self) -> Dict[str, Any]:
        """
        Load and validate regulations
        Returns:
            {
                "regulation_name": {
                    "description": str,
                    "clauses": {
                        "clause_id": "clause_text",
                        ...
                    }
                },
                ...
            }
        """
        # Create sample if missing
        if not os.path.exists(self.regulations_path):
            self._create_sample_file()

        # Check file age
        if os.path.exists(self.regulations_path):
            file_age = (datetime.now() - 
                       datetime.fromtimestamp(os.path.getmtime(self.regulations_path)))
            if file_age.days > 30:
                print(f"Warning: Regulations file is {file_age.days} days old")

        # Load and validate
        try:
            with open(self.regulations_path, 'r') as f:
                data = json.load(f)
            self._validate_structure(data)
            return data
        except Exception as e:
            print(f"Error loading regulations: {str(e)}")
            return {}

# Singleton instance for easy import
regulation_loader = RegulationLoader()