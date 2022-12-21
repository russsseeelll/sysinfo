import platform
import subprocess
import uuid
import re
import os
import psutil
import sys
import pyodbc


# get the MAC address
def get_mac_address():
    mac_address = None
    try:
        mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    except ValueError:
        pass
    return mac_address


# format mac address
def format_mac_address(mac_address):
    formatted_mac_address = re.sub(r"(..)", r"\1:", mac_address)
    # remove the post address colon
    formatted_mac_address = formatted_mac_address[:-1]
    return formatted_mac_address


# get the hostname
def get_hostname():
    hostname = None
    try:
        hostname = platform.node()
    except ValueError:
        pass
    return hostname


# get the current logged-in username
def get_current_username():
    username = None
    username = os.getlogin()
    return username


# get the CPU information
def get_cpu_info():
    cpu_info = None
    try:
        # get the CPU model name
        if platform.system() == "Windows":
            cmd = ["wmic", "cpu", "get", "name"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"Name\s*\r+\n+(.*)", output)
            if match:
                cpu_name = match.group(1)
            else:
                cpu_name = "Unknown"
        elif platform.system() == "Darwin":
            # MacOS
            cmd = ["sysctl", "-n", "machdep.cpu.brand_string"]
            cpu_name = subprocess.check_output(cmd).decode().strip()
        elif platform.system() == "Linux":
            # Linux
            cmd = ["cat", "/proc/cpuinfo"]
            output = subprocess.check_output(cmd).decode()
            match = re.search(r"model name\s*: (.*)", output)
            if match:
                cpu_name = match.group(1)
            else:
                cpu_name = "Unknown"

        # get the number of CPU cores
        if platform.system() == "Windows":
            cmd = ["wmic", "cpu", "get", "NumberOfCores"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"NumberOfCores\s*\r+\n+(.*)", output)
            if match:
                num_cores = match.group(1)
            else:
                num_cores = "Unknown"
        else:
            # MacOS and Linux
            num_cores = str(os.cpu_count())

        # get the CPU frequency
        if platform.system() == "Windows":
            cmd = ["wmic", "cpu", "get", "MaxClockSpeed"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"MaxClockSpeed\s*\r+\n+(.*)", output)
            if match:
                frequency = match.group(1)
            else:
                frequency = "Unknown"
        elif platform.system() == "Darwin":
            # MacOS
            cmd = ["sysctl", "-n", "hw.cpufrequency"]
            frequency = subprocess.check_output(cmd).decode().strip()
            frequency = str(int(frequency) // 1000000) + " MHz"
        elif platform.system() == "Linux":
            # Linux
            cmd = ["cat", "/proc/cpuinfo"]
            output = subprocess.check_output(cmd).decode()
            match = re.search(r"cpu MHz\s*: (.*)", output)
            if match:
                frequency = match.group(1) + " MHz"
            else:
                frequency = "Unknown"

        cpu_info = f"{cpu_name} ({num_cores} cores, {frequency})"
    except Exception:
        pass
    return cpu_info


# get the GPU information
def get_gpu_info():
    gpu_info = None
    try:
        # Get the GPU model name depending on OS
        if sys.platform == "win32":  # Windows
            cmd = ["wmic", "path", "Win32_VideoController", "get", "Name"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"Name\s*\r+\n+(.*)", output)
            if match:
                gpu_name = match.group(1)
            else:
                gpu_name = "Unknown"
        elif sys.platform == "darwin":  # Mac
            cmd = ["system_profiler", "SPDisplaysDataType"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"Chipset Model:\s+(.*)", output)
            if match:
                gpu_name = match.group(1)
            else:
                gpu_name = "Unknown"
        else:  # Linux
            cmd = ["lspci"]
            output = subprocess.check_output(cmd).decode().strip()
            match = re.search(r"VGA.*: (.*)", output)
            if match:
                gpu_name = match.group(1)
            else:
                gpu_name = "Unknown"
        gpu_info = f"{gpu_name}"
    except Exception:
        pass
    return gpu_info


# get the RAM information
def get_ram_info():
    ram_info = None
    try:
        # get the total RAM size
        cmd = ["wmic", "memorychip", "get", "capacity"]
        output = subprocess.check_output(cmd).decode().strip()
        match = re.search(r"Capacity\s*\r+\n+(.*)", output)
        if match:
            total_ram = int(match.group(1)) / (1024 ** 3)
        else:
            total_ram = "Unknown"

        ram_info = f"{total_ram:.2f} GB"
    except Exception:
        pass
    return ram_info


# get the service tag of the system
def get_service_tag():
    service_tag = None
    try:
        cmd = ["wmic", "bios", "get", "serialnumber"]
        output = subprocess.check_output(cmd).decode().strip()
        match = re.search(r"SerialNumber\s*\r+\n+(.*)", output)
        if match:
            service_tag = match.group(1)
        else:
            service_tag = "Unknown"
    except Exception:
        pass
    return service_tag


# get the HDD information
def get_hdd_info():
    hdd_info = []
    try:
        # Get the list of partitions
        partitions = psutil.disk_partitions()

        # Iterate through the partitions
        for partition in partitions:
            # Get the total and used storage space for the partition
            usage = psutil.disk_usage(partition.mountpoint)

            # Format the storage space information
            total_space = usage.total / (1024 ** 3)
            used_space = usage.used / (1024 ** 3)
            free_space = usage.free / (1024 ** 3)
            hdd = f"{partition.device}: {used_space:.2f} GB / {total_space:.2f} GB ({free_space:.2f} GB free)"

            # Add the HDD information to the list
            hdd_info.append(hdd)

    except Exception:
        pass

    # remove square brackets from hdd_info
    hdd_str = "\n".join(hdd_info)
    return hdd_str


# Sets
mac_address = get_mac_address()
formatted_mac_address = format_mac_address(mac_address)
hostname = get_hostname()
username = get_current_username()
service_tag = get_service_tag()
cpu_info = get_cpu_info()
gpu_info = get_gpu_info()
ram_info = get_ram_info()
hdd_info = get_hdd_info()

# Connect to the database
conn = pyodbc.connect(
    "DRIVER={MySQL ODBC 8.0 ANSI Driver};"
    "SERVER=localhost;"
    "DATABASE=sysinfo;"
    "UID=root;"
    "PWD="
)

cursor = conn.cursor()

# Check if the MAC address already exists in the table
query = "SELECT * FROM sysinfo WHERE mac_address = ?"
cursor.execute(query, (mac_address,))
row = cursor.fetchone()

if row:
    # MAC address exists, update the record
    query = "UPDATE sysinfo SET hostname = ?, username = ?, " \
            "cpu_info = ?, gpu_info = ?, ram_info = ?, hdd_info = ? WHERE mac_address = ?"
    cursor.execute(query, (hostname, username, cpu_info, gpu_info, ram_info, hdd_info, mac_address))
    conn.commit()
else:
    # MAC address does not exist, insert a new record
    query = "INSERT INTO sysinfo (mac_address, hostname, username, service_tag, " \
            "cpu_info, gpu_info, ram_info, hdd_info) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(query, (mac_address, hostname, username, service_tag, cpu_info, gpu_info, ram_info, hdd_info))
conn.commit()


# Close the cursor and connection
cursor.close()
conn.close()

