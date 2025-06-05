import os
import json
import logging
from datetime import datetime
from typing import Dict, List
from api.document_parser import DocumentParser
from api.regulation_loader import RegulationLoader
from api.match_engine import MatchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compliance_checker.log'),
        logging.StreamHandler()
    ]
)

def initialize_components() -> tuple:
    """Initialize all system components with error handling"""
    try:
        # Initialize document parser with database
        doc_parser = DocumentParser()
        doc_parser.init_db()
        logging.info("Document parser initialized")

        # Load regulations
        reg_loader = RegulationLoader()
        regulations = reg_loader.load()
        if not regulations:
            raise ValueError("No regulations loaded")
        logging.info(f"Loaded {len(regulations)} regulations")

        # Initialize matching engine
        matcher = MatchEngine()
        logging.info("Matching engine initialized")

        return doc_parser, regulations, matcher

    except Exception as e:
        logging.error(f"Initialization failed: {str(e)}")
        raise

def process_sample_documents(parser: DocumentParser) -> List[Dict]:
    """Process test documents and return parsed content"""
    test_docs = [
        {
            "name": "gdpr_compliance.docx",
            "content": """Data Protection Policy
                        --------------------
                        1. We process personal data lawfully per GDPR Article 1
                        2. All data is encrypted according to GDPR Article 6 requirements
                        3. Data collection is limited to specified purposes (GDPR Article 2)"""
        },
        {
            "name": "hipaa_compliance.pdf",
            "content": """HIPAA Compliance Document
                        ------------------------
                        - All patient records are protected per HIPAA Section 1
                        - Patients can request records access as per HIPAA Section 2"""
        }
    ]

    processed = []
    os.makedirs("data/controls", exist_ok=True)

    for doc in test_docs:
        try:
            path = os.path.join("data/controls", doc["name"])
            with open(path, "w") as f:
                f.write(doc["content"])

            # Simulate file upload with metadata
            class FileObj:
                def __init__(self, name, path):
                    self.name = name
                    self.path = path
                def getbuffer(self):
                    with open(self.path, "rb") as f:
                        return f.read()

            file_obj = FileObj(doc["name"], path)
            company_info = {"name": "TestCorp", "branch": "HQ"}
            
            result = parser.parse_controls([file_obj], company_info)
            if result:
                processed.extend(result)
                logging.info(f"Processed {doc['name']}")

        except Exception as e:
            logging.warning(f"Failed to process {doc['name']}: {str(e)}")

    return processed

def run_compliance_analysis():
    """End-to-end compliance checking workflow"""
    try:
        logging.info("\n" + "="*50)
        logging.info(f"🚀 Starting Compliance Check - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        logging.info("="*50 + "\n")

        # 1. Initialize system
        doc_parser, regulations, matcher = initialize_components()

        # 2. Process sample documents
        logging.info("[1/3] Processing sample documents...")
        processed_docs = process_sample_documents(doc_parser)
        if not processed_docs:
            raise RuntimeError("No documents processed successfully")

        # 3. Run compliance matching
        logging.info("\n[2/3] Running compliance matching...")
        control_texts = [doc["text"] for doc in processed_docs]
        matches = matcher.match_controls_to_regulations(control_texts, regulations)
        
        # Save results to database
        matcher.save_results(matches)
        logging.info("Saved results to database")

        # 4. Display results
        logging.info("\n[3/3] Compliance Analysis Results:")
        for i, result in enumerate(matches, 1):
            logging.info(f"\n📄 Document {i}:")
            logging.info(f"Control Text: {result['control_text'][:100]}...")
            
            if not result["matches"]:
                logging.warning("  ⚠️ No regulation matches found")
                continue
                
            for match in result["matches"]:
                logging.info(
                    f"  ✅ {match['regulation']} {match['clause_id']} "
                    f"(Score: {match['similarity_score']:.2f}): "
                    f"{match['clause_text'][:50]}..."
                )

        logging.info("\n🎉 Compliance check completed successfully")

    except Exception as e:
        logging.error(f"❌ Workflow failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if run_compliance_analysis():
        print("\nCheck 'compliance_checker.log' for detailed results")
    else:
        print("\nCompliance check failed - see log for details")