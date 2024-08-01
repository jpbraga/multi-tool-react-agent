import subprocess
import platform
import subprocess
import platform
import threading
import queue
from langchain.agents import tool

class ShellManager:
    def __init__(self):
        self.shell_process = None
        self.output_queue = queue.Queue()
        self.output_thread = None
        self.stop_thread = threading.Event()

    def open_shell(self) -> str:
        """
        Opens a shell process based on the system type and prepares it to execute commands.
        
        Returns:
            str: A message indicating the status of the shell opening process.
            
        Functionality:
            1. Determines the system type (Windows or Linux) and selects the appropriate shell command.
            2. Opens a shell process using subprocess.Popen with stdin, stdout, and stderr configured for text mode.
            3. Starts a background thread to read the shell's output.
            4. Handles any exceptions that occur during the process initiation.
            5. Returns a status message indicating whether the shell was opened successfully or if it was already open.
        """
        cmd = "cmd" if platform.system() == "Windows" else "bin/bash"
        if self.shell_process is None:
            try:
                self.shell_process = subprocess.Popen(
                    [cmd],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Start the output reading thread
                self.output_thread = threading.Thread(target=self._read_output)
                self.output_thread.daemon = True
                self.output_thread.start()
                return "Shell opened successfully and ready to execute commands"
            except Exception as e:
                return (f"An error occurred: {e}")
        else:
            return "Shell opened successfully and ready to execute commands"
    
    def issue_command(self, command):
        """
        Issues a command to the opened shell.
        """
        if self.shell_process is not None:
            try:
                self.shell_process.stdin.write(command + '\n')
                self.shell_process.stdin.flush()
                return self._get_output()
            except Exception as e:
                return (f"An error occurred: {e}")
        else:
            return("Shell is not opened.")

    def close_shell(self):
        """
        Closes the opened shell process and stops the output thread.
        """
        if self.shell_process is not None:
            self.shell_process.stdin.write('exit\n')
            self.shell_process.stdin.flush()
            self.shell_process.stdin.close()
            self.shell_process.terminate()
            self.shell_process = None
            
            # Stop the output reading thread
            self.stop_thread.set()
            self.output_thread.join()
            self.output_thread = None
            return "Shell closed"
        else:
            return ("Shell is not opened.")

    def _read_output(self):
        """
        Reads the output from the shell process and puts it into a queue.
        """
        while not self.stop_thread.is_set():
            line = self.shell_process.stdout.readline()
            if line:
                self.output_queue.put(line.strip())
            if self.shell_process.poll() is not None:
                break

    def _get_output(self):
        """
        Retrieves all lines from the output queue.
        """
        output = []
        while not self.output_queue.empty():
            output.append(self.output_queue.get())
        return '\n'.join(output)

shell_manager = ShellManager()

# @tool
# def open_shell(cmd:str) -> str:
#     """
#     Opens a shell process based on the system type and prepares it to execute commands.
    
#     Returns:
#         str: A message indicating the status of the shell opening process.
        
#     Functionality:
#         1. Determines the system type (Windows or Linux) and selects the appropriate shell command.
#         2. Opens a shell process using subprocess.Popen with stdin, stdout, and stderr configured for text mode.
#         3. Starts a background thread to read the shell's output.
#         4. Handles any exceptions that occur during the process initiation.
#         5. Returns a status message indicating whether the shell was opened successfully or if it was already open.
#     """
#     return shell_manager.open_shell()

# @tool
# def issue_command(command:str) -> str:
#     """
#     Issues a command to the opened shell and retrieves the output.
    
#     Parameters:
#         command (str): The command to be issued to the shell.
        
#     Returns:
#         str: The output from the shell command execution, or an error message if the shell is not opened or an exception occurs.
        
#     Functionality:
#         1. Checks if the shell process is opened.
#         2. If the shell is opened, writes the command to the shell's standard input and flushes the input buffer.
#         3. Retrieves and returns the output from the shell's standard output by calling _get_output.
#         4. Handles any exceptions that occur during the command issuance and returns an appropriate error message.

#     Important:
#         Some commands do not produce output, so some times you will need to check for it's succesfull execution.
#     """
#     return shell_manager.issue_command(command=command)
    
# @tool
# def close_shell(cmd:str) -> str:
#     """
#     Closes the opened shell process and stops the output thread.
    
#     Returns:
#         str: A message indicating the status of the shell closing process.
        
#     Functionality:
#         1. Checks if the shell process is opened.
#         2. If the shell is opened, writes the 'exit' command to the shell's standard input and flushes the input buffer.
#         3. Closes the shell's standard input, terminates the shell process, and sets the process reference to None.
#         4. Stops the output reading thread by setting the stop_thread event and waiting for the thread to finish.
#         5. Returns a status message indicating whether the shell was successfully closed or if it was not opened.
#     """
#     return shell_manager.close_shell()


@tool
def run_shell(command: str) -> str:
    """
    Useful tool to run a single shell command and receive the output of it.
    
    This function supports running commands on both Windows and Unix-like systems.
    
    Parameters:
        command (str): The shell command to be executed.
        
    Returns:
        str: The output of the command or an error message if the command fails.
    """
    try:
        # Determine the shell to use based on the operating system
        if platform.system() == "Windows":
            result = subprocess.run(["cmd", "/c", command], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"