from mac_vendor_lookup import MacLookup
from scapy.all import *
from scapy.layers.inet import IP
from scapy.layers.l2 import ARP
from entity_services.device import Device, ComDevices


def read_pcap_file(file):
    return rdpcap(file)


def extract_packet_addrs(pac):
    src_ip = dst_ip = None
    if ARP in pac:
        src_ip = pac[ARP].psrc
        dst_ip = pac[ARP].psrc
        # if the packet is request ARP packet - There is no destination mac address so only source device is returned
        if pac.op == 1:
            return {(pac.src, src_ip)}
    if IP in pac:
        src_ip = pac[IP].src
        dst_ip = pac[IP].dst
        # ff:ff:ff:ff:ff:ff means broadcast address - not considered as a device
        if pac.dst == "ff:ff:ff:ff:ff:ff":
            return {(pac.src, src_ip)}

    return {(pac.src, src_ip), (pac.dst, dst_ip)}


def find_vendor(mac_addr):
    try:
        # finds device's vendor by mac addr
        return MacLookup().lookup(mac_addr)
    # sometimes there is no vendor and KeyError is raised
    except KeyError:
        return None


def remove_duplicates(tuples: set):
    # remove duplicates - when the first value of tuple repeats itself and put None instead of the second value
    seen_values = set()
    duplicates = set()
    tuples2 = tuples.copy()
    for tpl in tuples:
        if tpl[0] in seen_values:
            duplicates.add(tpl[0])
        else:
            seen_values.add(tpl[0])
    for tpl in tuples:
        if tpl[0] in duplicates:
            new_tpl = (tpl[0], None)
            tuples2.add(new_tpl)
            tuples2.remove(tpl)
    return tuples2


def create_devices_list(pct_lst, network_id):
    dev_set = set()
    for pac in pct_lst:
        dev_set |= extract_packet_addrs(pac)
    # For cases where the MAC address is the same but the IP address is different
    no_duplicates_dev_set = remove_duplicates(dev_set)
    dev_lst = list()
    timestamp = int(pct_lst[0].time)
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).date()
    for dvc in no_duplicates_dev_set:
        new_device = Device(
            mac_address=dvc[0],
            ip_address=dvc[1],
            last_update=date,
            network_id=network_id,
            vendor=find_vendor(dvc[0]))
        dev_lst.append(new_device)
    return dev_lst


def create_connections_list(packets_lst, devices_lst: List[Device]):
    connections = set()
    # finds ids of source device and destination device
    for pac in packets_lst:
        protocols = [layer.__name__ for layer in pac.layers()]
        src_mac = dst_mac = None
        # Check if it's an ARP packet
        if 'ARP' in protocols and pac.op == 2:
            src_mac = pac[ARP].hwsrc
            dst_mac = pac[ARP].hwdst
        # Check if it's a packet between components
        if 'IP' in protocols:
            src_mac = pac.src
            dst_mac = pac.dst
        src_id = dst_id = None
        for dvc in devices_lst:
            if dvc.mac_address == src_mac:
                src_id = dvc.id
            elif dvc.mac_address == dst_mac:
                dst_id = dvc.id
        if src_id and dst_id:
            new_conn = (str(protocols), src_id, dst_id)
            connections.add(new_conn)
    connections_lst = [ComDevices(protocols=pro, src_device_id=src, dst_device_id=dst) for pro, src, dst in connections]
    return connections_lst
