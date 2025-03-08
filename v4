import subprocess
import time
import requests
import os
import threading
import sys

GAME_IDS = [
    "3101667897",  # Legends Of Speed
    "7041939546",  # Catalog Avatar Creator
    "18853192637", # Pet Mine
    "17625359962", # RIVALS
    "116495829188952", # Dead Rails Alpha
    "18994560526", # Realistic Anime Outfits
    "6872265039", # CTF BedWars
    "132903971646556", # Kivotos TD
    "16732694052"
]

BLOX_FRUIT_ID = "2753915549"
TELEGRAM_BOT_TOKEN = "7714379995:AAEknOKKMUv8dSYBLKtCppH5JVfFPuGfwJY"
TELEGRAM_CHAT_ID = "7193275860"
MESSAGE_ID = ""

current_id = None
next_id = None
time_left = 300

def install_requirements():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

install_requirements()

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def find_roblox_packages():
    output = run_shell_command("pm list packages | grep 'com.roblox.clien.' | cut -f 2 -d ':'")
    if output:
        return output.splitlines()
    return []

def open_roblox_url(package_name, place_id):
    run_shell_command(f"am start -a android.intent.action.VIEW -d 'roblox://placeId={place_id}' '{package_name}'")
    time.sleep(15)

def get_ip():
    try:
        response = requests.get("https://ifconfig.me")
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return f"Error getting IP: {e}"

def send_telegram_message(message):
    global MESSAGE_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        MESSAGE_ID = response.json()["result"]["message_id"]
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")
    except KeyError:
        print("Error parsing Telegram response.")

def edit_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    data = {"chat_id": TELEGRAM_CHAT_ID, "message_id": MESSAGE_ID, "text": message}
    try:
        requests.post(url, data=data)
    except requests.exceptions.RequestException as e:
        print(f"Error editing Telegram message: {e}")

def rainbow_text(text):
    colors = ["31", "33", "32", "36", "34", "35"]
    color_index = 0
    for char in text:
        print(f"\033[{colors[color_index]}m{char}\033[0m", end="")
        color_index = (color_index + 1) % len(colors)
    print()

def display_ui(status, instance_count, timer=None):
    # Clear only the part of the output we want to update (timer)
    os.system('clear')
    rainbow_text("Creator: Trần Hải")
    ip = get_ip()
    print(f"IP: {ip}")
    print(f"Status: {status}")
    if timer:
        print(f"Time left: {timer} seconds")
    for i in range(1, instance_count + 1):
        print(f"Instance {i}: Running")

def run_games():
    global current_id, next_id, time_left

    packages = find_roblox_packages()
    if not packages:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    current_id = None
    next_id = ""
    time_left = 300

    for game_id in GAME_IDS:
        current_id = next_id
        next_id = game_id
        time_left = 300

        display_ui("Seeding", len(packages), time_left)

        threads = []
        for package in packages:
            thread = threading.Thread(target=open_roblox_url, args=(package, game_id))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            display_ui("Seeding", len(packages), time_left)

        choice = input("\n1. Skip 1 game\n2. Skip all (skip to Blox Fruit)\nChoose an option: ")
        if choice == "1":
            continue
        elif choice == "2":
            break

    os.system("clear")

def run_blox_fruit():
    packages = find_roblox_packages()
    if not packages:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    ip = get_ip()
    instances = packages

    while True:
        message = f"IP: {ip}\n"
        instance_count = 1
        for package in instances:
            output = run_shell_command(f"pm list packages | grep '{package}'")
            if package in output:
                message += f"Instance {instance_count}: Running\n"
            else:
                message += f"Instance {instance_count}: Stopped\n"
                threading.Thread(target=open_roblox_url, args=(package, BLOX_FRUIT_ID)).start()
            instance_count += 1

        if not MESSAGE_ID:
            send_telegram_message(message)
        else:
            edit_telegram_message(message)

        display_ui("Running", len(instances))
        instance_choice = input("\n1. Rejoin Single (choose instance to rejoin)\n2. Rejoin All\nChoose an option: ")
        if instance_choice == "1":
            instance_number = int(input("Choose instance number to rejoin: "))
            open_roblox_url(instances[instance_number - 1], BLOX_FRUIT_ID)
        elif instance_choice == "2":
            for instance in instances:
                open_roblox_url(instance, BLOX_FRUIT_ID)
        time.sleep(5)

run_games()
run_blox_fruit()
