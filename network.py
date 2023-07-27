from db_services import add_row, get_many_by_condition

TABLE_NAME = "networks"


def add_network(client_id: int):
    return add_row(TABLE_NAME, {"client_id": client_id})


