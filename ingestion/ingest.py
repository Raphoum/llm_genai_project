import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Configuration
DATA_DIR = Path("data/pdfs")
PERSIST_DIRECTORY = Path("chroma_db")
EMBEDDING_MODEL = "models/embedding-001"

def ingest_file(file_path: Path):
    """Ingests a single PDF file into the existing vector store."""
    print(f"Processing {file_path.name}...")
    
    try:
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        if not docs:
            print(f"No pages found in {file_path.name}")
            return False
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        splits = text_splitter.split_documents(docs)
        print(f"Split {len(docs)} pages into {len(splits)} chunks.")
        
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Initialize Chroma with persist directory
        vectorstore = Chroma(
            persist_directory=str(PERSIST_DIRECTORY), 
            embedding_function=embeddings
        )
        
        vectorstore.add_documents(documents=splits)
        print(f"Successfully added {file_path.name} to vector store.")
        return True
        
    except Exception as e:
        print(f"Error ingesting {file_path.name}: {e}")
        return False

def ingest_all():
    """Ingests all PDFs in the data directory."""
    if not DATA_DIR.exists():
        print(f"Data directory {DATA_DIR} not found.")
        return

    pdf_files = list(DATA_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")
    
    for pdf_path in pdf_files:
        ingest_file(pdf_path)

if __name__ == "__main__":
    ingest_all()
