#!/usr/bin/env python3
"""
Test script for LeetCode Auto-Solver camera capture functionality.
Default to Camera ID 1 (iPhone back camera).
"""

import cv2
import sys
import time
import os
import argparse

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our camera module
from camera_stream import CameraStream

def list_available_cameras(max_cameras=10):
    """List all available camera devices and their status."""
    print("Checking available cameras...")
    available_cameras = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"Camera {i}: Available and working")
            else:
                print(f"Camera {i}: Available but not returning frames")
            cap.release()
        else:
            print(f"Camera {i}: Not available")
    
    return available_cameras

def test_camera_capture(camera_id=1, num_frames=5, save_frames=True):
    """Test capturing frames from the specified camera."""
    print(f"\nTesting camera {camera_id}...")
    
    # Initialize our camera stream
    camera = CameraStream(capture_interval=1)
    try:
        camera.connect_to_usb_camera(camera_id)
    except Exception as e:
        print(f"Error connecting to camera: {e}")
        return False
    
    # Create directory for test frames if saving is enabled
    if save_frames:
        os.makedirs("test_frames", exist_ok=True)
    
    # Capture multiple frames
    success_count = 0
    for i in range(num_frames):
        print(f"Capturing frame {i+1}/{num_frames}...")
        frame = camera.capture_frame()
        
        if frame is not None:
            success_count += 1
            print(f"Frame {i+1} captured successfully! Shape: {frame.shape}")
            
            # Save the frame if requested
            if save_frames:
                filename = f"test_frames/frame_{camera_id}_{i+1}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved frame to {filename}")
        else:
            print(f"Failed to capture frame {i+1}")
        
        # Wait a bit between captures
        time.sleep(1)
    
    # Release the camera
    camera.release()
    
    # Report results
    success_rate = (success_count / num_frames) * 100
    print(f"\nCapture test completed for camera {camera_id}")
    print(f"Success rate: {success_rate:.1f}% ({success_count}/{num_frames} frames captured)")
    
    return success_count > 0

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Camera Capture Test')
    
    parser.add_argument('--camera-id', type=int, default=1,  # Default to camera ID 1
                      help='Camera ID to test (default: 1)')
    parser.add_argument('--frames', type=int, default=5,
                      help='Number of frames to capture (default: 5)')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("=== iPhone Camera Capture Test ===")
    print(f"Testing camera ID {args.camera_id} (iPhone back camera)")
    
    # List available cameras for information
    available_cameras = list_available_cameras()
    
    if args.camera_id not in available_cameras:
        print(f"\nWarning: Camera {args.camera_id} was not detected as available.")
        proceed = input("Do you want to try anyway? (y/n): ")
        if proceed.lower() != 'y':
            return
    
    # Test the selected camera
    success = test_camera_capture(args.camera_id, num_frames=args.frames)
    
    if success:
        print("\n✅ Camera test successful! Your iPhone camera is working properly.")
        print("You can now run the full LeetCode Auto-Solver system using this camera.")
    else:
        print("\n❌ Camera test failed. Please check your iPhone connection and try again.")
        print("Make sure your iPhone is unlocked and you've trusted this computer.")

if __name__ == "__main__":
    main()