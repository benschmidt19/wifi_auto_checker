import ctypes
import subprocess
import sys
import time
import logging
import schedule as scheduler

# Configuration
LOG_FILENAME = "network_monitor_log.txt"
TEST_DOMAIN = "www.google.com"

# Create log file if missing
try:
    with open(LOG_FILENAME, 'x') as log_file:
        log_file.write("Network Log Initialized\n")
    print(f"Created new log file: {LOG_FILENAME}")
except FileExistsError:
    print(f"Log file '{LOG_FILENAME}' already exists.")

# Set up logging
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a')

# Enable wireless network
def turn_on_wifi():
    try:
        subprocess.call("netsh interface set interface name='Wi-Fi' admin=enabled", shell=True)
        print("WiFi turned ON")
        logging.info("WiFi turned ON")
    except Exception as error:
        print(f"Could not enable WiFi: {error}")
        logging.error(f"WiFi enable failed: {error}")

# Disable wireless network
def turn_off_wifi():
    try:
        subprocess.call("netsh interface set interface name='Wi-Fi' admin=disabled", shell=True)
        print("WiFi turned OFF")
        logging.info("WiFi turned OFF")
    except Exception as error:
        print(f"Could not disable WiFi: {error}")
        logging.error(f"WiFi disable failed: {error}")

# Connectivity check and recovery routine
def monitor_network():
    try:
        subprocess.call("netsh interface set interface name='Wi-Fi' admin=enabled", shell=True)
        print("Checking internet access...")
        logging.info("Checking internet connectivity")

        ping_result = subprocess.call(f"ping -n 1 {TEST_DOMAIN}", shell=True)

        if ping_result != 0:
            print("Network unreachable")
            logging.warning("Ping failed. Internet not reachable.")

            retries = 0
            max_retries = 3

            while retries < max_retries:
                print(f"Retry attempt {retries + 1}")
                logging.info(f"Retrying connection: attempt {retries + 1}")

                turn_off_wifi()
                time.sleep(2)
                turn_on_wifi()
                time.sleep(5)

                retry_ping = subprocess.call(f"ping -n 1 {TEST_DOMAIN}", shell=True)
                if retry_ping == 0:
                    print("Reconnected successfully")
                    logging.info("Internet reconnection successful")
                    break
                else:
                    print("Retry failed")
                    logging.warning(f"Attempt {retries + 1} failed to restore connection")

                retries += 1

            if retries == max_retries:
                print("All reconnection attempts failed")
                logging.error("Failed to reconnect after multiple tries")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        logging.error(f"Monitor function error: {ex}")

# Check for administrative privileges
def has_admin_rights():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as admin_err:
        logging.error(f"Privilege check failed: {admin_err}")
        return False

# Launch main routine
if has_admin_rights():
    scheduler.every(50).seconds.do(monitor_network)
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# Keep running the scheduled checks
while True:
    scheduler.run_pending()
    time.sleep(1)
