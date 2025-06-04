# app/dashboard.py
import streamlit as st
from api.document_parser import parse_controls
from api.regulation_loader import load_regulations
from api.match_engine import MatchEngine
from utils.visualize import display_compliance_summary, display_gap_analysis

def show_dashboard():
    st.title("Compliance Dashboard")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload your organization's control documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Process files
        control_texts = parse_controls(uploaded_files)
        regulations = load_regulations()
        
        # Analyze compliance
        match_engine = MatchEngine()
        analysis_results = match_engine.match_controls_to_regulations(control_texts, regulations)
        
        # Display results
        st.header("Compliance Analysis Results")
        display_compliance_summary(analysis_results, regulations)
        
        st.header("Gap Analysis")
        display_gap_analysis(analysis_results, regulations)