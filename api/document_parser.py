# api/document_parser.py (with database support)
import os
import sqlite3
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
DB_PATH = "data/compliance.db"

def init_db():
    """Initialize the database with required tables"""
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
            processing_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def extract_text_from_file(file_path):
    """Extract text from PDF, DOCX, or TXT files"""
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
            raise ValueError("Unsupported file format")
        
        return text.strip()
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return ""

def save_document_metadata(company, branch, filename, filepath, text):
    """Save document information to database"""
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
    conn.close()
    return doc_id

def parse_controls(uploaded_files, company_info, save_dir="data/controls"):
    """
    Process uploaded control documents with database support
    
    Args:
        uploaded_files: List of uploaded file objects
        company_info: Dict with 'name' and 'branch' keys
        save_dir: Directory to store uploaded files
    """
    # Initialize database on first run
    init_db()
    
    os.makedirs(save_dir, exist_ok=True)
    processed_documents = []
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join(save_dir, uploaded_file.name)
        
        try:
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
            print(f"Error processing {uploaded_file.name}: {str(e)}")
    
    return processed_documents

def get_company_documents(company_name, branch=None):
    """Retrieve all documents for a specific company/branch"""
    conn = sqlite3.connect(DB_PATH)
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
    
    results = cursor.fetchall()
    conn.close()
    
    return results