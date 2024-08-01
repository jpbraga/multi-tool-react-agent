import os
from typing import Any, Dict, List, Optional, Union
from xml.dom.minidom import Document
from dotenv import load_dotenv
from langchain.agents import tool, AgentExecutor, initialize_agent, AgentType, create_react_agent, Agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import Tool
from pydantic import BaseModel, Field
import ast
from langchain import hub
from langchain_core.retrievers import RetrieverLike
from langchain_core.runnables import (
    RunnableConfig
)
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datetime import datetime

load_dotenv()

class CombinedRetriever(RetrieverLike):
    def __init__(self, retrievers):
        self.retrievers = retrievers

    def get_relevant_documents(self, query):
        results = []
        for retriever in self.retrievers:
            # results.extend(retriever.get_relevant_documents(query))
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
def retrieve_context_info(query: str) -> int:
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

@tool
def get_current_date_time(i:str = None) -> int:
    """Returns a value representing the current date and time for the users location
    This function receives no parameters"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def find_tool_by_name(name: str, tools: List[Tool]) -> Tool:
    for tool in tools:
        if tool.name == name:
            return tool
    return None

if __name__ == "__main__":
    print("Hello React Langchain")
    
    tools = [retrieve_context_info,get_current_date_time]
    llm = ChatOpenAI(temperature=0, model_name=os.getenv("OPENAI_MODEL_NAME"), stop=["\nObservation"])#, callbacks=[AgentCallbackHandler()])
    
    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}
    The tools can be used as many times as needed to answer the question. You have the liberty to change the parameters as needed to better use the tools.

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
"""

    prompt = PromptTemplate.from_template(template=template).partial(
        tools=render_text_description(tools), 
        tool_names=", ".join([t.name for t in tools])
    )
    
    
    # intermediate_steps = []
    
    # agent = {"agent_scratchpad": lambda x:format_log_to_str(x["agent_scratchpad"]), "input": lambda x:x["input"]}|prompt | llm | ReActSingleInputOutputParser()
    
    # agent_step = ""
    # while not isinstance(agent_step, AgentFinish):
    #     if isinstance(agent_step, AgentAction):
    #         print("\n*** Agent Action ***")
    #         tool_name = agent_step.tool
    #         tool_to_use = find_tool_by_name(tool_name, tools)
    #         tool_input = agent_step.tool_input
            
    #         print(f"tool_name: {tool_name} ({tool_input})")
    #         observation = tool_to_use.func(str(tool_input))
    #         print(f"Observation: {observation}")
    #         intermediate_steps.append((agent_step, str(observation)))
        
    #     agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
    #         {
    #             "input": "What is the length in characters of the words DOG, CAT and BIRD separatedly and sum them up afterwards?", 
    #             "agent_scratchpad": intermediate_steps
    #         }
    #     )



react_prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

result = agent_executor.invoke(
    input={
        # "input": "What is the length in characters of the words DOG, CAT, the sentence 'today is a good day to die' and BIRD separately and the total representing the sum of the lengths?"
        "input": "Que restaurantes estao fechados agora na regiao de botafogo?"
    }
)

print(result)
