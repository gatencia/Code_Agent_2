import cv2
import numpy as np
from paddleocr import PaddleOCR

class ImageProcessor:
    """Processes frames to extract text using OCR."""
    
    def __init__(self):
        """Initialize the OCR engine and other processors."""
        # Initialize PaddleOCR with English language
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
    def preprocess_image(self, frame):
        """Preprocess the image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to enhance text
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        return thresh
    
    def detect_regions(self, frame):
        """
        Detect the regions of interest in the frame.
        
        Returns:
            tuple: (problem_region, code_editor_region, test_cases_region)
        """
        # This is a simplified approach - in a production system,
        # we would use more sophisticated methods to detect regions
        
        height, width = frame.shape[:2]
        
        # Based on the example images, we'll make some assumptions about regions
        # Left section (problem statement)
        problem_region = frame[0:height, 0:int(width * 0.3)]
        
        # Middle section (code editor)
        code_editor_region = frame[0:height, int(width * 0.3):int(width * 0.7)]
        
        # Right section (test cases)
        test_cases_region = frame[0:height, int(width * 0.7):width]
        
        return problem_region, code_editor_region, test_cases_region
    
    def extract_text(self, image):
        """
        Extract text from an image using OCR.
        
        Args:
            image: The image to extract text from
            
        Returns:
            str: The extracted text
        """
        # Run OCR on the image
        result = self.ocr.ocr(image, cls=True)
        
        # Extract text from OCR results
        texts = []
        for line in result:
            for word in line:
                texts.append(word[1][0])  # Extract the text content
                
        return '\n'.join(texts)
    
    def process_frame(self, frame):
        """
        Process a frame to extract text from different regions.
        
        Args:
            frame: The frame to process
            
        Returns:
            tuple: (problem_text, function_signature, test_cases)
        """
        if frame is None:
            return None, None, None
            
        # Detect regions
        problem_region, code_editor_region, test_cases_region = self.detect_regions(frame)
        
        # Preprocess each region
        problem_preprocessed = self.preprocess_image(problem_region)
        code_preprocessed = self.preprocess_image(code_editor_region)
        tests_preprocessed = self.preprocess_image(test_cases_region)
        
        # Extract text from each region
        problem_text = self.extract_text(problem_preprocessed)
        function_signature = self.extract_text(code_preprocessed)
        test_cases = self.extract_text(tests_preprocessed)
        
        return problem_text, function_signature, test_cases