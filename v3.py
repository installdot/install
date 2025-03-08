import subprocess
import time
import requests
import os
import threading
import sys
import select

GAME_IDS = [
    "3101667897",  # Legends Of Speed
    "7041939546",  # Catalog Avatar Creator
    "18853192637",  # Pet Mine
    "17625359962",  # RIVALS
    "116495829188952",  # Dead Rails Alpha
    "18994560526",  # Realistic Anime Outfits
    "6872265039",  # CTF BedWars
    "132903971646556",  # Kivotos TD
    "16732694052"
]

BLOX_FRUIT_ID = "2753915549"
TELEGRAM_BOT_TOKEN = "7714379995:AAEknOKKMUv8dSYBLKtCppH5JVfFPuGfwJY"
TELEGRAM_CHAT_ID = "7193275860"
MESSAGE_ID = ""
STATUS = "Starting..."
CURRENT_ID = ""
NEXT_ID = ""

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

def display_ui(packages, ip, status, current_id, next_id, time_left=0):
    os.system("clear")
    rainbow_text("Creator: Trần Hải")
    print(f"IP: {ip}")
    print(f"Status: {status}")
    if status == "Seeding":
        print(f"Current ID: {current_id}")
        print(f"Next ID: {next_id}")
        print(f"Time left: {time_left} seconds")
        print("Options:")
        print("1. Skip 1 game")
        print("2. Skip all (Blox Fruit)")
    elif status == "Running":
        instance_count = 1
        for package in packages:
            output = run_shell_command(f"pm list packages | grep '{package}'")
            if package in output:
                print(f"Instance {instance_count}: Running")
            else:
                print(f"Instance {instance_count}: Stopped")
            instance_count += 1
        print("Options:")
        print("1. Rejoin Single (Choose 1 instance)")
        print("2. Rejoin All")

def run_games():
    global STATUS, CURRENT_ID, NEXT_ID
    packages = find_roblox_packages()
    if not packages:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    ip = get_ip()
    game_index = 0
    while game_index < len(GAME_IDS):
        CURRENT_ID = GAME_IDS[game_index -1] if game_index > 0 else ""
        NEXT_ID = GAME_IDS[game_index]
        time_left = 300
        STATUS = "Seeding"

        display_ui(packages, ip, STATUS, CURRENT_ID, NEXT_ID, time_left)

        threads = []
        for package in packages:
            thread = threading.Thread(target=open_roblox_url, args=(package, GAME_IDS[game_index]))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        while time_left > 0:
            display_ui(packages, ip, STATUS, CURRENT_ID, NEXT_ID, time_left)
            rlist, _, _ = select.select([sys.stdin], [], [], 1)
            if rlist:
                choice = sys.stdin.readline().strip()
                if choice == "1":
                    game_index += 1
                    break
                elif choice == "2":
                    return
            time.sleep(1)
            time_left -= 1
        game_index += 1

def run_blox_fruit():
    global STATUS
    packages = find_roblox_packages()
    if not packages:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    ip = get_ip()
    STATUS = "Running"

    while True:
        display_ui(packages, ip, STATUS, "", "")
        message = f"IP: {ip}\nStatus: Running\n"
        instance_count = 1
        for package in packages:
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

        rlist, _, _ = select.select([sys.stdin], [], [], 5)
        if rlist:
            choice = sys.stdin.readline().strip()
            if choice == "1":
                print("Enter Instance Number to Rejoin:")
                instance_num = int(sys.stdin.readline().strip()) -1
                if 0 <= instance_num < len(packages):
                    threading.Thread(target=open_roblox_url, args=(packages[instance_num], BLOX_FRUIT_ID)).start()
            elif choice == "2":
