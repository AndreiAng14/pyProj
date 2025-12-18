import subprocess
import sys
import os

def install():
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\nSUCCESS: All dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Failed to install dependencies. Error code: {e.returncode}")
        print("Please try running 'pip install -r requirements.txt' manually.")
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {e}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    if not os.path.exists("requirements.txt"):
        print("ERROR: requirements.txt not found in the same directory.")
    else:
        install()
