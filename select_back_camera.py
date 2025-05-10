#!/usr/bin/env python3
"""
Script to help identify and select the iPhone's back camera.
This will test each available camera and save a sample image from each.
"""

import cv2
import os
import time

def list_and_test_all_cameras(max_cameras=5):
    """List all available cameras and capture a test image from each."""
    print("Testing all available cameras...")
    os.makedirs("camera_test", exist_ok=True)
    
    # Test each possible camera index
    for camera_id in range(max_cameras):
        print(f"\nTesting camera ID {camera_id}...")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"  Camera {camera_id}: Not available")
            continue
            
        # Try to capture a frame
        ret, frame = cap.read()
        
        if not ret:
            print(f"  Camera {camera_id}: Connected but couldn't capture frame")
            cap.release()
            continue
            
        # We got a frame, save it
        filename = f"camera_test/camera_{camera_id}_sample.jpg"
        cv2.imwrite(filename, frame)
        
        # Get camera properties if possible
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        print(f"  Camera {camera_id}: Working! Frame size: {width}x{height}")
        print(f"  Sample image saved to: {filename}")
        
        # Release the camera
        cap.release()
        
    print("\nAll cameras tested. Check the 'camera_test' folder to see which one is your iPhone's back camera.")
    print("Look for the highest resolution image that shows what's in front of your iPhone (not your face).")

def select_and_confirm_camera():
    """Let the user select the correct camera and confirm it's working."""
    # First list all cameras
    list_and_test_all_cameras()
    
    # Ask user which one is the back camera
    camera_id = input("\nAfter reviewing the sample images, which camera ID is your iPhone's back camera? ")
    
    try:
        camera_id = int(camera_id)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Test the selected camera with continuous preview
    print(f"\nTesting camera {camera_id} (iPhone back camera)...")
    print("A window will open showing the camera feed.")
    print("Press 'q' to exit the preview.")
    
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_id}")
        return
    
    # Create window
    window_name = f"Camera {camera_id} Preview (iPhone Back Camera)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Show preview
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error capturing frame")
            break
            
        # Display the frame
        cv2.imshow(window_name, frame)
        
        # Press q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nCamera {camera_id} confirmed as your iPhone's back camera.")
    print(f"Use --camera-id {camera_id} when running the LeetCode Auto-Solver.")
    
    # Save the camera id to a config file for future use
    with open("camera_config.txt", "w") as f:
        f.write(f"CAMERA_ID={camera_id}\n")
    
    print(f"This camera ID has been saved to camera_config.txt for future reference.")

if __name__ == "__main__":
    print("=== iPhone Back Camera Selection Tool ===")
    select_and_confirm_camera()