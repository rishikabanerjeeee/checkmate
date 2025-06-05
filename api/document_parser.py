# api/document_parser.py
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Union
from PyPDF2 import PdfReader 
from docx import Document
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

# Database setup
DB_PATH = os.getenv('DB_PATH', 'data/compliance.db')

def init_db():
    """Initialize the database with required tables"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                branch_location TEXT,
                original_filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed_text TEXT,
                file_size_kb INTEGER,
                file_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER REFERENCES documents(id),
                regulation_name TEXT NOT NULL,
                clause_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                processing_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            )
        ''')
        conn.commit()
    except Exception as e:
        raise Exception(f"Database initialization failed: {str(e)}")
    finally:
        conn.close()

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT files"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            text = " ".join([para.text for para in doc.paragraphs])
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {os.path.splitext(file_path)[1]}")
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error processing {file_path}: {str(e)}")

def extract_text_from_files(company_name: Optional[str] = None) -> List[str]:
    """
    Get all processed texts from database for matching
    Args:
        company_name: Optional filter by company
    Returns:
        List of non-empty document texts
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if company_name:
            cursor.execute(
                'SELECT processed_text FROM documents WHERE company_name = ? AND processed_text IS NOT NULL',
                (company_name,)
            )
        else:
            cursor.execute('SELECT processed_text FROM documents WHERE processed_text IS NOT NULL')
            
        texts = [row[0] for row in cursor.fetchall() if row[0].strip()]
        return texts
    except Exception as e:
        raise Exception(f"Failed to fetch documents: {str(e)}")
    finally:
        conn.close()

def save_document_metadata(
    company: str,
    branch: str,
    filename: str,
    filepath: str,
    text: str
) -> int:
    """Save document information to database"""
    try:
        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        file_type = os.path.splitext(filename)[1].lower()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (
                company_name, 
                branch_location, 
                original_filename, 
                stored_path, 
                processed_text,
                file_size_kb,
                file_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (company, branch, filename, filepath, text, file_size, file_type))
        
        doc_id = cursor.lastrowid
        conn.commit()
        return doc_id
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to save document metadata: {str(e)}")
    finally:
        conn.close()

def parse_controls(
    uploaded_files: List[object],
    company_info: Dict[str, str],
    save_dir: str = "data/controls"
) -> List[Dict[str, Union[int, str]]]:
    """
    Process uploaded control documents with database support
    
    Args:
        uploaded_files: List of file-like objects with .name and .getbuffer()
        company_info: Dictionary with 'name' and optional 'branch'
        save_dir: Directory to store uploaded files
    
    Returns:
        List of processed documents with ids, texts, and paths
    """
    if not isinstance(company_info, dict):
        raise ValueError("company_info must be a dictionary")
    if 'name' not in company_info:
        raise ValueError("company_info must contain 'name' key")
    
    # Initialize database on first run
    init_db()
    os.makedirs(save_dir, exist_ok=True)
    processed_documents = []
    
    for uploaded_file in uploaded_files:
        try:
            file_path = os.path.join(save_dir, uploaded_file.name)
            
            # Save original file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract text
            text = extract_text_from_file(file_path)
            if not text:
                continue
                
            # Save to database
            doc_id = save_document_metadata(
                company=company_info.get('name', 'Unknown'),
                branch=company_info.get('branch', 'Headquarters'),
                filename=uploaded_file.name,
                filepath=file_path,
                text=text
            )
            
            processed_documents.append({
                'id': doc_id,
                'text': text,
                'original_path': file_path
            })
            
        except Exception as e:
            print(f"Error processing {getattr(uploaded_file, 'name', 'unknown')}: {str(e)}")
            continue
    
    return processed_documents

def get_company_documents(
    company_name: str,
    branch: Optional[str] = None
) -> List[Dict[str, Union[int, str, datetime]]]:
    """Retrieve all documents for a specific company/branch"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        cursor = conn.cursor()
        
        if branch:
            cursor.execute('''
                SELECT * FROM documents 
                WHERE company_name = ? AND branch_location = ?
                ORDER BY upload_timestamp DESC
            ''', (company_name, branch))
        else:
            cursor.execute('''
                SELECT * FROM documents 
                WHERE company_name = ?
                ORDER BY upload_timestamp DESC
            ''', (company_name,))
        
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        raise Exception(f"Failed to fetch company documents: {str(e)}")
    finally:
        conn.close()