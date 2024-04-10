# Importing necessary libraries
from flask import Flask, render_template, Response
import cv2
import numpy as np

# Creating Flask app
app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Function to generate video frames
def gen_frames():
    lower_green = np.array([35, 100, 100])  # Lower bounds (BGR)
    upper_green = np.array([77, 255, 255])  # Upper bounds (BGR)
    
    # Load background video
    cap_video = cv2.VideoCapture("green.mp4")
    # Webcam feed
    cap_webcam = cv2.VideoCapture(0)
    
    # Check if video captures are opened successfully
    if not cap_video.isOpened() or not cap_webcam.isOpened():
        print("Error opening video capture(s)")
        return
    
    while True:
        ret_video, frame_video = cap_video.read()
        ret_webcam, frame_webcam = cap_webcam.read()
        
        # Check if frames are read successfully
        if not ret_video or not ret_webcam:
            print("Error reading frames")
            break
        
        # Convert video frame to HSV
        hsv_video = cv2.cvtColor(frame_video, cv2.COLOR_BGR2HSV)
        # Create mask for green screen
        mask = cv2.inRange(hsv_video, lower_green, upper_green)
        # Invert mask
        inv_mask = cv2.bitwise_not(mask)
        # Apply mask to video frame to extract foreground
        foreground = cv2.bitwise_and(frame_video, frame_video, mask=inv_mask)
        # Resize mask to webcam frame size
        mask = cv2.resize(mask, (frame_webcam.shape[1], frame_webcam.shape[0]))
        # Apply mask to webcam frame to extract background
        background = cv2.bitwise_and(frame_webcam, frame_webcam, mask=mask)
        # Resize foreground and background to webcam frame size
        foreground = cv2.resize(foreground, (frame_webcam.shape[1], frame_webcam.shape[0]))
        background = cv2.resize(background, (frame_webcam.shape[1], frame_webcam.shape[0]))
        # Combine foreground and background
        final_frame = cv2.add(foreground, background)
        
        # Encode final frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', final_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Release video captures
    cap_video.release()
    cap_webcam.release()

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
