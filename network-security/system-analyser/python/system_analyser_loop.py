import os
import platform
import psutil
import socket
import subprocess
import time


def get_system_info():
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "hostname": socket.gethostname(),
        "public_ip": get_public_ip(),
        "private_ip": socket.gethostbyname(socket.gethostname()),
        "default_gateway": get_default_gateway()
    }
    return system_info


def get_public_ip():
    try:
        result = subprocess.run(["curl", "ifconfig.me"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_default_gateway():
    try:
        gateways = psutil.net_if_addrs()
        for gateway in gateways.values():
            for snic in gateway:
                if snic.family == socket.AF_INET:
                    return snic.address
    except Exception as e:
        return f"Error: {e}"
    return "N/A"


def get_disk_usage():
    disk_usage = psutil.disk_usage('/')
    gb_factor = 1024 * 1024 * 1024  # Convert bytes to GB
    return {
        "total": disk_usage.total / gb_factor,
        "used": disk_usage.used / gb_factor,
        "free": disk_usage.free / gb_factor
    }


def get_largest_directories(path='.', count=5):
    if platform.system() == "Windows":
        command = ["powershell", "-Command",
                   f"Get-ChildItem -Path {path} -Recurse | Sort-Object Length -Descending | Select-Object -First {count} | ForEach-Object {{$_.FullName}}"]
    else:
        command = ["du", "-ah", path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=(platform.system() == "Windows"))
        lines = result.stdout.strip().split('\n')
        if platform.system() == "Windows":
            return lines[:count]
        else:
            sorted_lines = sorted(lines, key=lambda x: x.split()[0], reverse=True)
            return sorted_lines[:count]
    except Exception as e:
        return [f"Error: {e}"]


def display_system_info():
    system_info = get_system_info()
    print(f"Operating System: {system_info['os']}")
    print(f"OS Version: {system_info['os_version']}")
    print(f"Hostname: {system_info['hostname']}")
    print(f"Public IP: {system_info['public_ip']}")
    print(f"Private IP: {system_info['private_ip']}")
    print(f"Default Gateway: {system_info['default_gateway']}")


def display_disk_usage():
    disk_usage = get_disk_usage()
    print(f"Disk Total: {disk_usage['total']:.2f} GB")
    print(f"Disk Used: {disk_usage['used']:.2f} GB")
    print(f"Disk Free: {disk_usage['free']:.2f} GB")


def display_largest_directories():
    print("Largest Directories:")
    directories = get_largest_directories()
    for directory in directories:
        print(directory)


def main():
    while True:
        print("\nSystem Information:")
        display_system_info()

        print("\nDisk Usage:")
        display_disk_usage()

        print("\nLargest Directories:")
        display_largest_directories()

        print("\nCPU Usage:")
        print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")

        time.sleep(10)


if __name__ == "__main__":
    main()
