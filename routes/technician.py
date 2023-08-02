from fastapi import Request, APIRouter, Form
from entity_services.client import add_client
from entity_services.combinations import get_technician_clients
from exceptions_handling import handle_app_exceptions
from entity_services.technician import BaseTechnician, get_technician_by_condition, \
    get_all_technicians
from entity_services.combinations import add_client_to_technician

router = APIRouter(prefix="/api/technician")


@router.get("/token-sanity")
@handle_app_exceptions
def checking(request: Request):
    return request.state.user


@router.get("/")
@handle_app_exceptions
def get(request: Request):
    if len(request.query_params) > 0:
        qp = request.query_params
        # send key and value to function that finds a technician by this condition: key == value
        db_technician = get_technician_by_condition(**qp)
        return BaseTechnician(**dict(db_technician))
    technicians: list = get_all_technicians()
    db_technicians = [BaseTechnician(**dict(technician)) for technician in technicians]
    return db_technicians


# @router.delete("/")
# @handle_app_exceptions
# def delete_one(request: Request):
#     if len(request.query_params) == 0:
#         raise HTTPException(status_code=400, detail="One pair of query params is required.")
#     qp = request.query_params
#     # send key and value to function that deletes a technician by this condition: key == value
#     delete_technician_by_condition(**qp)
#     return f"user ({qp}) deleted successfully"


@router.post("/create-client/")
@handle_app_exceptions
def create_client(request: Request, name: str = Form(...)):
    # Creates new client and adds him to current technician
    client_id = add_client(name)
    add_client_to_current_technician(request, client_id)
    return {"client_id": client_id}


@router.put("/add-client/{id}")
@handle_app_exceptions
def add_client_to_current_technician(request: Request, id_: int):
    add_client_to_technician(client_id=id_, technician_id=request.state.user.id)
    return {"client_id": id_}


@router.get("/clients")
@handle_app_exceptions
def get_clients(request: Request):
    clients = get_technician_clients(technician_id=request.state.user.id)
    return clients
