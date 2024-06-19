import os
import sys
import subprocess

def check_file_permissions(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False
    
    # Check read permissions
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permission for file '{file_path}'.")
        return False

    # Check write permissions
    if not os.access(file_path, os.W_OK):
        print(f"Error: No write permission for file '{file_path}'.")
        return False

    print(f"File permissions for '{file_path}' are OK.")
    return True

def check_audio_device_permissions():
    # Use subprocess to check audio device permissions
    try:
        subprocess.run(["osascript", "-e", "set volume 1"])
        print("Audio device permissions check passed.")
        return True
    except Exception as e:
        print(f"Error checking audio device permissions: {e}")
        return False

def main():
    # File path to check permissions
    file_path = "/Users/sanyadoda/ONR-HAI/Server/TTS_first_test.py"  
    
    # Check file permissions
    if not check_file_permissions(file_path):
        sys.exit(1)

    # Check audio device permissions
    if not check_audio_device_permissions():
        sys.exit(1)

    print("All system permissions checks passed.")

if __name__ == "__main__":
    main()
