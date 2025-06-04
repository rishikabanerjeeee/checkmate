# main.py
import streamlit as st
from app.dashboard import show_dashboard
from app.chatbot import show_chatbot

def main():
    st.set_page_config(page_title="Compliance Checkmate", layout="wide")
    
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["Dashboard", "Chatbot"])
    
    if app_mode == "Dashboard":
        show_dashboard()
    else:
        show_chatbot()

if __name__ == "__main__":
    main()