from db_access.db_services import add_row, get_all

TABLE_NAME = "clients"


def add_client(name: str):
    return add_row(TABLE_NAME, {"name": name})


def get_all_clients():
    return get_all(TABLE_NAME)


