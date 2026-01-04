# ESILV Smart Assistant

## 🎓 Project Overview
An intelligent Agentic Chatbot designed for ESILV engineering school. This system allows users to ask questions about programs and admissions (RAG) and register for contact via a conversational interface.

Key Features:
- **RAG (Retrieval Augmented Generation)**: Answers based on official ESILV documents.
- **Agentic Registration**: Conversationally collects user details (Name, Email, Interest) and saves them.
- **Memory**: Remembers conversation context across turns.
- **Admin Dashboard**: View registrations and manage knowledge base.
- **Modular Architecture**: Organized for scalability using LangGraph and LangChain.

## 📂 Project Structure
```
├── agents/             # Agent logic and graph definition
│   └── graph.py        # LangGraph definition with Memory and Tools
├── app/                # Application entry points (CLI)
│   └── cli.py          # Terminal-based chat interface
├── data/               # Data storage
│   ├── pdfs/           # PDF Knowledge Base
│   └── registrations.json # Saved user registrations
├── ingestion/          # Data processing scripts
│   └── ingest.py       # Script to load and embed PDFs
├── ui/                 # User Interface
│   └── app.py          # Streamlit Web Application
├── chroma_db/          # Vector Store Persistence
├── Requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🚀 Setup & Installation

1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd Project_LLM_GenAi
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   ```

## 🛠️ Usage

### 1. Ingest Data
Process the initial PDFs in `data/pdfs`:
```bash
python ingestion/ingest.py
```

### 2. Run Terminal Chat
Test the agent in your terminal:
```bash
python app/cli.py
```

### 3. Run Web Interface (Streamlit)
Launch the full UI with Chat, Upload, and Admin tabs:
```bash
streamlit run ui/app.py
```

## 🤖 Features Guide

- **Chat Tab**: Ask "What programs do you have?" or "I want to apply".
- **Upload Knowledge**: Go to the "Upload" tab to add new PDF brochures.
- **Admin Dashboard**: Go to "Admin" to view the list of registered students.

## 🏗️ Tech Stack
- **LLM**: Google Gemini 2.0 Flash
- **Orchestration**: LangGraph, LangChain
- **Vector DB**: ChromaDB
- **UI**: Streamlit
