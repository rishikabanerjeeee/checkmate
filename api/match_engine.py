# api/match_engine.py (updated)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

class MatchEngine:
    def __init__(self):
        # Authenticate with Hugging Face
        self.model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2',
            use_auth_token=os.getenv('HUGGINGFACEHUB_API_TOKEN')
        )
    
    def calculate_similarity(self, control_text, regulation_texts):
        """Calculate semantic similarity between control and regulations"""
        if not control_text.strip():
            return [0.0] * len(regulation_texts)
            
        control_embedding = self.model.encode([control_text])
        regulation_embeddings = self.model.encode(regulation_texts)
        
        similarities = cosine_similarity(control_embedding, regulation_embeddings)
        return similarities[0]
    
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