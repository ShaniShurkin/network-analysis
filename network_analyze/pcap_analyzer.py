from datetime import datetime, timezone
from typing import List

from mac_vendor_lookup import MacLookup
from scapy.all import *

from entity_services.device import Device


def read_pcap_file(file):
    return rdpcap(file)


def extract_packet_addrs(pac):
    src_ip_addr = dst_ip_addr = None
    # todo: check - Can there be such a situation in the network where the same device has different IP addresses?
    # if IP in pac:
    #   src_ip_addr = pac[IP].src
    #  dst_ip_addr = pac[IP].dst
    # return set of 2 tuples (src & dst) that each tuple includes:
    # mac address, ip address (if exists), date of capturing

    return {(pac.src, src_ip_addr), (pac.dst, dst_ip_addr)}


def find_vendor(mac_addr):
    try:
        # finds device's vendor by mac addr
        return MacLookup().lookup(mac_addr)
    # sometimes there is no vendor and KeyError is raised
    except KeyError:
        return None


def create_devices_list(pct_lst, network_id):
    dev_set = set()
    for pac in pct_lst:
        # print([layer for layer in pac.layers()])
        dev_set |= extract_packet_addrs(pac)

    dev_lst = list()
    timestamp = int(pct_lst[0].time)
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(hour=0, minute=0, second=0)
    for dvc in dev_set:
        new_device = Device(
            mac_address=dvc[0],
            ip_address=dvc[1],
            last_update=date,
            network_id=network_id,
            vendor=find_vendor(dvc[0]))
        dev_lst.append(new_device)
    return dev_lst


# todo: keep protocol, filter connections
def create_connections_list(packets_lst, devices_lst: List[Device]):
    connections = set()
    # finds ids of source device and destination device
    for pac in packets_lst:
        src_id = dst_id = None
        for dvc in devices_lst:
            if dvc.mac_address == pac.src:
                src_id = dvc.id
            elif dvc.mac_address == pac.dst:
                dst_id = dvc.id

        connections.add((src_id, dst_id))
    connections_lst = [{"src_device_id": conn[0], "dst_device_id": conn[1]} for conn in connections]
    return connections_lst
