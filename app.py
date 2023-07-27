import asyncio
from datetime import timedelta
from typing import List
from scapy.plist import PacketList
from starlette import status
import uvicorn as uvicorn
from fastapi import FastAPI, File, UploadFile, Form, Request, Response, Depends, HTTPException, encoders
from fastapi.security import OAuth2PasswordRequestForm
from authentication import get_password_hash, authenticate_user, create_access_token, Token
from client import add_client
from device import add_devices, add_connections, Device, get_devices_by_network
from middlewares import auth_middleware, client_auth_middleware
from network import add_network
from pcap_analyzer import read_pcap_file, create_devices_list, find_vendor, create_connections_list
from technician import add_tech, BaseTechnician, RegisterTechnician, DBTechnician, get_technician_by_condition, \
    get_all_technicians, delete_technician_by_condition, add_client_to_technician

app = FastAPI()


@app.middleware("http")
async def apply_middleware(request: Request, call_next):
    # Apply the authorization middleware only to specific endpoints
    if request.url.path.startswith("/technician"):
        return await auth_middleware(request, call_next)
    client_id = request.path_params.get("client_id")
    if client_id:
        return await client_auth_middleware(request, call_next)
    response = await call_next(request)
    return response


# todo: send exceptions up
@app.post("/register")
async def register(response: Response, technician: RegisterTechnician):
    hashed_pwd = get_password_hash(technician.password)
    db_tech = DBTechnician(**dict(technician), hashed_password=hashed_pwd)
    add_tech(db_tech)
    access_token = create_access_token(data={"sub": technician.name})
    response.set_cookie(
        key="Authorization", value=f"Bearer {encoders.jsonable_encoder(access_token)}",
        httponly=True
    )
    return "Your registration has been successfully completed"


# todo: get username and password via headers
@app.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(get_user_func=get_technician_by_condition,
                             password=form_data.password,
                             name=form_data.username)
    access_token = create_access_token(data={"sub": user.name})
    response.set_cookie(
        key="Authorization", value=f"Bearer {encoders.jsonable_encoder(access_token)}",
        httponly=True
    )
    return "You've logged in successfully"


@app.get("/technician/")
async def get(request: Request):
    if len(request.query_params) > 0:
        qp = request.query_params
        # send key and value to function that finds a technician by this condition: key == value
        db_technician = get_technician_by_condition(**qp)
        return BaseTechnician(**dict(db_technician))
    technicians: list = get_all_technicians()
    db_technicians = [BaseTechnician(**dict(technician)) for technician in technicians]
    return db_technicians


@app.delete("/technician/")
async def delete_one(request: Request):
    if len(request.query_params) != 1:
        raise HTTPException(status_code=400, detail="One pair of query params is required.")
    qp = request.query_params
    # send key and value to function that deletes a technician by this condition: key == value
    return delete_technician_by_condition(key=list(qp.keys())[0], value=list(qp.values())[0])


@app.get("/technician/token-sanity")
async def checking(request: Request):
    return request.state.user


@app.post("/technician/create-client/{name}")
async def create_client(request: Request, name: str):
    # Creates new client and adds him to current technician
    client_id = add_client(name)
    add_client_to_technician(client_id=client_id,
                             technician_id=request.state.user.id)
    return {"client_id": client_id}


@app.post("/technician/add-client/{id}")
async def add_client_to_current_technician(request: Request, id: int):
    return add_client_to_technician(client_id=id,
                                    technician_id=request.state.user.id)


# todo: make it async and solve problem with vendor( when async)
@app.post("/technician/network")
def analyze_network(file: UploadFile = File(...), client_id: int = Form(...)):
    network_id: int = add_network(client_id)
    packets_lst: PacketList = read_pcap_file(file.file)
    dvcs_lst: List[Device] = create_devices_list(packets_lst, network_id)
    add_devices(dvcs_lst)
    dvcs_with_id_lst: List[Device] = get_devices_by_network(network_id)
    connections_list: [List[dict]] = create_connections_list(packets_lst, dvcs_with_id_lst)
    add_connections(connections_list)
    return {"network_id": network_id}


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
