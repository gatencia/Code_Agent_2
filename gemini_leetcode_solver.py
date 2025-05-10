#!/usr/bin/env python3
"""
LeetCode Vision Solver using Google's Gemini API.
This script captures images of LeetCode problems and uses Gemini's vision capabilities
to extract information and generate solutions directly.
"""

import os
import sys
import time
import argparse
import json
import cv2
from datetime import datetime
from PIL import Image
import google.generativeai as genai

# System prompt for Gemini
SYSTEM_PROMPT = """
You are an expert LeetCode problem solver. You will analyze a screenshot of a LeetCode problem.
Your task is to:
1. Extract the problem statement
2. Extract all function signatures
3. Extract the test cases
4. Generate a correct solution that passes all test cases

You will see three main sections in the LeetCode interface:
- Left side: Problem statement (white background with "Scenario" heading)
- Middle: Function definitions (code editor with syntax highlighting)
- Right side: Test cases and terminal output

Respond with JSON containing these fields:
- problem_statement: The full problem description
- function_signatures: Array of function signatures
- test_cases: Array of test cases with inputs and expected outputs
- solution: Your complete code solution
"""

# User prompt for Gemini
USER_PROMPT = """
This image shows a LeetCode problem. Please:
1. Extract the problem details
2. Generate a working solution

For the solution, focus on implementing the specific functions shown in the editor.
Make sure your solution passes all the test cases visible in the image.

IMPORTANT: Respond with a JSON object containing these fields:
- problem_statement: The full problem description
- function_signatures: Array of function signatures
- test_cases: Array of test cases with inputs and expected outputs
- solution: Your complete code solution
"""

class GeminiLeetCodeSolver:
    """Uses Google's Gemini to solve LeetCode problems from images."""
    
    def __init__(self, output_dir="solutions", api_key=None):
        """
        Initialize the LeetCode Vision Solver with Gemini.
        
        Args:
            output_dir: Directory to save solutions
            api_key: Google API key
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required - set GOOGLE_API_KEY or provide with --api-key")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Use the Gemini Pro Vision model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-pro-exp-03-25",
            generation_config={
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 0,
                "max_output_tokens": 8192,
            },
            system_instruction=SYSTEM_PROMPT
        )
    
    def capture_from_camera(self, camera_id=1):
        """
        Capture an image from the camera.
        
        Args:
            camera_id: Camera device ID to use
            
        Returns:
            str: Path to the captured image
        """
        print(f"Initializing camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise Exception(f"Could not open camera with ID {camera_id}")
        
        print("Camera initialized. Press SPACE to capture or ESC to cancel.")
        
        # Create a window
        window_name = "LeetCode Capture (Press SPACE to capture, ESC to cancel)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Camera warm-up time
        time.sleep(2)
        
        image_path = None
        try:
            while True:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue
                
                # Display the frame
                cv2.imshow(window_name, frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                
                # If space is pressed, save the frame
                if key == 32:  # Space key
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(self.output_dir, f"leetcode_{timestamp}.jpg")
                    cv2.imwrite(image_path, frame)
                    print(f"Image captured and saved to {image_path}")
                    break
                
                # If escape is pressed, exit
                elif key == 27:  # Escape key
                    print("Capture cancelled")
                    break
        finally:
            # Release the camera and close windows
            cap.release()
            cv2.destroyAllWindows()
        
        return image_path
    
    def handle_heic_conversion(self, image_path):
        """
        Convert HEIC/HEIF images to JPEG format for compatibility.
        
        Args:
            image_path: Path to the image
            
        Returns:
            str: Path to converted image (or original if no conversion needed)
        """
        # If not a HEIC/HEIF file, return original path
        if not image_path.lower().endswith(('.heic', '.heif')):
            return image_path
            
        # Create a JPG path
        jpg_path = os.path.splitext(image_path)[0] + "_converted.jpg"
        
        # Try multiple methods for conversion
        try:
            # Method 1: Using ImageMagick if available
            import subprocess
            try:
                print("Attempting to convert HEIC using ImageMagick...")
                subprocess.run(['magick', 'convert', image_path, jpg_path], check=True)
                print(f"Converted HEIC to JPG using ImageMagick: {jpg_path}")
                return jpg_path
            except (subprocess.SubprocessError, FileNotFoundError):
                print("ImageMagick not available or failed")
                
            # Method 2: Using sips on macOS
            if sys.platform == 'darwin':  # macOS
                try:
                    print("Attempting to convert HEIC using sips (macOS)...")
                    subprocess.run(['sips', '-s', 'format', 'jpeg', image_path, '--out', jpg_path], check=True)
                    print(f"Converted HEIC to JPG using sips: {jpg_path}")
                    return jpg_path
                except subprocess.SubprocessError:
                    print("sips conversion failed")
            
            # Try other methods as needed...
            print("All conversion methods failed. Proceeding with original file.")
            return image_path
                
        except Exception as e:
            print(f"Warning: All HEIC conversion methods failed: {e}")
            print("Proceeding with original file, but this might cause issues.")
            return image_path
    
    def process_image_with_gemini(self, image_path):
        """
        Process an image using Gemini.
        
        Args:
            image_path: Path to the image to process
            
        Returns:
            dict: Extracted information and solution
        """
        print(f"Processing image with Gemini: {image_path}")
        
        # Handle HEIC/HEIF files by converting to JPG first
        image_path = self.handle_heic_conversion(image_path)
        
        try:
            # Load the image using PIL
            img = Image.open(image_path)
            
            # Generate content using Gemini
            response = self.model.generate_content([USER_PROMPT, img])
            
            # Get the text response
            result_text = response.text
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise
        
        # Try to parse JSON response
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in result_text:
                json_text = result_text.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_text)
            elif "```" in result_text and "{" in result_text:
                # Try to find any code block that might contain JSON
                for block in result_text.split("```"):
                    if block.strip().startswith("{") and block.strip().endswith("}"):
                        try:
                            result = json.loads(block.strip())
                            break
                        except:
                            continue
                else:
                    # No valid JSON block found
                    raise ValueError("No valid JSON found in code blocks")
            else:
                # Try to extract JSON from the text
                try:
                    # Look for a JSON object in the text
                    start_idx = result_text.find("{")
                    end_idx = result_text.rfind("}") + 1
                    if start_idx != -1 and end_idx != -1:
                        json_text = result_text[start_idx:end_idx]
                        result = json.loads(json_text)
                    else:
                        raise ValueError("No JSON object found in text")
                except:
                    # Not JSON, extract solution from the text
                    solution = result_text
                    if "```python" in result_text:
                        solution = result_text.split("```python")[1].split("```")[0].strip()
                    elif "```" in result_text:
                        solution = result_text.split("```")[1].split("```")[0].strip()
                    
                    result = {
                        "problem_statement": "Extracted from image",
                        "function_signatures": [],
                        "test_cases": [],
                        "solution": solution
                    }
        except Exception as e:
            print(f"Warning: Could not parse response as JSON: {e}")
            print("Using raw text instead.")
            
            # Extract any Python code if present
            solution = result_text
            if "```python" in result_text:
                solution = result_text.split("```python")[1].split("```")[0].strip()
            elif "```" in result_text:
                solution = result_text.split("```")[1].split("```")[0].strip()
            
            result = {
                "problem_statement": "Could not extract automatically.",
                "function_signatures": [],
                "test_cases": [],
                "solution": solution
            }
        
        return result
    
    def save_solution(self, result, image_filename):
        """
        Save the solution and extracted information.
        
        Args:
            result: The result from the LLM
            image_filename: Name of the original image file
            
        Returns:
            str: Path to the saved solution file
        """
        # Base filename without extension
        base_filename = os.path.splitext(os.path.basename(image_filename))[0]
        
        # Save the solution
        solution_file = os.path.join(self.output_dir, f"{base_filename}_solution.py")
        with open(solution_file, "w") as f:
            f.write(result.get("solution", "# No solution generated"))
        
        # Save the full result as JSON
        info_file = os.path.join(self.output_dir, f"{base_filename}_info.json")
        with open(info_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Solution saved to {solution_file}")
        print(f"Extracted information saved to {info_file}")
        
        return solution_file
    
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
            import subprocess
            subprocess.run(['code', filepath], check=True)
            return True
        except Exception as e:
            print(f"Could not open VS Code: {e}")
            print(f"File saved at {filepath}")
            return False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='LeetCode Gemini Solver')
    
    parser.add_argument('--api-key', 
                       help='API key for Google Gemini (or set GOOGLE_API_KEY)')
    parser.add_argument('--camera-id', type=int, default=1,
                       help='Camera ID for capturing images (default: 1)')
    parser.add_argument('--image-path',
                       help='Path to an existing image to process (instead of capturing)')
    parser.add_argument('--output-dir', default='solutions',
                       help='Directory to save solutions (default: solutions)')
    
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_args()
    
    try:
        # Check if google.generativeai is installed
        try:
            import google.generativeai as genai
        except ImportError:
            print("The 'google-generativeai' package is not installed. Installing now...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai pillow"])
            import google.generativeai as genai
            print("Successfully installed the 'google-generativeai' package.")
        
        solver = GeminiLeetCodeSolver(output_dir=args.output_dir, api_key=args.api_key)
        
        # Get image path - either from capture or provided path
        image_path = args.image_path
        if not image_path:
            print("\nPreparing to capture LeetCode problem from camera...")
            image_path = solver.capture_from_camera(camera_id=args.camera_id)
            if not image_path:
                print("No image captured. Exiting.")
                return
        elif not os.path.exists(image_path):
            print(f"Error: Image file {image_path} not found")
            return
        
        # Process the image
        result = solver.process_image_with_gemini(image_path)
        
        # Save and open the solution
        solution_file = solver.save_solution(result, image_path)
        solver.open_in_vscode(solution_file)
        
        print("\nDone! Your LeetCode solution is ready.")
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()