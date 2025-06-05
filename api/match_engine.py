# api/match_engine.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import os
import sqlite3
from document_parser import DocumentParser
from regulation_loader import RegulationLoader

load_dotenv()

class MatchEngine:
    def __init__(self):
        # Authenticate with Hugging Face
        self.model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2',
            use_auth_token=os.getenv('HUGGINGFACEHUB_API_TOKEN')
        )
        self.document_parser = DocumentParser()
        self.regulation_loader = RegulationLoader()

    def calculate_similarity(self, control_text, regulation_texts):
        """Calculate semantic similarity between control and regulations"""
        if not control_text.strip():
            return [0.0] * len(regulation_texts)
            
        control_embedding = self.model.encode([control_text])
        regulation_embeddings = self.model.encode(regulation_texts)
        
        similarities = cosine_similarity(control_embedding, regulation_embeddings)
        return similarities[0]

    def load_and_match(self):
        """Load data from parser/loader and run matching"""
        # Step 1: Get document texts from document_parser
        control_texts = self.document_parser.extract_text_from_files()
        
        # Step 2: Load regulations from regulation_loader
        regulations = self.regulation_loader.load("data/regulations.json")
        
        # Step 3: Match them
        results = self.match_controls_to_regulations(control_texts, regulations)
        
        return results
    
    def match_controls_to_regulations(self, control_texts, regulations):
        """Match each control to all regulatory clauses"""
        results = []
        
        # Flatten all regulatory clauses
        reg_clauses = []
        reg_metadata = []
        for reg_name, reg_data in regulations.items():
            for clause_id, clause_text in reg_data['clauses'].items():
                reg_clauses.append(clause_text)
                reg_metadata.append((reg_name, clause_id, reg_data['description']))
        
        for control_text in control_texts:
            if not control_text.strip():
                continue
                
            similarities = self.calculate_similarity(control_text, reg_clauses)
            top_indices = np.argsort(similarities)[::-1][:5]  # Top 5 matches
            
            matches = []
            for idx in top_indices:
                matches.append({
                    "regulation": reg_metadata[idx][0],
                    "regulation_description": reg_metadata[idx][2],
                    "clause_id": reg_metadata[idx][1],
                    "clause_text": reg_clauses[idx],
                    "similarity_score": float(similarities[idx])
                })
            
            results.append({
                "control_text": control_text,
                "matches": matches
            })
        
        return results

    def save_results(self, results, db_path="data/compliance.db"):
        """Save results to SQLite database with proper foreign keys"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get document IDs for each control text
        text_to_id = {}
        cursor.execute("SELECT id, processed_text FROM documents")
        for doc_id, text in cursor.fetchall():
            text_to_id[text] = doc_id
        
        # Insert matches with document_id foreign key
        for result in results:
            doc_id = text_to_id.get(result["control_text"])
            if not doc_id:
                continue
                
            for match in result["matches"]:
                cursor.execute('''
                    INSERT INTO processing_results (
                        document_id, 
                        regulation_name, 
                        clause_id, 
                        similarity_score
                    ) VALUES (?, ?, ?, ?)
                ''', (doc_id, match["regulation"], match["clause_id"], match["similarity_score"]))
        
        conn.commit()
        conn.close()