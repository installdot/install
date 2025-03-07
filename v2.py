import os
import time
import random
import subprocess

# List of 9 game IDs
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
CYCLE_TIME = 300  # 5 minutes per game
CHECK_INTERVAL = 10  # Check instances every 10 seconds
BLOX_FRUITS_REJOIN_TIME = 1200  # 20 minutes

def clear_screen():
    """Clear the terminal screen."""
    os.system("clear")

def get_roblox_instances():
    """Fetch installed Roblox instances with package names like com.roblox.clien{random}."""
    instances = []
    output = subprocess.getoutput("pm list packages | grep 'com.roblox.clien'")
    
    for line in output.splitlines():
        package = line.replace("package:", "").strip()
        if package.startswith("com.roblox.clien"):
            instances.append(package)
    
    return instances

def open_roblox_instances(instances):
    """Open all detected Roblox instances."""
    for package in instances:
        os.system(f"am start -n {package}/.MainActivity")
        time.sleep(2)  # Give time for each instance to launch

def launch_game(package, game_id):
    """Make an instance join a specific game."""
    os.system(f"am start -n {package}/.MainActivity -a android.intent.action.VIEW -d 'rblx://place?id={game_id}'")

def rotate_games():
    """Ensure each instance plays all 9 games before joining Blox Fruits."""
    instances = get_roblox_instances()

    if not instances:
        print("❌ No Roblox instances found.")
        return

    print(f"✅ Detected {len(instances)} Roblox instances.")
    
    # Open all instances
    open_roblox_instances(instances)

    played_games = {instance: [] for instance in instances}

    for cycle in range(1, 10):  # Each instance plays all 9 games
        clear_screen()
        print(f"Seeding... Cycle {cycle}/9\n")

        for idx, instance in enumerate(instances, start=1):
            available_games = list(set(GAME_IDS) - set(played_games[instance]))

            if not available_games:
                played_games[instance] = []
                available_games = GAME_IDS.copy()

            game_id = random.choice(available_games)
            played_games[instance].append(game_id)

            print(f"🎮 Instance {idx} -> {game_id}")
            launch_game(instance, game_id)

        for remaining_time in range(CYCLE_TIME, 0, -CHECK_INTERVAL):
            clear_screen()
            print(f"Seeding... Cycle {cycle}/9")
            print(f"⏳ Time to next cycle: {remaining_time}s\n")
            time.sleep(CHECK_INTERVAL)

    # Join Blox Fruits after all cycles
    clear_screen()
    print("🎉 Finished seeding!!!\nJoining Blox Fruits...\n")
    for instance in instances:
        launch_game(instance, FINAL_GAME_ID)

    last_rejoin_time = time.time()

    while True:
        clear_screen()
        print("\n🔄 Auto-rejoining Blox Fruits...\n")
        for instance in instances:
            launch_game(instance, FINAL_GAME_ID)

        last_rejoin_time = time.time()

        print(f"\nNext rejoin in {BLOX_FRUITS_REJOIN_TIME // 60} minutes...\n")
        time.sleep(BLOX_FRUITS_REJOIN_TIME)

# Start the rotation process
rotate_games()
