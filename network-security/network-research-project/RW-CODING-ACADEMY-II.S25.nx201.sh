#!/bin/bash
# Student Name: MUGISHA Pascal
# Student Code: S25
# Unit Code: RW-CODING-ACADEMY-II
# Program code: nx201
#Lecture's name: NZEYIMANA Celestin


check_command() {
    command -v "$1" >/dev/null 2>&1
}

install_tools() {
    echo "Checking and installing required tools..."
    tools=("sshpass" "tor" "nipe" "nmap" "whois" "curl")
    for tool in "${tools[@]}"; do
        if ! check_command "$tool"; then
            echo "Installing $tool..."
            sudo apt-get install -y "$tool"
        else
            echo "$tool is already installed."
        fi
    done
}

check_anonymity() {
    read -p "Enter the IP address to check its anonymity: " ip_address
    echo "Checking network anonymity for IP: $ip_address..."
    current_ip=$(curl -s https://ipinfo.io/ip)
    
    if [ "$current_ip" != "$ip_address" ]; then
        echo "The network is anonymous. Current IP: $current_ip (Spoofed country: $(curl -s https://ipinfo.io/country))"
    else
        echo "The network is not anonymous. Your real IP is being used."
        exit 1
    fi
}

execute_remote_commands() {
    local remote_ip=$1
    local address=$2
    local ssh_user=$3
    local ssh_pass=$4

    echo "Connecting to remote server at $remote_ip..."
    sshpass -p "$ssh_pass" ssh -o StrictHostKeyChecking=no "$ssh_user@$remote_ip" <<EOF
        echo "Remote Server Details:"
        echo "Country: $(curl -s https://ipinfo.io/country)"
        echo "IP: $(hostname -I)"
        echo "Uptime: $(uptime)"

        echo "Performing Whois lookup for $address..."
        whois "$address" > whois_$address.txt
        echo "Whois results saved to whois_$address.txt"

        echo "Scanning for open ports on $address..."
        nmap -Pn "$address" > nmap_$address.txt
        echo "Nmap results saved to nmap_$address.txt"
EOF
}

save_results() {
    local remote_ip=$1
    local ssh_user=$2
    local ssh_pass=$3
    local address=$4

    echo "Saving results from remote server to local computer..."
    sshpass -p "$ssh_pass" scp "$ssh_user@$remote_ip:whois_$address.txt" "./whois_$address.txt"
    sshpass -p "$ssh_pass" scp "$ssh_user@$remote_ip:nmap_$address.txt" "./nmap_$address.txt"

    echo "Creating audit log..."
    echo "$(date): Retrieved Whois and Nmap data for $address from $remote_ip" >> audit_log.txt
}

main() {
    install_tools

    check_anonymity

    read -p "Enter the address to scan: " address
    read -p "Enter remote server IP: " remote_ip
    read -p "Enter SSH username: " ssh_user
    read -sp "Enter SSH password: " ssh_pass
    echo

    execute_remote_commands "$remote_ip" "$address" "$ssh_user" "$ssh_pass"

    save_results "$remote_ip" "$ssh_user" "$ssh_pass" "$address"

    echo "All tasks completed. Results saved locally."
}

main
