import platform
from langchain.agents import tool

@tool
def get_os(param:str):
    """
    Returns the operating system name.
    """
    return platform.system()