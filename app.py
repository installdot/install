import os
import time
import random
import subprocess

# Ensure necessary packages are installed
def install_requirements():
    os.system("pkg update -y")
    os.system("pkg install proot -y")  # Ensures proper process handling
    os.system("pkg install grep -y")   # Required for process filtering

install_requirements()  # Run the installation

# List of 9 game IDs (to be played before Blox Fruits)
GAME_IDS = [
    "3101667897",  # Legends Of Speed
    "7041939546",  # Catalog Avatar Creator
    "18853192637", # Pet Mine
    "17625359962", # RIVALS
    "116495829188952", # Dead Rails Alpha
    "18994560526", # Realistic Anime Outfits
    "6872265039", # CTF BedWars
    "132903971646556", # Kivotos TD
    "16732694052"  # Fisch 2X XP
]

FINAL_GAME_ID = "2753915549"  # Blox Fruits
CYCLE_TIME = 60  # 5 minutes per game
CHECK_INTERVAL = 10  # Check instances every 10 seconds
BLOX_FRUITS_REJOIN_TIME = 1200  # 20 minutes

def clear_screen():
    """Clear the terminal screen."""
    os.system("clear")

def get_running_roblox_packages():
    """Fetch all running Roblox instances with package names like com.roblox.clien?"""
    try:
        output = subprocess.getoutput("ps -A | grep com.roblox.clien")
        packages = set()

        for line in output.splitlines():
            parts = line.split()
            for part in parts:
                if part.startswith("com.roblox.clien"):  # More reliable detection
                    packages.add(part)

        return list(packages)
    except Exception:
        return []

def launch_game(package, game_id):
    """Launch a game in a specific instance."""
    os.system(f"am start -n {package}/com.roblox.client -a android.intent.action.VIEW -d 'rblx://place?id={game_id}'")

def restart_instance(package):
    """Restart a closed/crashed instance."""
    print(f"Restarting {package}...")
    os.system(f"am force-stop {package}")
    time.sleep(2)
    os.system(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")  # Simulates app launch

def rotate_games():
    """Ensure each instance plays all 9 games before joining Blox Fruits."""
    instances = get_running_roblox_packages()

    if not instances:
        print("No running Roblox instances found.")
        return

    # Print detected instances
    for idx, instance in enumerate(instances, start=1):
        print(f"Instance {idx}: {instance}")

    time.sleep(2)

    # Track played games per instance
    played_games = {instance: [] for instance in instances}

    for cycle in range(1, 10):  # Each instance must play all 9 games
        clear_screen()
        print(f"Seeding... Cycle {cycle}/9\n")

        for idx, instance in enumerate(instances, start=1):
            # Ensure each instance plays all 9 games before repeating
            available_games = list(set(GAME_IDS) - set(played_games[instance]))

            if not available_games:  # If all games were played, reset the list
                played_games[instance] = []
                available_games = GAME_IDS.copy()

            game_id = random.choice(available_games)
            played_games[instance].append(game_id)

            print(f"Instance {idx} -> {game_id}")
            launch_game(instance, game_id)

        for remaining_time in range(CYCLE_TIME, 0, -CHECK_INTERVAL):
            clear_screen()
            print(f"Seeding... Cycle {cycle}/9")
            print(f"Time to next cycle: {remaining_time}s\n")
            time.sleep(CHECK_INTERVAL)

    # Join Blox Fruits after all cycles
    clear_screen()
    print("Finished seeding!!!\nJoining Blox Fruits...\n")
    for instance in instances:
        launch_game(instance, FINAL_GAME_ID)

    last_rejoin_time = time.time()

    # Keep checking instance status and auto-rejoin Blox Fruits
    while True:
        clear_screen()
        print("\nChecking instance status...\n")
        running_instances = get_running_roblox_packages()

        for idx, instance in enumerate(instances, start=1):
            if instance in running_instances:
                print(f"Instance {idx}: Running")
            else:
                print(f"Instance {idx}: Stopped! Restarting...")
                restart_instance(instance)  # Restart the instance if it crashed
                time.sleep(5)  # Wait before relaunching
                launch_game(instance, FINAL_GAME_ID)

        # Auto rejoin Blox Fruits every 20 minutes
        if time.time() - last_rejoin_time >= BLOX_FRUITS_REJOIN_TIME:
            print("\nRejoining Blox Fruits...\n")
            for instance in instances:
                launch_game(instance, FINAL_GAME_ID)
            last_rejoin_time = time.time()

        print(f"\nNext check in {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)

# Start the rotation process
rotate_games()
