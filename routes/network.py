import os
from collections import defaultdict
from functools import reduce
from typing import List
from scapy.plist import PacketList
from fastapi import APIRouter, File, UploadFile, Request, Form
from starlette.responses import HTMLResponse

from entity_services.combinations import get_technician_clients
from entity_services.device import add_devices, add_connections, Device, get_devices_by_network, get_connected_devices, \
    get_devices_by_condition
from exceptions_handling import handle_app_exceptions
from entity_services.network import add_network
from entity_services.combinations import get_networks_by_technician, get_networks_by_client
from network_analyze.pcap_analyzer import read_pcap_file, create_devices_list, create_connections_list
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/network")


# todo: get more details in form, create network after device list is ready
@router.post("/{{client_id}}")
@handle_app_exceptions
def analyze_network(client_id: int, file: UploadFile = File(...)):
    network_id: int = add_network(client_id)
    packets_lst: PacketList = read_pcap_file(file.file)
    dvcs_lst: List[Device] = create_devices_list(packets_lst, network_id)
    add_devices(dvcs_lst)
    dvcs_with_id_lst: List[Device] = get_devices_by_network(network_id)
    connections_list: [List[dict]] = create_connections_list(packets_lst, dvcs_with_id_lst)
    add_connections(connections_list)
    return {"network_id": network_id}


@router.get("/{{network_id}}")
@handle_app_exceptions
def get_connections_lst(network_id: int):
    conn_dvcs_lst: dict = get_connected_devices(network_id)
    print(conn_dvcs_lst)
    conn_dvcs_table = reduce(lambda dct, conn_dvcs:
                             (dct[conn_dvcs["src_mac_address"]].routerend(conn_dvcs["dst_mac_address"]), dct)[-1],
                             conn_dvcs_lst,
                             defaultdict(list))
    return conn_dvcs_table


@router.get("/{{network_id}}/devices/")
@handle_app_exceptions
def get_network_devices(request: Request, network_id: int):
    if (len(request.query_params)) > 0:
        return get_devices_by_condition(**request.query_params, network_id=network_id)
    return get_devices_by_network(network_id)


@router.get("/client/{{client_id}}")
@handle_app_exceptions
def get_client_networks(request: Request, client_id: int):
    networks = get_networks_by_client(technician_id=request.state.user.id, client_id=client_id)
    return networks


@router.get("/technician")
@handle_app_exceptions
def get_technician_network(request: Request):
    networks = get_networks_by_technician(technician_id=request.state.user.id)
    return networks


# root_dir = os.path.dirname(
#     os.path.abspath(__file__)
# )
abs = r"C:\Users\User\Desktop\מדעי המחשב\bootcamp\project\python_project\static"
router.mount("/static", StaticFiles(directory=abs), name="static")

templates = Jinja2Templates(directory="templates")


@router.get("/{network_id}/visualize", response_class=HTMLResponse)
def read_items(request: Request, network_id: int):
    return templates.TemplateResponse("network_visualisation.html", {request: request, "network_id": network_id})
    # return f"""
    # <html>
    #     <head>
    #         <title>{network_id}</title>
    #     </head>
    #     <body>
    #         <h1>Look ma! HTML!</h1>
    #     </body>
    # </html>
    # """
