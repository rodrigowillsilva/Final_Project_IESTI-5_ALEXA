
'''
Install:
- pip install -U 'langchain-chroma'
- pip install -U langchain
- pip install -U langchain-community
- pip install -U langchain-ollama
- pip install -U langchain-text-splitter
- pip install -U langchain-community pypdf
- pip install tiktoken


'''

import warnings
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Suppress LangSmith warnings
warnings.filterwarnings("ignore", 
                        message="API key must be provided when using hosted LangSmith API",
                        category=UserWarning)


# Vector Database

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define persistent directory for Chroma
PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_db")


# Directory for music files
music_dir = os.path.join(BASE_DIR, "data", "musics")


def create_vectorstore():
    """Create the vector store with document data and persist it to disk"""
    print("Creating persistent vector store...")
    
    docs_list = []
    
    # Load music files
    if os.path.exists(music_dir):
        print(f"Loading music files from: {music_dir}")
        # Walk through the directory
        for root, dirs, files in os.walk(music_dir):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    print(f"Loading file: {file}")
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Use the filename (without extension) as the music name
                        music_name = os.path.splitext(file)[0].replace('_', ' ').title()
                        
                        # Create a document object manually to ensure metadata is correct
                        from langchain_core.documents import Document
                        doc = Document(
                            page_content=content,
                            metadata={"source": file_path, "music_name": music_name}
                        )
                        docs_list.append(doc)
                    except Exception as e:
                        print(f"Error loading file {file}: {e}")
    else:
        print(f"Warning: Music directory {music_dir} not found")

    if not docs_list:
        print("Error: No documents were loaded. Check file paths.")
        return None
    
    print(f"Total documents loaded: {len(docs_list)}")
    
    # Split documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=30
    )
    doc_splits = text_splitter.split_documents(docs_list)
    print(f"Created {len(doc_splits)} document chunks")
    
    # Create embedding function
    print("Initializing embedding model...")
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    
    # Create and persist vectorstore to disk
    print("Creating vector database...")
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-edgeai-eng-chroma",
        embedding=embedding_function,
        persist_directory=PERSIST_DIRECTORY
    )
    
    # Important: persist to disk - Chroma now persists automatically
    # vectorstore.persist()
    
    print(f"Vector store created and saved to {PERSIST_DIRECTORY}")
    print(f"Total document chunks indexed: {len(doc_splits)}")
    
    return vectorstore


# Check if database already exists
if os.path.exists(PERSIST_DIRECTORY):
    choice = input(f"Database already exists at {PERSIST_DIRECTORY}. Recreate? (y/n): ")
    if choice.lower() != 'y':
        print("Exiting without changes.")
        exit()
    
# Create the vector store
create_vectorstore()
print("Database creation complete!")