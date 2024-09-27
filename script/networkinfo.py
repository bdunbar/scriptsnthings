import psutil
import socket

def get_network_info():
    addrs = psutil.net_if_addrs()
    network_info = {}
    for iface, iface_addrs in addrs.items():
        for addr in iface_addrs:
            if addr.family == socket.AF_INET:  # AF_INET means IPv4
                network_info[iface] = addr.address
    return network_info

print(get_network_info())

