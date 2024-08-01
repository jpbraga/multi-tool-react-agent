from datetime import datetime
from langchain.agents import tool

@tool
def get_current_date_time(i:str = None) -> str:
    """Returns a value representing the current date and time for the users location
    This function receives no parameters"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")