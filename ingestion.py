import os
from dotenv import load_dotenv

import consts

load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import ReadTheDocsLoader
from langchain_pinecone import PineconeVectorStore

embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDINGS_MODEL"))


def ingest_docs():
    print("Loading the documentation from disk...")
    loader = ReadTheDocsLoader("langchain-docs/api.python.langchain.com/en/latest")
    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} documents.")
    print("Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    documents = text_splitter.split_documents(raw_documents)
    
    
    print("Updating references...")
    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")
        doc.metadata.update({"source": new_url})
    
    print(f"Adding {len(documents)} documents to Pinecone...")
    PineconeVectorStore.from_documents(
        documents, embeddings, index_name=consts.INDEX_NAME
    )
    print("Data embedded and stored in Pinecone index.")


if __name__ == "__main__":
    ingest_docs()
