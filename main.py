from typing import Set
from backend.core_agent import chat_with_agent
from backend.core import run_llm
import streamlit as st
from streamlit_chat import message

st.header("LangChain Documentation Helper Bot")
prompt = st.text_input("Prompt", placeholder="Enter your query...")
    
if ("user_prompt_history" not in st.session_state
    and "chat_answers_history" not in st.session_state
    and "chat_history" not in st.session_state):
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []

def create_sources_string(sources_url: Set[str]) -> str:
    if not sources_url or not has_substring(sources_url, ".html"):
        return ""
    sources_list = list(sources_url)
    sources_list.sort()
    sources_string = "Sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"[{get_page_name(source)}]({source})\n"
    return sources_string

def has_substring(strings, substring):
    for string in strings:
        if substring in string:
            return True
    return False

def get_page_name(url: str) -> str:
    return url.split("/")[-1].replace(".html", "").replace(".", " ").replace("_", " ").capitalize()

if prompt:
    
    with st.spinner("Working..."):
        # generated_response = run_llm(query=prompt, chat_history=st.session_state["chat_history"])
        generated_response = chat_with_agent(question=prompt, chat_history=st.session_state["chat_history"])
        # sources = set([doc.metadata.get("source") for doc in generated_response["source_documents"]])
        
        # formated_response = f"{generated_response['result']}\n\n\n{create_sources_string(sources)}\n"
        
        formated_response = f"{generated_response['result']}\n"
        
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formated_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))
        
if st.session_state["chat_answers_history"]:
    for i, (generated_response, user_query) in enumerate(zip(st.session_state["chat_answers_history"], st.session_state["user_prompt_history"])):
        message(user_query, is_user=True, key=f"user_{i}")
        message(generated_response, is_user=False, key=f"bot_{i}")
    
    
    
    
    