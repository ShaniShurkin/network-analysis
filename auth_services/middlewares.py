from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from auth_services.authentication import get_user_from_token, oauth2_cookie_scheme
from db_access.db_services import get_one_by_condition
from entity_services.combinations import get_technician_with_network


def auth_middleware(request: Request, call_next):
    token = oauth2_cookie_scheme(request)
    user = get_user_from_token(token)
    request.state.user = user
    response = call_next(request)
    return response


# Check if exits client with this id (client_id) to the current technician
def client_auth_middleware(request: Request, call_next):
    client_id = request.path_params.get("client_id")
    contact = get_one_by_condition(
        table="clients_technicians",
        client_id=client_id,
        technician_id=request.state.user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Technician {request.state.user.name} does not have client with id {client_id}",
        )
    response = call_next(request)
    return response


def network_auth_middleware(request: Request, call_next):
    network_id = request.path_params.get("client_id")
    contact = get_technician_with_network(network_id=network_id, technician_id=request.state.user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Technician {request.state.user.name} does not have client with network {network_id}",
        )
    response = call_next(request)
    return response
