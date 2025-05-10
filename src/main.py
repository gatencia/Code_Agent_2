import time
import os
import argparse

from camera_stream import CameraStream
from image_processor import ImageProcessor
from problem_parser import ProblemParser
from code_generator import CodeGenerator
from output_handler import OutputHandler

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='LeetCode Auto-Solver')
    
    # Camera arguments
    parser.add_argument('--camera-type', choices=['ip', 'usb'], default='usb',
                      help='Type of camera connection (default: usb)')
    parser.add_argument('--camera-url', default='http://192.168.1.100:8080/shot.jpg',
                      help='URL for IP camera (default: http://192.168.1.100:8080/shot.jpg)')
    parser.add_argument('--camera-id', type=int, default=0,
                      help='Camera ID for USB camera (default: 0)')
    parser.add_argument('--interval', type=int, default=3,
                      help='Frame capture interval in seconds (default: 3)')
    
    # API key argument
    parser.add_argument('--api-key', help='API key for the LLM service')
    
    # Output arguments
    parser.add_argument('--output-dir', default='.',
                      help='Directory to save output files (default: current directory)')
    
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_args()
    
    # Initialize components
    camera = CameraStream(capture_interval=args.interval)
    processor = ImageProcessor()
    parser = ProblemParser()
    
    try:
        generator = CodeGenerator(api_key=args.api_key)
    except ValueError as e:
        print(f"Error initializing code generator: {e}")
        print("Please provide an API key with --api-key or set the OPENAI_API_KEY environment variable")
        return
    
    output_handler = OutputHandler(output_dir=args.output_dir)
    
    # Connect to camera
    if args.camera_type == 'ip':
        camera.connect_to_ip_camera(args.camera_url)
    else:
        camera.connect_to_usb_camera(args.camera_id)
    
    print(f"LeetCode Auto-Solver started")
    print(f"Capturing frames every {args.interval} seconds")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Capture frame
            frame = camera.capture_frame()
            
            if frame is not None:
                print("Frame captured, processing...")
                
                # Process frame
                problem_text, function_signature_text, test_cases_text = processor.process_frame(frame)
                
                # Parse content
                problem_data = parser.parse_content(problem_text, function_signature_text, test_cases_text)
                
                # Generate solution
                print("Generating solution...")
                solution = generator.generate_solution(problem_data)
                
                # Save and display the solution
                filepath = output_handler.save_solution(solution)
                output_handler.open_in_vscode(filepath)
                
                print(f"Solution generated and saved to {filepath}")
                
                # Wait for user to continue
                input("Press Enter to capture another frame or Ctrl+C to exit...")
            
            # Sleep to control the loop
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting LeetCode Auto-Solver")
    finally:
        camera.release()

if __name__ == "__main__":
    main()