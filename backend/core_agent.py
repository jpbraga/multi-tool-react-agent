import os
from typing import Any, Dict, List
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.chat_models import ChatOllama
from tools.shell_tools  import run_shell
from tools.file_tools import create_file_in_folder, delete_file, list_files_in_directory, load_file
from tools.os_tools import get_os
from tools.utils_tools import get_current_date_time
from tools.vdb_tools import retrieve_context_info

load_dotenv()

def find_tool_by_name(name: str, tools: List[Tool]) -> Tool:
    for tool in tools:
        if tool.name == name:
            return tool
    return None

def chat_with_agent(question: str, chat_history: List[Dict[str, Any]]) -> str:
    print("React Agent")
    
    tools = [retrieve_context_info, get_current_date_time, PythonREPLTool(), get_os, run_shell, create_file_in_folder, load_file, list_files_in_directory, delete_file]    
    
    llm = ChatOpenAI(temperature=0, model_name=os.getenv("OPENAI_MODEL_NAME"), stop=["\nObservation"])
    # llm = ChatOllama(temperature=0.3, model="llama3.1")
    
#     template = """
#     Answer the following questions as best you can. You have access to the following tools:

#     {tools}
#     The tools can be used as many times as needed to answer the question. You have the liberty to change the parameters as needed to better use the tools.
#     You have the hability to use Python to resolve problems. If you need to use Python, use the PythonREPLTool tool.
#     Whenever you need to use Python, ALWAYS debug the code until it runs with no problems, and ALWAYS output the result of the execution. Also ALWAYS display code you've written to the user.
#     Always check before installing a new package and always check if it's installed after you try
#     For shell commands be sure to target the OS you are running on.
#     For shell executions, be sure to open a shell before issue a command, and close it after you finish.
#     For every shell execution that changes and/or creates something in the system, you must check it before executing another action to complete the task.

#     Use the following format, when you do not need to take any action:

#     Question: the input question you must answer
#     Thought: you should always think about what to do
#     Action: the action to take, should be one of [{tool_names}]
#     Action Input: the input to the action
#     Observation: the result of the action
#     ... (this Thought/Action/Action Input/Observation can repeat N times)
#     Thought: I now know the final answer
#     Final Answer: the final answer to the original input question

#     Begin!

#     {chat_history}
    
#     Question: {input}
#     Thought: {agent_scratchpad}
# """

    template = """
    Answer the following questions as accurately and efficiently as possible. You have access to the following tools:

    {tools}
    
    You can use the tools as many times as needed to answer the question, with the freedom to adjust parameters for optimal usage. You can also use Python for problem-solving with the PythonREPLTool.

    Guidelines for any code execution:
        Always debug the code until it runs without errors.
        Output the execution result and display the code written to the user.
    
    Guidelines for Shell Commands:
        Ensure compatibility with the OS you're running on.
        Open a shell before issuing a command and close it after completion.
        For actions that change or create system settings, always verify the changes before proceeding.
    
    Format:
        When responding to a question, follow this structure:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

    Begin!

    Chat History:
    {chat_history}

    New Question:
    Question: {input}
    Thought: {agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(template=template).partial(
        tools=render_text_description(tools), 
        tool_names=", ".join([t.name for t in tools])
    )

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_execution_time=120, max_iterations=120)

    # chat_history_str = format_chat_history(chat_history)
    result = agent_executor.invoke(
        input={
            "input": question,
            "chat_history": chat_history
        }
    )
    # chat_history.append({
    #     "question": question,
    #     "thought": "Your thought process here",  # Update with actual thought if needed
    #     "action": "The action taken",
    #     "action_input": "The input to the action",
    #     "observation": "The result of the action",
    #     "final_answer": result
    # })
    new_result = {
        "query": result["input"],
        "result": result["output"]
        # "source_documents": result["context"]
        
    }
    return new_result

def format_chat_history(chat_history: List[Dict[str, Any]]) -> str:
    formatted_history = ""
    for entry in chat_history:
        formatted_history += f"Question: {entry['question']}\n"
        formatted_history += f"Thought: {entry['thought']}\n"
        formatted_history += f"Action: {entry['action']}\n"
        formatted_history += f"Action Input: {entry['action_input']}\n"
        formatted_history += f"Observation: {entry['observation']}\n"
        formatted_history += f"Final Answer: {entry['final_answer']}\n\n"
    return formatted_history


if __name__ == "__main__":
    print("Hello React Langchain")
    # res = chat_with_agent("Quais opcoes de pizza disponiveis para entrega?", [])
    create_file_in_folder("{'folder_path': 'NODE_POC_PROJECT', 'file_name': 'dummy.txt', 'content': 'This is a dummy file to create the directory.'}")