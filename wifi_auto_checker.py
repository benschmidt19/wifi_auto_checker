import ctypes
import subprocess
import sys
import time
import logging
import schedule as sc

# Constants
LOG_FILE = "wifi_status_log.txt"       # Log file name
PING_HOST = "www.google.com"           # Host to ping for connectivity check

# Try to create the log file if it doesn't already exist
try:
    with open(LOG_FILE, 'x') as file:
        file.write("Logs:\n")
    print(f"File '{LOG_FILE}' created successfully.")
except FileExistsError:
    print(f"File '{LOG_FILE}' already exists.")

# Configure logging to write messages to the log file with timestamps
logging.basicConfig(filename=LOG_FILE, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    filemode='a')  # Append mode

# Function to enable WiFi using netsh command
def enable():
    try:
        subprocess.call("netsh interface set interface Wi-Fi enabled", shell=True)
        print("Turning On the laptop WiFi")
        logging.info("WiFi enabled")
    except Exception as e:
        print(f"Failed to enable WiFi: {e}")
        logging.error(f"Failed to enable WiFi: {e}")

# Function to disable WiFi using netsh command
def disable():
    try:
        subprocess.call("netsh interface set interface Wi-Fi disabled", shell=True)
        print("Turning Off the laptop WiFi")
        logging.info("WiFi disabled")
    except Exception as e:
        print(f"Failed to disable WiFi: {e}")
        logging.error(f"Failed to disable WiFi: {e}")

# Main job function to check WiFi and try reconnection if it's down
def job():
    try:
        # Ensure WiFi is enabled before checking connectivity
        subprocess.call("netsh interface set interface Wi-Fi enabled", shell=True)
        print("WiFi is enabled and connected to internet")
        logging.info("WiFi is enabled and connected to the internet.")
        
        # Ping the host to check if the internet is reachable
        response = subprocess.call(f"ping -n 1 {PING_HOST}", shell=True)
        
        if response == 1:
            # If ping fails, start reconnection attempts
            print("Your Connection is not working")
            logging.warning("WiFi connection not working, ping failed.")

            attempt_counter = 0
            max_attempts = 3  # Limit the number of reconnection tries

            while attempt_counter < max_attempts:
                print(f"Attempt {attempt_counter + 1} to reconnect...")
                logging.info(f"Attempt {attempt_counter + 1} to reconnect...")
                
                disable()
                time.sleep(1)  # Wait before enabling again
                enable()
                time.sleep(5)  # Give the system time to reconnect

                # Check again if internet is reachable
                response = subprocess.call(f"ping -n 1 {PING_HOST}", shell=True)
                if response == 0:
                    print("Reconnection successful!")
                    logging.info("Reconnection successful!")
                    break
                else:
                    print(f"Reconnection attempt {attempt_counter + 1} failed.")
                    logging.warning(f"Reconnection attempt {attempt_counter + 1} failed.")
                
                attempt_counter += 1

            # Log failure if all attempts were unsuccessful
            if attempt_counter == max_attempts and response != 0:
                print(f"Failed to reconnect after {max_attempts} attempts.")
                logging.error(f"Failed to reconnect after {max_attempts} attempts.")
    except Exception as e:
        # Catch and log any unexpected errors during the process
        print(f"Error during WiFi check: {e}")
        logging.error(f"Error during WiFi check: {e}")

# Function to check if the script is running with administrator privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.error(f"Admin check failed: {e}")
        return False

# Main execution
if is_admin():
    # Schedule the job to run every 50 seconds
    sc.every(50).seconds.do(job)
else:
    # Relaunch the script with admin privileges if not already
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# Keep running the scheduler loop
while True:
    sc.run_pending()
    time.sleep(1)
