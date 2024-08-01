import ast
import subprocess
import platform
import os
from langchain.agents import tool

@tool
def list_files_in_directory(directory_path: str) -> list:
    """
    Lists files in the given directory path and returns their names and sizes.
    
    Parameters:
        directory_path (str): The path to the directory to list files from.
    
    Returns:
        list: A list of dictionaries containing the name and size of each file in bytes.
    """
    files_info = []

    try:
        # Check if the provided path is a directory
        if not os.path.isdir(directory_path):
            raise ValueError(f"The path '{directory_path}' is not a directory.")
        
        # List files in the directory
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            
            # Only process files (skip directories)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files_info.append({"name": file_name, "size": file_size})
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return files_info

@tool
def create_file_in_folder(file_definition:str) -> str:
    """
    Creates a file within a specified folder and writes given content to it.
    
    The expected input for this function is a string in the following format:
    "{'folder_path': 'foo', 'file_name': 'bar', 'content': 'foobar'}"
    
    Parameters:
        file_definition (str): A string representation of a dictionary containing:
            - folder_path (str): The path to the folder where the file will be created.
            - file_name (str): The name of the file to be created.
            - content (str): The content to be written to the file.
    
    Returns:
        str: A message indicating the result of the file creation process.
        
    The input parameter must not contain any format specifiers such as:
    ```json
    ```
    
    Example input:
    "{'folder_path': 'foo', 'file_name': 'bar', 'content': 'foobar'}"
    
    Example output:
    "File 'bar' created successfully in 'foo' with the given content."
    """
    try:
        fDef = ast.literal_eval(file_definition)
        print(fDef)
        # Create the folder if it doesn't exist
        if not os.path.exists(fDef['folder_path']):
            os.makedirs(fDef['folder_path'])
        
        # Full file path
        file_path = os.path.join(fDef['folder_path'] , fDef['file_name'] )
        
        # Create and write to the file
        with open(file_path, 'w') as file:
            file.write(fDef['content'])
        
        return(f"File '{fDef['file_name']}' created successfully in '{fDef['folder_path']}' with the given content.")
    except Exception as e:
        return(f"An error occurred: {e}")
    
@tool
def load_file(file_path: str) -> str:
    """
    Loads a file from the given path and returns its contents.
    
    Parameters:
        file_path (str): The path to the file to be loaded.
    
    Returns:
        str: The contents of the file.
        
    Raises:
        FileNotFoundError: If the file does not exist at the given path.
        IOError: If there is an error reading the file.
    """
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except IOError as e:
        return f"Error: An error occurred while reading the file. {e}"
    
@tool
def delete_file(file_path: str) -> str:
    """
    Deletes a file at the given path.
    
    Parameters:
        file_path (str): The path to the file to be deleted.
    
    Returns:
        str: A message indicating the result of the delete operation.
    """
    try:
        # Check if the file exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"File '{file_path}' has been deleted successfully."
        else:
            return f"File '{file_path}' does not exist."
    except Exception as e:
        return f"An error occurred: {e}"