import uvicorn as uvicorn
from fastapi import FastAPI, Request
from exceptions_handling import handle_app_exceptions
from auth_services.middlewares import auth_middleware, client_auth_middleware, network_auth_middleware
from routes import login, technician, network

app = FastAPI()


@app.middleware("http")
@handle_app_exceptions
def apply_middleware(request: Request, call_next):
    # Apply the authorization middleware only to specific endpoints
    if "login" not in request.url.path:
        print("1th mw")
        return auth_middleware(request, call_next)
    client_id = request.path_params.get("client_id")
    if client_id:
        print("2th mw")
        return client_auth_middleware(request, call_next)
    network_id = request.path_params.get("network_id")
    if network_id:
        print("3th mw")
        return network_auth_middleware(request, call_next)
    response = call_next(request)
    return response


app.include_router(login.router)
app.include_router(technician.router)
app.include_router(network.router)


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
# uvicorn your_app_module:app --reload
