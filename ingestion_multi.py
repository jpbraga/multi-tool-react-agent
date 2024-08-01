import os
from typing import List
from xml.dom.minidom import Document
from dotenv import load_dotenv

import consts

load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import ReadTheDocsLoader, JSONLoader, TextLoader
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDINGS_MODEL"))

def load_json_doc(json_file:str) -> List[Document]:
    print("Loading JSON files...")
    loader = JSONLoader(
    jq_schema='.',
    file_path=json_file,
    text_content=False)
    document = loader.load();
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(document)
    return docs

def load_text(json_file:str) -> List[Document]:
    print("Loading JSON files...")
    loader = JSONLoader(
    jq_schema='.',
    file_path=json_file,
    text_content=False)
    document = loader.load();
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(document)
    return docs


def load_pdf(pdf_file:str) -> List[Document]:
    print("Loading PDF...")
    loader = PyPDFLoader(file_path=pdf_file)
    document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(document)
    return docs

def load_text(text_file:str) -> List[Document]:
    print("Loading text...")
    loader = TextLoader(text_file)
    document = loader.load()
    print("Document loaded...")
    print("Splitting...")
    text_splitter = CharacterTextSplitter(chunk_size=1536, chunk_overlap=200, separator="\n")
    docs = text_splitter.split_documents(document)
    return docs

def load_html_docs(files_root_folder:str, update_refs: bool=False) -> List[Document]:
    print("Loading HTML files...")
    loader = ReadTheDocsLoader(files_root_folder)
    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} documents.")
    print("Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)
    if update_refs:
        print("Updating references...")
        for doc in documents:
            new_url = doc.metadata["source"]
            new_url = new_url.replace("langchain-docs", "https:/")
            doc.metadata.update({"source": new_url})
    return documents

def ingest_docs():
    documents = load_text("ivegan/ivegan.txt")
    print(f"Adding {len(documents)} documents to Pinecone...")
    index_name = "ivegan-index"
    PineconeVectorStore.from_documents(
        documents, embeddings, index_name=index_name
    )
    print(f"Data embedded and stored in Pinecone index {index_name}.")

if __name__ == "__main__":
    ingest_docs()
