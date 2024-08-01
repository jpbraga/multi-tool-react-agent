import os
import ast
from typing import Any, Dict, List, Optional
from xml.dom.minidom import Document
from dotenv import load_dotenv

load_dotenv()
from langchain_core.prompts import PromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain_core.retrievers import RetrieverLike
from langchain_core.runnables import (
    RunnableConfig
)
class CombinedRetriever(RetrieverLike):
    def __init__(self, retrievers):
        self.retrievers = retrievers

    def get_relevant_documents(self, query):
        results = []
        for retriever in self.retrievers:
            results.extend(retriever.invoke(query))
        return results

    def as_retriever(self):
        return self

    def with_config(self, config):
        return self

    def retrieve(self, input):
        query = input['input']
        return self.get_relevant_documents(query)
    
    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> List[Document]:
        return self.get_relevant_documents(input)
    
def run_llm(query: str, chat_history:List[Dict[str, Any]]):
    embeddings = OpenAIEmbeddings(model=os.environ["OPENAI_EMBEDDINGS_MODEL"])
    
    # Initialize multiple indexes
    index_names = ast.literal_eval(os.environ['MULTI_INDEX_LIST'])
    vector_stores = [PineconeVectorStore(index_name=index_name, embedding=embeddings) for index_name in index_names]
    
    chat = ChatOpenAI(model=os.environ["OPENAI_MODEL_NAME"], temperature=0, verbose=True)

    template ="""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    As a helpful assistant, be polite and helpful.
    {context}

    Question: {input}
    Helpful Answer:"""
    
    retrieval_qa_chat_prompt = PromptTemplate(template=template,input_variables=["context", "input"])
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)
    
    # Create a combined retriever for all indexes
    all_retrievers = [store.as_retriever() for store in vector_stores]
    combined_retriever = CombinedRetriever(all_retrievers)
    
    history_aware_retriever = create_history_aware_retriever(chat, combined_retriever, rephrase_prompt)
    
    qa = create_retrieval_chain(
        retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
    )
    result = qa.invoke(input={"input": query, "chat_history": chat_history})
    new_result = {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"]
        
    }
    return new_result

if __name__ == "__main__":
    query = "What is kubernetes?"
    result = run_llm(query=query,chat_history=[])
    print(result["result"])