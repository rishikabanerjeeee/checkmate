# api/document_parser.py (updated)
import os
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def parse_controls(uploaded_files, save_dir="data/controls"):
    """Process uploaded control documents"""
    os.makedirs(save_dir, exist_ok=True)
    control_texts = []
    
    for uploaded_file in uploaded_files:
        # Ensure the controls directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        file_path = os.path.join(save_dir, uploaded_file.name)
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            text = extract_text_from_file(file_path)
            if text:  # Only add if text extraction succeeded
                control_texts.append(text)
        except Exception as e:
            print(f"Error saving {uploaded_file.name}: {str(e)}")
    
    return control_texts