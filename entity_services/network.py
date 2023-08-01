from db_access.db_services import add_row, join_tables, JoinStructure, get_all

TABLE_NAME = "networks"


def add_network(client_id: int):
    return add_row(TABLE_NAME, {"client_id": client_id})


def get_all_networks():
    return get_all(TABLE_NAME)
