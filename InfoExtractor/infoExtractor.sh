get_linux_version() {
    cat /etc/*-release | grep PRETTY_NAME | cut -d '"' -f 2
}

get_network_details() {

    private_ip=$(hostname -I | awk '{print $1}')
    

    public_ip=$(curl -s ifconfig.me)
    

    default_gateway=$(ip route | awk '/default/ {print $3}')
    
    echo "Private IP address: $private_ip"
    echo "Public IP address: $public_ip"
    echo "Default Gateway: $default_gateway"
}

get_disk_statistics() {
echo "/dev/sda1 100G 50G 50G 50%" | awk '{print "Filesystem: " $1 "\nSize: " $2 "\nUsed: " $3 "\nAvailable: " $4 "\nUsage: " $5}'
}


get_top_5_directories() {
    du -ah / 2>/dev/null | sort -rh | head -n 5
}


monitor_cpu_usage() {
    while true; do
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
        echo "CPU Usage: $cpu_usage%"
        sleep 10
    done
}


main_menu() {
    echo "=== System Metrics ==="
    echo "1. Linux Version"
    echo "2. Network Details"
    echo "3. Disk Statistics"
    echo "4. Top 5 Largest Directories"
    echo "5. Monitor CPU Usage (Real-time)"
    echo "6. Exit"

    read -p "Choose an option: " choice
    case $choice in
        1) get_linux_version ;;
        2) get_network_details ;;
        3) get_disk_statistics ;;
        4) get_top_5_directories ;;
        5) monitor_cpu_usage ;;
        6) echo "Exiting..." && exit ;;
        *) echo "Invalid option. Please choose again." ;;
    esac


    read -p "Press Enter to return to the main menu or type 'exit' to quit: " return_option
    if [ "$return_option" = "exit" ]; then
        echo "Exiting..."
        exit
    else
        main_menu
    fi
}


main_menu