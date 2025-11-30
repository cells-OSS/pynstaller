from time import sleep
import shutil
import subprocess
import os
import sys
import ctypes
import tempfile

__version__ = "v1.5"


def get_latest_release_tag():
    try:
        url = "https://api.github.com/repos/cells-OSS/pynstaller/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print("Failed to check for updates:", e)
        return __version__.lstrip("v")


def is_update_available(current_version):
    latest = get_latest_release_tag()
    return version.parse(latest) > version.parse(current_version.lstrip("v"))


def download_latest_script():
    latest_version = get_latest_release_tag()
    filename = f"pynstaller-v{latest_version}.py"
    url = "https://raw.githubusercontent.com/cells-OSS/pynstaller/main/pynstaller.py"
    response = requests.get(url)
    lines = response.text.splitlines()
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
    print(
        f"Current version: {__version__}, Latest: v{get_latest_release_tag()}")
    print(
        f"Downloaded update as '{filename}'. You can now safely delete the old version.")

    input("Press Enter to exit...")
    exit()

def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False
    
if not _is_admin():
    print("Requesting admin privileges...")
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def install_chocolatey():
    installationScript = (
        'Set-ExecutionPolicy Bypass -Scope Process -Force; '
        '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; '
        'iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))'
    )

    if _is_admin():
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", installationScript],
            check=True
        )
        return

    fd, script_path = tempfile.mkstemp(suffix=".ps1", text=True)
    os.close(fd)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(installationScript)

    ps_cmd = (
        "Start-Process powershell -Verb RunAs -ArgumentList "
        "'-NoProfile','-ExecutionPolicy','Bypass','-File','{}' -Wait"
    ).format(script_path.replace("'", "''"))

    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_cmd], check=True)

    try:
        os.remove(script_path)
    except OSError:
        pass

def get_choco_cmd():
    return shutil.which("choco") or r"C:\ProgramData\chocolatey\bin\choco.exe"

def install_packages(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ["pyfiglet", "requests", "packaging"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing required package(s) {package}...")
        install_packages(package)

import pyfiglet
import requests
from packaging import version

os.system('cls' if os.name == 'nt' else 'clear')

config_dir = os.path.join(os.getenv("APPDATA"), "pynstaller")

os.makedirs(config_dir, exist_ok=True)

programming_profile_path = os.path.join(config_dir, "profile_programming.conf")

with open(programming_profile_path, "w", encoding="utf-8") as f:
    for name in ["librewolf", "vscode", "python3", "vscode-python"]:
        f.write(name + "\n")

welcomeMessage_config_path = os.path.join(config_dir, "welcome_message.conf")
figlet_config_path = os.path.join(config_dir, "figlet.conf")
auto_update_config_path = os.path.join(config_dir, "auto_update.conf")
profile_path = os.path.join(config_dir)

if os.path.exists(auto_update_config_path):
    if is_update_available(__version__):
        print("New version available!")
        download_latest_script()

if os.path.exists(welcomeMessage_config_path):
    with open(welcomeMessage_config_path, "r", encoding="utf-8") as f:
        welcomeMessage = f.read()
else:
    welcomeMessage = """
===================================================
                     pynstaller
===================================================
"""

if os.path.exists(figlet_config_path):
    with open(figlet_config_path, "rb") as figlet_configFile:
        figlet_config = figlet_configFile.read().decode()
        if figlet_config == "True":
            welcomeMessage = pyfiglet.figlet_format(welcomeMessage)

menu = """
1 = Install an app
2 = Create a profile
3 = Run a profile
4 = Settings

WARNING: The names of the apps are separated
like "app1;app2;app3" unless specified otherwise.

TIP: To come back to this menu at any time, just type "back".
"""

print(welcomeMessage, menu)

chooseOption = input("Which option would you like to choose(1/2/3/4)?: ")

if chooseOption == "1":

    whichApp = input("Type the name of the app(s) you want to install: ")

    if whichApp.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    print("Installing Chocolatey...")

    sleep(2)

    if os.path.exists(get_choco_cmd()):
        print("Chocolatey is already installed.")
    else:
        install_chocolatey()

    print(f"Installing {whichApp}...")

    sleep(2)

    choco = get_choco_cmd()
    subprocess.run([choco, "install", whichApp, "-y"], check=True)

if chooseOption == "2":

    profileName = input("Type the name of the profile you want to create: ")

    config_path = os.path.join(config_dir, profileName)

    if profileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)


    with open(f"{config_path}.conf", "w") as profileFile:
        appNames = input(
            "Type the names of the apps you want to add to the profile (separated by commas): ")
        for appName in appNames.split(","):
            profileFile.write(appName.strip() + "\n")

    print(f"Your profile '{profileName}.conf' has been created successfully at '%appdata%/pynstaller'.")

if chooseOption == "3":
    print("Please place the profile config file at '%appdata%/pynstaller'.")
    inputProfileName = input("Type the name of the profile you want to run: ")
    config_path = os.path.join(config_dir, inputProfileName)

    if inputProfileName.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if os.path.exists(f"{config_path}.conf"):
        print("Checking if Chocolatey is installed...")
        
        sleep(2)

        if os.path.exists(get_choco_cmd()):
            print("Chocolatey is already installed.")
        else:
            print("Chocolatey is not installed. Installing Chocolatey...")

            sleep(2)

            install_chocolatey()

        print(f"Installing apps from profile '{inputProfileName}.conf'...")

        sleep(2)

        with open(f"{config_path}.conf", "r") as profileFile:
            for line in profileFile:
                appName = line.strip()
                if appName:
                    print(f"Installing {appName}...")
                    subprocess.run(
                        ["choco", "install", appName, "-y"], check=True)

        print("All apps from the profile have been successfully installed.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print(f"Profile '{inputProfileName}.conf' does not exist.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

if chooseOption == "4":
    settings_menu = """
===================================================
                     Settings
    1 = Turn Auto Update On/Off
    2 = Change Welcome Message
    3 = Reset Welcome Message
    4 = Figlet Welcome Message
===================================================
    """

    print(settings_menu)

    settingOption = input("Which setting would you like to change(1/2/3/4)?: ")
    if settingOption.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    if settingOption == "1":
        autoUpdateMenu = """
===================================================
                     Auto Update
    1 = Enable Auto Updates
    2 = Disable Auto Updates
===================================================
    """

        print(autoUpdateMenu)

        autoUpdateOption = input("Which option would you like to choose(1/2)?: ")

        if autoUpdateOption.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        if autoUpdateOption == "1":
            config_path = os.path.join(config_dir, "auto_update.conf")
            print("Enabling Auto Updates...")
            with open(config_path, "wb") as autoUpdateFile:
                autoUpdateFile.write("True".encode())
            print("Auto Updates have been enabled successfully!")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        
        if autoUpdateOption == "2":
            config_path = os.path.join(config_dir, "auto_update.conf")
            print("Disabling Auto Updates...")
            if os.path.exists(config_path):
                os.remove(config_path)
                print("Auto-Updates have been disabled successfully!")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("Auto-Updates are already disabled.")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

    if settingOption == "2":
        welcome_messageMenu = """
============================================
        Change Welcome Message
============================================            
"""
        print(welcome_messageMenu)
        config_path = os.path.join(config_dir, "welcome_message.conf")

        new_welcome_message = input(
            "New welcome message(use \\n for new lines): ")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_welcome_message.replace("\\n", "\n"))
        print("Welcome message updated.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if settingOption == "3":
        config_path = os.path.join(config_dir, "welcome_message.conf")

        if os.path.exists(config_path):
            os.remove(config_path)
            print("Welcome message has been reset to default.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Welcome message is already the default.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    if settingOption == "4":
        figletWelcome = """
============================================
        Figlet Welcome Message
1 = Turn on Figlet Welcome Message
2 = Turn off Figlet Welcome Message
============================================
"""
        print(figletWelcome)
        figletOption = input("Which option would you like to choose(1/2)?: ")
        if figletOption.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)
        
        config_path = os.path.join(config_dir, "figlet.conf")

        if figletOption == "1":
            print("Enabling Figlet Welcome Message...")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("True")
            print("Figlet Welcome Message has been enabled successfully!")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    
        if figletOption == "2":
            print("Disabling Figlet Welcome Message...")
            if os.path.exists(config_path):
                os.remove(config_path)
                print("Figlet Welcome Message has been disabled successfully!")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("Figlet Welcome Message is already disabled.")
                input("Press Enter to continue...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

    else:
        print("Invalid choice.")
        input("Press Enter to continue...")


else:
    print("Invalid choice.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)