from entity_services.device import Device, ComDevices, get_devices_by_network, add_devices, add_connections
from network_analyze.pcap_analyzer import read_pcap_file, create_devices_list, create_connections_list
from entity_services.network import add_network
from typing import List
import io
from scapy.plist import PacketList
import networkx as nx


def create_network(client_id: int, file):
    network_id: int = add_network(client_id)
    packets_lst: PacketList = read_pcap_file(file.file)
    dvcs_lst: List[Device] = create_devices_list(packets_lst, network_id)
    print(dvcs_lst)
    add_devices(dvcs_lst)
    dvcs_with_id_lst: List[Device] = get_devices_by_network(network_id)
    print(dvcs_with_id_lst)
    connections_list: [List[ComDevices]] = create_connections_list(packets_lst, dvcs_with_id_lst)
    add_connections(connections_list)
    return {"network_id": network_id}


def create_network_visualization(com_dvcs_lst: list):
    com_dvcs_lst = [(com["src_mac_address"], com["dst_mac_address"], {"protocols": com["protocols"]})
                    for com in com_dvcs_lst]
    g = nx.DiGraph()
    g.add_edges_from(com_dvcs_lst)
    pos = nx.planar_layout(g)
    nx.draw(g, pos, with_labels=True, node_color='white')
    edge_labels = nx.get_edge_attributes(g, "protocols")
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_color="red")
    buffer = io.BytesIO()
    buffer.seek(0)
    return buffer
