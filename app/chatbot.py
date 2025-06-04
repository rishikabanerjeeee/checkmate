# app/chatbot.py
import streamlit as st
from transformers import pipeline
from api.regulation_loader import load_regulations

def show_chatbot():
    st.title("Compliance Assistant Chatbot")
    
    # Load regulations and initialize chatbot
    regulations = load_regulations()
    chatbot = pipeline("text-generation", model="gpt2")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Ask about compliance..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        context = f"""
        You are a compliance expert helping a multinational bank. Here are relevant regulations:
        {regulations}
        """
        full_prompt = f"{context}\n\nQuestion: {prompt}\n\nAnswer:"
        
        response = chatbot(full_prompt, max_length=200, do_sample=True)[0]['generated_text']
        response = response.split("Answer:")[-1].strip()
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})