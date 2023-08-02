from fastapi import APIRouter, Response, Depends, encoders
from fastapi.security import OAuth2PasswordRequestForm
from auth_services.authentication import get_password_hash, authenticate_user, create_access_token
from exceptions_handling import handle_app_exceptions
from entity_services.technician import add_tech, RegisterTechnician, DBTechnician, \
    get_technician_by_condition

router = APIRouter(prefix="/api/login")


@router.post("/")
@handle_app_exceptions
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


@router.post("/new-user")
@handle_app_exceptions
def register(response: Response, technician: RegisterTechnician):
    hashed_pwd = get_password_hash(technician.password)
    db_tech = DBTechnician(**dict(technician), hashed_password=hashed_pwd)
    add_tech(db_tech)
    access_token = create_access_token(data={"sub": technician.name})
    response.set_cookie(
        key="Authorization", value=f"Bearer {encoders.jsonable_encoder(access_token)}",
        httponly=True
    )
    return "Your registration has been successfully completed"
