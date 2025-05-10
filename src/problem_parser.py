import re

class ProblemParser:
    """Parses extracted text to identify problem components."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def extract_problem_statement(self, text):
        """
        Extract the problem statement from the OCR text.
        
        Args:
            text: OCR text from the problem region
            
        Returns:
            str: The problem statement
        """
        # Look for the problem description section
        scenario_match = re.search(r'Scenario(.*?)(?:Unit tests|$)', text, re.DOTALL)
        if scenario_match:
            return scenario_match.group(1).strip()
        return text
    
    def extract_function_signature(self, text):
        """
        Extract function signatures from the OCR text.
        
        Args:
            text: OCR text from the code editor region
            
        Returns:
            list: Function signatures found in the text
        """
        # Look for Python function definitions
        signatures = []
        pattern = r'def\s+(\w+)\s*\((.*?)\)\s*(->\s*\w+)?:'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            signature = match.group(0)
            signatures.append(signature)
            
        return signatures
    
    def extract_test_cases(self, text):
        """
        Extract test cases from the OCR text.
        
        Args:
            text: OCR text from the test cases region
            
        Returns:
            list: Test cases found in the text
        """
        # Look for test cases - patterns vary based on the format
        test_cases = []
        
        # Example pattern matching for test cases like "Add 1, 2, 5 -> [1, 2, 5]"
        pattern = r'(Add|Delete|Median of).*?(\d.*?)(?:is|->)\s*(.*?)$'
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            operation = match.group(1).strip()
            input_values = match.group(2).strip()
            expected_output = match.group(3).strip()
            
            test_case = {
                'operation': operation,
                'input': input_values,
                'expected_output': expected_output
            }
            test_cases.append(test_case)
            
        return test_cases
    
    def parse_content(self, problem_text, function_signature_text, test_cases_text):
        """
        Parse the OCR content into structured problem data.
        
        Args:
            problem_text: OCR text from problem region
            function_signature_text: OCR text from code editor region
            test_cases_text: OCR text from test cases region
            
        Returns:
            dict: Structured problem data
        """
        problem_statement = self.extract_problem_statement(problem_text)
        function_signatures = self.extract_function_signature(function_signature_text)
        test_cases = self.extract_test_cases(test_cases_text)
        
        return {
            'problem_statement': problem_statement,
            'function_signatures': function_signatures,
            'test_cases': test_cases
        }