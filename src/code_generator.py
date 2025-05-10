import openai
import os
import json

class CodeGenerator:
    """Generates code solutions using LLM."""
    
    def __init__(self, api_key=None):
        """
        Initialize the code generator.
        
        Args:
            api_key: API key for the LLM service
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for code generation")
        
        openai.api_key = self.api_key
    
    def build_prompt(self, problem_data):
        """
        Build a prompt for the LLM based on problem data.
        
        Args:
            problem_data: Structured problem data
            
        Returns:
            str: The constructed prompt
        """
        function_signatures_str = "\n".join(problem_data.get('function_signatures', []))
        
        test_cases_str = ""
        for i, test in enumerate(problem_data.get('test_cases', [])):
            test_cases_str += f"Test {i+1}: {test['operation']} {test['input']} -> {test['expected_output']}\n"
        
        prompt = f"""
You are a competitive programming expert. Write Python code to solve the following problem:

Problem Statement:
{problem_data.get('problem_statement', '')}

Function Signature:
{function_signatures_str}

Test Cases:
{test_cases_str}

Implement the solution that passes all test cases. The code should be efficient and follow best practices.
Only provide the implementation of the required methods, no extra explanations.
"""
        
        return prompt
    
    def generate_solution(self, problem_data):
        """
        Generate a code solution using the LLM.
        
        Args:
            problem_data: Structured problem data
            
        Returns:
            str: The generated code solution
        """
        prompt = self.build_prompt(problem_data)
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a competitive programming expert who writes clean, efficient, and correct Python code solutions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more deterministic output
            max_tokens=1000
        )
        
        # Extract the solution from the response
        solution = response.choices[0].message.content.strip()
        
        # Filter to keep only the code implementation
        code_lines = []
        in_code_block = False
        
        for line in solution.split('\n'):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if in_code_block or ('```' not in solution):
                code_lines.append(line)
                
        return '\n'.join(code_lines)