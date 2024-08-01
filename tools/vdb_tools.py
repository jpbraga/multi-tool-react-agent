
import ast
import os
from xml.dom.minidom import Document
from typing import Any, Optional, List
from langchain.agents import tool
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
    
@tool
def retrieve_context_info(query: str) -> str:
    """Returns context information about ivegan platform such as restaurants, menu items and their composition, work schedule information and payment methods.
    Input params: context to be searched in a vector database"""
    embeddings = OpenAIEmbeddings(model=os.environ["OPENAI_EMBEDDINGS_MODEL"])
    index_names = ast.literal_eval(os.environ['MULTI_INDEX_LIST'])
    vector_stores = [PineconeVectorStore(index_name=index_name, embedding=embeddings) for index_name in index_names]
    
    all_retrievers = [store.as_retriever() for store in vector_stores]
    combined_retriever = CombinedRetriever(all_retrievers)
    docs = combined_retriever.invoke(input=query)
    rdocs = ""
    for i, document in enumerate(docs):
        rdocs += (f"Document {i} page_content:")
        rdocs += (document.page_content)
        rdocs += ("\n")
    return rdocs