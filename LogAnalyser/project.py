import os
import platform
import psutil
import socket
import subprocess
import time

# Function to gather basic system information like OS, hostname, IP addresses, etc.
def get_system_info():
    system_info = {
        "os": platform.system(),  # Get the operating system name (e.g., Windows, Linux)
        "os_version": platform.version(),  # Get the version of the operating system
        "hostname": socket.gethostname(),  # Get the machine's hostname
        "public_ip": get_public_ip(),  # Get the machine's public IP address
        "private_ip": socket.gethostbyname(socket.gethostname()),  # Get the machine's private IP address
        "default_gateway": get_default_gateway()  # Get the default gateway (router) IP address
    }
    return system_info

# Function to get the public IP address of the machine using an external service
def get_public_ip():
    try:
        # Execute the command to get the public IP using the `curl` command and `ifconfig.me`
        result = subprocess.run(["curl", "ifconfig.me"], capture_output=True, text=True)
        return result.stdout.strip()  # Return the public IP address as a string
    except Exception as e:
        return f"Error: {e}"  # Return an error message if something goes wrong

# Function to get the default gateway (router) IP address
def get_default_gateway():
    try:
        gateways = psutil.net_if_addrs()  # Get network interface addresses
        for gateway in gateways.values():
            for snic in gateway:
                if snic.family == socket.AF_INET:  # Check if the address is an IPv4 address
                    return snic.address  # Return the gateway IP address
    except Exception as e:
        return f"Error: {e}"  # Return an error message if something goes wrong
    return "N/A"  # Return "N/A" if no gateway is found

# Function to get disk usage statistics
def get_disk_usage():
    disk_usage = psutil.disk_usage('/')  # Get disk usage information for the root directory
    gb_factor = 1024 * 1024 * 1024  # Convert bytes to gigabytes (GB)
    return {
        "total": disk_usage.total / gb_factor,  # Total disk space in GB
        "used": disk_usage.used / gb_factor,  # Used disk space in GB
        "free": disk_usage.free / gb_factor  # Free disk space in GB
    }

# Function to find and list the largest directories/files
def get_largest_directories(path='.', count=5):
    if platform.system() == "Windows":
        # Command to get the largest directories on Windows using PowerShell
        command = ["powershell", "-Command",
                   f"Get-ChildItem -Path {path} -Recurse | Sort-Object Length -Descending | Select-Object -First {count} | ForEach-Object {{$_.FullName}}"]
    else:
        # Command to get the size of directories on Linux/Unix systems
        command = ["du", "-ah", path]

    try:
        # Run the command to find the largest directories
        result = subprocess.run(command, capture_output=True, text=True, shell=(platform.system() == "Windows"))
        lines = result.stdout.strip().split('\n')
        if platform.system() == "Windows":
            return lines[:count]  # Return the largest directories on Windows
        else:
            sorted_lines = sorted(lines, key=lambda x: x.split()[0], reverse=True)
            return sorted_lines[:count]  # Return the largest directories on Linux/Unix
    except Exception as e:
        return [f"Error: {e}"]  # Return an error message if something goes wrong

# Function to display the system information on the console
def display_system_info():
    system_info = get_system_info()  # Get the system information
    print(f"Operating System: {system_info['os']}")  # Display the OS name
    print(f"OS Version: {system_info['os_version']}")  # Display the OS version
    print(f"Hostname: {system_info['hostname']}")  # Display the hostname
    print(f"Public IP: {system_info['public_ip']}")  # Display the public IP address
    print(f"Private IP: {system_info['private_ip']}")  # Display the private IP address
    print(f"Default Gateway: {system_info['default_gateway']}")  # Display the default gateway IP address

# Function to display disk usage information on the console
def display_disk_usage():
    disk_usage = get_disk_usage()  # Get the disk usage statistics
    print(f"Disk Total: {disk_usage['total']:.2f} GB")  # Display total disk space in GB
    print(f"Disk Used: {disk_usage['used']:.2f} GB")  # Display used disk space in GB
    print(f"Disk Free: {disk_usage['free']:.2f} GB")  # Display free disk space in GB

# Function to display the largest directories on the console
def display_largest_directories():
    print("Largest Directories:")
    directories = get_largest_directories()  # Get the list of largest directories
    for directory in directories:
        print(directory)  # Display each directory path

# Main function to run the program in a loop, updating every 10 seconds
def main():
    while True:
        print("\nSystem Information:")
        display_system_info()  # Display system information

        print("\nDisk Usage:")
        display_disk_usage()  # Display disk usage information

        print("\nLargest Directories:")
        display_largest_directories()  # Display the largest directories

        print("\nCPU Usage:")
        print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")  # Display CPU usage percentage

        time.sleep(10)  # Pause for 10 seconds before the next iteration

# Entry point of the script
if __name__ == "__main__":
    main()  # Run the main function
