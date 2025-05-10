#!/usr/bin/env python3
"""
Main script for the LeetCode Auto-Solver system.
Default to Camera ID 1 (iPhone back camera).
"""

import time
import os
import argparse
import sys

# Import our modules
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
    parser.add_argument('--camera-id', type=int, default=1,  # Changed default to 1
                      help='Camera ID for USB camera (default: 1)')
    parser.add_argument('--interval', type=int, default=3,
                      help='Frame capture interval in seconds (default: 3)')
    
    # API key argument
    parser.add_argument('--api-key', 
                      help='API key for the LLM service (or set OPENAI_API_KEY env var)')
    
    # Output arguments
    parser.add_argument('--output-dir', default='solutions',
                      help='Directory to save output files (default: solutions)')
    
    # Mode arguments
    parser.add_argument('--continuous', action='store_true',
                      help='Run in continuous mode (keep capturing frames)')
    
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize components
    camera = CameraStream(capture_interval=args.interval)
    processor = ImageProcessor()
    parser = ProblemParser()
    output_handler = OutputHandler(output_dir=args.output_dir)
    
    # Try to initialize code generator
    try:
        generator = CodeGenerator(api_key=args.api_key)
        generator_initialized = True
    except ValueError as e:
        print(f"Warning: {e}")
        print("System will run without code generation capability.")
        print("Set the OPENAI_API_KEY environment variable or provide it with --api-key")
        generator_initialized = False
    
    # Connect to camera
    try:
        if args.camera_type == 'ip':
            camera.connect_to_ip_camera(args.camera_url)
        else:
            print(f"Connecting to USB camera ID {args.camera_id} (iPhone back camera)...")
            camera.connect_to_usb_camera(args.camera_id)
    except Exception as e:
        print(f"Error connecting to camera: {e}")
        sys.exit(1)
    
    print(f"LeetCode Auto-Solver started")
    print(f"Using camera ID {args.camera_id}")
    print(f"Capturing frames every {args.interval} seconds")
    print("Press Ctrl+C to stop")
    
    try:
        frame_count = 0
        while True:
            # Capture frame
            frame = camera.capture_frame()
            
            if frame is not None:
                frame_count += 1
                print(f"\nProcessing frame #{frame_count}...")
                
                # Save the captured frame
                capture_path = os.path.join(args.output_dir, f"capture_{frame_count}.jpg")
                os.makedirs(os.path.dirname(capture_path), exist_ok=True)
                processor.save_frame(frame, capture_path)
                
                # Process frame
                problem_text, function_signature_text, test_cases_text = processor.process_frame(frame)
                
                # Parse content
                problem_data = parser.parse_content(problem_text, function_signature_text, test_cases_text)
                
                # Check if we have valid problem data
                if not problem_data.get('function_signatures') or not problem_data.get('test_cases'):
                    print("Warning: Insufficient problem data extracted. Skipping code generation.")
                    
                    # Save extracted text for debugging
                    with open(os.path.join(args.output_dir, f"extracted_{frame_count}.txt"), "w") as f:
                        f.write(f"Problem:\n{problem_text}\n\n")
                        f.write(f"Function:\n{function_signature_text}\n\n")
                        f.write(f"Tests:\n{test_cases_text}\n\n")
                    
                    if not args.continuous:
                        print("No valid problem data found. Exiting.")
                        break
                    continue
                
                # Generate solution if code generator is available
                if generator_initialized:
                    print("Generating solution...")
                    solution = generator.generate_solution(problem_data)
                    
                    # Save and display the solution
                    filepath = output_handler.save_solution(
                        solution, 
                        filename=f"solution_{frame_count}.py"
                    )
                    output_handler.open_in_vscode(filepath)
                    
                    print(f"Solution generated and saved to {filepath}")
                
                # Exit if not in continuous mode
                if not args.continuous:
                    break
                
                # Wait for user to continue in continuous mode
                input("Press Enter to capture another frame or Ctrl+C to exit...")
            
            # Sleep to control the loop
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting LeetCode Auto-Solver")
    finally:
        camera.release()

if __name__ == "__main__":
    main()