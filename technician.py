from typing import Optional
from pydantic import BaseModel
from db_services import get_all, add_row, get_one_by_condition, delete_one_by_condition

TABLE_NAME = "technicians"


class BaseTechnician(BaseModel):
    name: str
    phone_number: str
    email: Optional[str]
    id: Optional[int] = None


class DBTechnician(BaseTechnician):
    hashed_password: str


class RegisterTechnician(BaseTechnician):
    password: str


def get_all_technicians():
    return get_all(TABLE_NAME)


def add_tech(tech: DBTechnician):
    return add_row(TABLE_NAME, tech)


def get_technician_by_condition(**kwargs):
    tech = get_one_by_condition(TABLE_NAME, **kwargs)
    if type(tech) is dict:
        return DBTechnician(**tech)
    return tech


def delete_technician_by_condition(**kwargs):
    tech = delete_one_by_condition(TABLE_NAME, **kwargs)
    if type(tech) is dict:
        return DBTechnician(**tech)
    return tech


def add_client_to_technician(client_id: int, technician_id: int):
    return add_row("clients_technicians", {"client_id": client_id, "technician_id": technician_id})
