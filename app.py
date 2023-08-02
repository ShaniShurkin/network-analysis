import uvicorn as uvicorn
from fastapi import FastAPI, Request
from exceptions_handling import handle_middleware_exceptions
from auth_services.middlewares import auth_middleware
from routes import login, technician, network

app = FastAPI()


@app.middleware("http")
@handle_middleware_exceptions
def apply_auth_middleware(request: Request, call_next):
    # Apply the authorization middleware only to specific endpoints
    if "login" not in request.url.path:
        return auth_middleware(request, call_next)
    response = call_next(request)
    return response


app.include_router(login.router)
app.include_router(technician.router)
app.include_router(network.router)

if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
# uvicorn your_app_module:app --reload
# kill: netstat -aon | findstr :8000
# TaskKill /PID <pid> /F
