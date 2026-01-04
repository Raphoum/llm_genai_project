import streamlit as st
import uuid
import json
import os
from pathlib import Path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.graph import graph
from ingestion.ingest import ingest_file
from langchain_core.messages import HumanMessage, AIMessage

def get_content_text(content):
    """Helper to extract text from message content which might be a list or string."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "".join([block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"])
    return str(content)

# Page Config
st.set_page_config(page_title="ESILV Smart Assistant", page_icon="🎓", layout="wide")

st.title("ESILV Smart Assistant")

# Tabs
tab1, tab2, tab3 = st.tabs(["Chat", "Upload Knowledge", "Admin"])

# --- TAB 1: Chat ---
with tab1:
    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Display Chat History
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(get_content_text(msg.content))
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(get_content_text(msg.content))

    # Chat Input
    if prompt := st.chat_input("Ask a question about ESILV..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                events = graph.stream(
                    {"messages": [("user", prompt)]},
                    config,
                    stream_mode="values"
                )
                
                for event in events:
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if last_msg.type == "ai":
                             full_response = get_content_text(last_msg.content)
                             message_placeholder.markdown(full_response)
                
                if full_response:
                    st.session_state.messages.append(AIMessage(content=full_response))
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- TAB 2: Upload ---
with tab2:
    st.header("Upload New Knowledge")
    st.markdown("Upload specific PDF documents to add them to the chatbot's knowledge base.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Ingest Document"):
            with st.spinner("Processing..."):
                # Save temp file
                save_path = Path("data/pdfs") / uploaded_file.name
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Ingest
                success = ingest_file(save_path)
                
                if success:
                    st.success(f"Successfully ingested {uploaded_file.name}!")
                else:
                    st.error("Failed to ingest document.")

# --- TAB 3: Admin ---
with tab3:
    st.header("Admin Dashboard")
    
    st.subheader("Registrations")
    reg_file = "data/registrations.json"
    if os.path.exists(reg_file):
        try:
            with open(reg_file, "r") as f:
                data = json.load(f)
            st.dataframe(data)
        except Exception as e:
            st.error(f"Error reading registrations: {e}")
    else:
        st.info("No registrations yet.")
        
    st.divider()
    
    st.subheader("Knowledge Base")
    data_dir = Path("data/pdfs")
    if data_dir.exists():
        files = list(data_dir.glob("*.pdf"))
        st.write(f"Total Documents: {len(files)}")
        for f in files:
            st.text(f"📄 {f.name}")
    else:
        st.warning("Data directory not found.")
