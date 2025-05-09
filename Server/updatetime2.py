import datetime
import requests
import json
import time
import os
import ctypes
import ctypes.util

def _linux_set_time(time_tuple):
    CLOCK_REALTIME = 0
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]
    librt = ctypes.CDLL(ctypes.util.find_library("rt"))
    ts = timespec()
    ts.tv_sec = int(datetime.datetime(*time_tuple[:6]).timestamp())
    ts.tv_nsec = time_tuple[6] * 1000000  # Milliseconds to nanoseconds
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

def fetch_datetime_from_server(url):
    try:
        print("Connecting to server...")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("Connected.")
            return json.loads(response.content)
        else:
            print("Failed to get valid response from server.")
    except requests.RequestException as e:
        print(f"Connection failed: {e}")
    return None

def update_system_time(data):
    if not data:
        print("No valid data received. System time update aborted.")
        return
    
    year, month, day = data['Year'], f"{data['Month']:02d}", f"{data['Day']:02d}"
    hour, minute, second = data['Hour'], data['Minute'], data['Second']
    time_str = f"{hour}:{minute}:{second}"
    cmd = f'sudo -S date +%Y%m%d%T -s "{year}{month}{day} {time_str}"'
    os.popen(cmd, 'w').write('vpd\n\n')
    # print(f"System time updated to: {year}-{month}-{day} {time_str}")

if __name__ == "__main__":
    SERVER_URL = "http://10.151.27.1:8082/Datetimeapi/api/datetime"
    datetime_data = fetch_datetime_from_server(SERVER_URL)
    update_system_time(datetime_data)
