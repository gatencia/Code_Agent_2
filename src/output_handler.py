import os
import subprocess

class OutputHandler:
    """Handles presenting the generated solution to the user."""
    
    def __init__(self, output_dir="."):
        """
        Initialize the output handler.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        
    def save_solution(self, solution, filename="solution.py"):
        """
        Save the solution to a file.
        
        Args:
            solution: The code solution to save
            filename: The filename to save to
            
        Returns:
            str: The path to the saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(solution)
            
        return filepath
    
    def open_in_vscode(self, filepath):
        """
        Open the solution file in Visual Studio Code.
        
        Args:
            filepath: Path to the file to open
            
        Returns:
            bool: Whether the operation was successful
        """
        try:
            # Try to use code command to open VS Code
            subprocess.run(['code', filepath], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Could not open VS Code. File saved at {filepath}")
            return False