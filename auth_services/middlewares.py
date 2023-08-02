from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from fastapi.responses import JSONResponse

from auth_services.authentication import get_user_from_token, oauth2_cookie_scheme
from db_access.db_services import get_one_by_condition
from entity_services.combinations import get_technician_with_network

import re

from exceptions_handling import handle_middleware_exceptions, EmptyRowError


def extract_id(prefix, url):
    # Extracts the ID from a URL.
    match = re.search(prefix + r"/(\d+)", url)
    if match:
        return int(match.group(1))
    else:
        return None


async def auth_middleware(request: Request, call_next):
    token = oauth2_cookie_scheme(request)
    user = get_user_from_token(token)
    request.state.user = user
    if "api/network/client" in request.url.path:
        return await client_auth_middleware(request, call_next)
    if "api/network/net" in request.url.path:
        return await network_auth_middleware(request, call_next)
    response = await call_next(request)
    return response


# Check if exits client with this id (client_id) to the current technician
async def client_auth_middleware(request: Request, call_next):
    client_id = extract_id(prefix="api/network/client", url=request.url.path)
    try:
        get_one_by_condition(
            "clients_technicians",
            client_id=client_id,
            technician_id=request.state.user.id)
    except EmptyRowError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Technician {request.state.user.name} does not have client with id {client_id}",
        )
    response = await call_next(request)
    return response


async def network_auth_middleware(request: Request, call_next):
    network_id = extract_id(prefix="api/network/net", url=request.url.path)
    try:
        get_technician_with_network(network_id=network_id, technician_id=request.state.user.id)
    except EmptyRowError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Technician {request.state.user.name} does not have client with network {network_id}",
        )
    response = await call_next(request)
    return response
