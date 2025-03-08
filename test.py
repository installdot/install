import subprocess
import time
import requests
import os
import threading
import sys
import signal

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
STATUS = "Idle"
INSTANCES = []
CURRENT_GAME_INDEX = 0

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

def display_ui(current_id="", next_id="", time_left=0):
    os.system("clear")
    rainbow_text("Creator: Trần Hải")
    ip = get_ip()
    print(f"IP: {ip}")
    print(f"Status: {STATUS}")
    if STATUS == "Seeding":
        print(f"Current ID: {current_id}")
        print(f"Next ID: {next_id}")
        print(f"Time left: {time_left} seconds")
        print("Options:")
        print("1. Skip 1 game")
        print("2. Skip all")
    for i, package in enumerate(INSTANCES):
        output = run_shell_command(f"pm list packages | grep '{package}'")
        status = "Running" if package in output else "Stopped"
        print(f"Instance {i + 1}: {status}")

def run_games():
    global STATUS, CURRENT_GAME_INDEX, INSTANCES
    INSTANCES = find_roblox_packages()
    if not INSTANCES:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    current_id = ""
    next_id = ""
    time_left = 300
    CURRENT_GAME_INDEX = 0

    while CURRENT_GAME_INDEX < len(GAME_IDS):
        game_id = GAME_IDS[CURRENT_GAME_INDEX]
        if CURRENT_GAME_INDEX > 0:
            current_id = GAME_IDS[CURRENT_GAME_INDEX -1]
        else:
            current_id = "None"
        if CURRENT_GAME_INDEX < len(GAME_IDS)-1:
            next_id = GAME_IDS[CURRENT_GAME_INDEX +1]
        else:
            next_id = "None"
        time_left = 300
        STATUS = "Seeding"

        display_ui(current_id, next_id, time_left)

        threads = []
        for package in INSTANCES:
            thread = threading.Thread(target=open_roblox_url, args=(package, game_id))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            display_ui(current_id, next_id, time_left)
            if input_available():
                choice = sys.stdin.readline().strip()
                if choice == "1":
                    CURRENT_GAME_INDEX += 1
                    break
                elif choice == "2":
                    CURRENT_GAME_INDEX = len(GAME_IDS)
                    break

        CURRENT_GAME_INDEX += 1
    STATUS = "Idle"
    display_ui()

def input_available():
    import select
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def run_blox_fruit():
    global STATUS, INSTANCES
    INSTANCES = find_roblox_packages()
    if not INSTANCES:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No Roblox packages found.")
        return

    STATUS = "Running"

    while True:
        message = f"IP: {get_ip()}\nStatus: {STATUS}\n"
        for i, package in enumerate(INSTANCES):
            output = run_shell_command(f"pm list packages | grep '{package}'")
            status = "Running" if package in output else "Stopped"
            message += f"Instance {i + 1}: {status}\n"
            if status == "Stopped":
                threading.Thread(target=open_roblox_url, args=(package, BLOX_FRUIT_ID)).start()

        if not MESSAGE_ID:
            send_telegram_message(message)
        else:
            edit_telegram_message(message)
        display_ui()
        time.sleep(5)

def signal_handler(sig, frame):
    global STATUS
    print("\nExiting...")
    STATUS = "Exiting"
    display_ui()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

run_games()
run_blox_fruit()
