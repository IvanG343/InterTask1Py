import os
import requests
import subprocess
import winreg
import platform
import time

# Constants
REGISTRY_FILE_URL = "https://drive.google.com/uc?export=download&id=1IGENwFzLm8bBEboISadYSNEdxbnjz1fH"
GAME_MANIFEST_FILE = 'appmanifest_1568590.acf'


def download_reg_file(url, destination):
    """Download a .reg file to the game directory."""
    try:
        response = requests.get(url, allow_redirects=True)
        confirmed_link = response.url + '&confirm=t'
        correct_response = requests.get(confirmed_link)

        with open(destination, 'wb') as f:
            f.write(correct_response.content)

        print(f"File has been downloaded: {destination}")
        return destination
    except requests.exceptions.RequestException as e:
        print(f"Error loading file: {e}")
        return None
    except IOError as e:
        print(f"I/O error: {e}")
        return None


def apply_reg_file(reg_file_path):
    """Apply the settings from the specified .reg file."""
    try:
        result = os.system(f'regedit.exe /s "{reg_file_path}"')
        if result == 0:
            print("Settings applied successfully.")
        else:
            print("Error: Administrator privileges are required to modify the registry.")
        return result == 0
    except Exception as e:
        print(f"Error applying registry file {reg_file_path}: {e}")
        return False


def launch_game(game_dir):
    """Launch the game."""
    try:
        subprocess.run([os.path.join(game_dir, "Goose Goose Duck.exe")], check=True)
        print("Game launched successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error launching game: {e}")


def get_steam_libraries_list(path):
    """Get the list of Steam library paths from the VDF file."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [
                line.split('"')[3]
                for line in file if line.strip().startswith('"path"')
            ]
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"Error reading file: {e}")
    return []


def get_steam_library_path(path):
    """Get the path to the Steam library where the game is installed."""
    libraries_paths = get_steam_libraries_list(path)

    for library_path in libraries_paths:
        filepath = os.path.join(library_path, "steamapps", GAME_MANIFEST_FILE)
        if os.path.exists(filepath):
            return library_path

    print("Goose Goose Duck isn't found in your Steam library.")
    return None


def get_steam_path():
    """Get the installation path of Steam from the Windows registry."""
    try:
        architecture = platform.architecture()[0]
        if architecture == '64bit':
            key_path = r"SOFTWARE\WOW6432Node\Valve\Steam"
        else:
            key_path = r"SOFTWARE\Valve\Steam"

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            return winreg.QueryValueEx(key, 'InstallPath')[0]

    except FileNotFoundError:
        print("Registry key not found.")
    except Exception as e:
        print(f"Error reading registry value: {e}")
    return None


def main():
    # Script running time
    start_time = time.time()

    # Get the Steam path
    steam_path = get_steam_path()
    if steam_path is None:
        print("Error: Steam path not found.")
        return

    # Get the steam library path where the game is installed
    steam_library = get_steam_library_path(os.path.join(steam_path, "steamapps", "libraryfolders.vdf"))
    if steam_library is None:
        return

    # Set game directory
    game_dir = os.path.normpath(os.path.join(steam_library, "steamapps", "common", "Goose Goose Duck"))

    # Download reg file to the game directory
    reg_file_local_path = os.path.join(game_dir, 'settings.reg')
    if not download_reg_file(REGISTRY_FILE_URL, reg_file_local_path):
        return

    # Apply settings.reg
    if not apply_reg_file(reg_file_local_path):
        return

    # Start the Game
    # launch_game(game_dir)

    #
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
