import cv2
import time
import requests
import numpy as np
from io import BytesIO
from PIL import Image

class CameraStream:
    """Handles streaming from iPhone camera to computer."""
    
    def __init__(self, camera_url=None, capture_interval=3):
        """
        Initialize camera stream.
        
        Args:
            camera_url: URL for the iPhone camera stream
            capture_interval: Interval between frame captures in seconds
        """
        self.camera_url = camera_url
        self.capture_interval = capture_interval
        self.last_capture_time = 0
        self.camera = None
        
    def connect_to_ip_camera(self, url):
        """Connect to IP camera app on iPhone."""
        self.camera_url = url
        print(f"Connected to IP camera at {url}")
        
    def connect_to_usb_camera(self, camera_id=0):
        """Connect to iPhone via USB using webcam interface."""
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            raise Exception(f"Could not open camera with ID {camera_id}")
        print(f"Connected to USB camera with ID {camera_id}")
        
    def capture_frame(self):
        """Capture a single frame from the camera, respecting the capture interval."""
        current_time = time.time()
        
        # Check if enough time has passed since the last capture
        if current_time - self.last_capture_time < self.capture_interval:
            return None
            
        self.last_capture_time = current_time
        
        if self.camera_url:
            # IP Camera approach
            try:
                response = requests.get(self.camera_url)
                img = Image.open(BytesIO(response.content))
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                return frame
            except Exception as e:
                print(f"Error capturing from IP camera: {e}")
                return None
        elif self.camera:
            # USB Camera approach
            success, frame = self.camera.read()
            if success:
                return frame
            else:
                print("Error capturing from USB camera")
                return None
        else:
            print("No camera connected")
            return None
    
    def release(self):
        """Release camera resources."""
        if self.camera:
            self.camera.release()