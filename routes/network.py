from collections import defaultdict
from functools import reduce
from fastapi import APIRouter, File, UploadFile, Request
from starlette.responses import Response
from entity_services.device import get_devices_by_network, get_connected_devices, \
    get_devices_by_condition, get_devices_by_client
from exceptions_handling import handle_app_exceptions
from entity_services.combinations import get_networks_by_technician, get_networks_by_client
from network_analyze.network_creation import create_network, create_network_visualization
import matplotlib.pyplot as plt

router = APIRouter(prefix="/api/network")


# todo: get more details in form, create network after device list is ready
@router.post("/client/{client_id}")
@handle_app_exceptions
def analyze_network(client_id: int, file: UploadFile = File(...)):
    return create_network(client_id, file)


@router.get("/net/{network_id}")
@handle_app_exceptions
def get_connections_lst(network_id: int):
    conn_dvcs_lst = get_connected_devices(network_id)
    print(conn_dvcs_lst)
    # create a list with dict of connections. For each device,
    # which devices does it communicate with and with which protocols
    conn_dvcs_table = reduce(lambda dct, conn_dvcs:
                             (dct[conn_dvcs["src_mac_address"]].append(
                                 [conn_dvcs["dst_mac_address"], eval(conn_dvcs["protocols"])]), dct)[-1],
                             conn_dvcs_lst,
                             defaultdict(list))
    return conn_dvcs_table


@router.get("/net/{network_id}/show")
@handle_app_exceptions
def get_network_visualization(network_id: int):
    com_dvcs_lst = get_connected_devices(network_id)
    buffer = create_network_visualization(com_dvcs_lst)
    plt.savefig(buffer, format='png')
    plt.clf()
    return Response(content=buffer.getvalue(), media_type="image/png")


@router.get("/net/{network_id}/devices/")
@handle_app_exceptions
def get_network_devices(request: Request, network_id: int):
    if (len(request.query_params)) > 0:
        return get_devices_by_condition(**request.query_params, network_id=network_id)
    return get_devices_by_network(network_id)


@router.get("/client/{client_id}/devices")
@handle_app_exceptions
def get_client_devices(client_id: int):
    return get_devices_by_client(client_id)


@router.get("/client/{client_id}")
@handle_app_exceptions
def get_client_networks(request: Request, client_id: int):
    networks = get_networks_by_client(technician_id=request.state.user.id, client_id=client_id)
    return networks


@router.get("/technician")
@handle_app_exceptions
def get_technician_networks(request: Request):
    networks = get_networks_by_technician(technician_id=request.state.user.id)
    return networks
