import json
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from db_access.db_services import get_all, add_row, get_one_by_condition, delete_one_by_condition, add_rows, \
    get_many_by_condition, join_tables, JoinStructure

TABLE_NAME = "devices"


class Device(BaseModel):
    mac_address: str
    network_id: int
    vendor: Optional[str]
    ip_address: Optional[str]
    last_update: Optional[datetime]
    id: Optional[int] = None


class ComDevices(BaseModel):
    src_device_id: int
    dst_device_id: int
    protocols: str = Field(...)

    def __init__(self, **data):
        if 'protocols' in data and isinstance(data['protocols'], list):
            # Convert protocols list to json string
            data['protocols'] = json.dumps(data['protocols'])
        super().__init__(**data)


def get_all_devices():
    return get_all(TABLE_NAME)


def add_device(device: Device):
    return add_row(TABLE_NAME, device)


def add_devices(dvcs_lst: List[Device]):
    return add_rows(TABLE_NAME, dvcs_lst)


def add_connections(connections_lst: List[ComDevices]):
    return add_rows("device_communication", connections_lst)


def get_device_by_condition(**kwargs):
    device = get_one_by_condition(TABLE_NAME, **kwargs)
    if type(device) is dict:
        return Device(**device)
    return device


def get_devices_by_condition(**kwargs):
    devices = get_many_by_condition(TABLE_NAME, **kwargs)
    if type(devices) is list:
        return [Device(**dict(device)) for device in devices]
    return devices


def get_devices_by_network(network_id):
    devices = get_many_by_condition(TABLE_NAME, network_id=network_id)
    if type(devices) is list:
        return [Device(**dict(device)) for device in devices]
    return devices


def get_devices_by_client(client_id):
    from_table = ("devices", "d")
    select = (("d.*", None),)
    join = (("networks", "n"),)
    on = ((("n.client_id", client_id), ("d.network_id", "n.id")),)
    js = JoinStructure(from_table=from_table, select=select, join=join, on=on)
    devices = join_tables(js)
    if type(devices) is list:
        return [Device(**dict(device)) for device in devices]
    return devices


def delete_device_by_condition(**kwargs):
    device = delete_one_by_condition(TABLE_NAME, **kwargs)
    if type(device) is dict:
        return Device(**device)
    return device


def get_connected_devices(network_id):
    from_table = ("device_communication", "dc")
    select = (("d1.mac_address", "src_mac_address"),
              ("d2.mac_address", "dst_mac_address"),
              ("dc.protocols", "protocols"))
    join = ((TABLE_NAME, "d1"),
            (TABLE_NAME, "d2"))
    on = ((("dc.src_device_id", "d1.id"), ("d1.network_id", network_id)),
          (("dc.dst_device_id", "d2.id"), ("d2.network_id", network_id)))
    js = JoinStructure(from_table=from_table, select=select, join=join, on=on)
    return join_tables(js)
