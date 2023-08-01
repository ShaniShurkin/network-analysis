from db_access.db_services import JoinStructure, join_tables, get_many_by_condition, add_row


# todo: join with clients table to get clients details
def get_technician_clients(technician_id):
    clients = get_many_by_condition("clients_technicians", technician_id=technician_id)
    clients = [client["client_id"] for client in clients]
    return clients


# todo: merge this functions
def get_networks_by_technician(technician_id):
    from_table = ("clients_technicians", "ct")
    select = (("n.id", "network_id"),
              ("ct.client_id", "client_id"))
    join = (("networks", "n"),)
    on = ((("n.client_id", "ct.client_id"), ("ct.technician_id", technician_id)),)
    js = JoinStructure(from_table=from_table, select=select, join=join, on=on)
    return join_tables(js)


def get_networks_by_client(technician_id, client_id):
    from_table = ("clients_technicians", "ct")
    select = (("n.id", "network_id"),)
    join = (("networks", "n"),)
    on = ((("n.client_id", client_id), ("ct.technician_id", technician_id), ("ct.client_id", client_id),
           ("ct.client_id", client_id)),)
    js = JoinStructure(from_table=from_table, select=select, join=join, on=on)
    return join_tables(js)


def add_client_to_technician(client_id: int, technician_id: int):
    return add_row("clients_technicians", {"client_id": client_id, "technician_id": technician_id})


# todo: change name
def get_technician_with_network(network_id, technician_id):
    from_table = ("clients_technicians", "ct")
    select = (("n.id", "network_id"),
              ("ct.technician_id", "technician_id"))
    join = (("networks", "n"),)
    on = ((("n.id", network_id), ("n.client_id", "ct.client_id"), ("ct.technician_id", technician_id)),)
    js = JoinStructure(from_table=from_table, select=select, join=join, on=on)
    return join_tables(js)
