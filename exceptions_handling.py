from functools import wraps
from fastapi import HTTPException
from mysql.connector import ProgrammingError, IntegrityError
from fastapi.responses import JSONResponse


class EmptyRowError(Exception):
    # Exception raised when there are no rows as required
    def __init__(self, message="Error: no rows as required"):
        self.message = message
        super().__init__(self.message)


def handle_app_exceptions(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except HTTPException as he:
            raise he

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return inner_function


def handle_middleware_exceptions(func):
    @wraps(func)
    async def inner_function(*args, **kwargs):
        try:
            func_res = await func(*args, **kwargs)
            return func_res
        except HTTPException as he:
            print(he)
            return JSONResponse(status_code=he.status_code, content={'detail': he.detail})

        except Exception as e:
            return JSONResponse(status_code=500, content={'detail': str(e)})

    return inner_function


def handle_db_exceptions(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except EmptyRowError as ere:
            raise ere
        except TypeError as te:
            msg = f"{te}\nYou are advised to check what you send"
            print(msg)
            raise TypeError(msg)
        except ProgrammingError as pe:
            msg = f"Check your SQL syntax \n{pe}"
            raise TypeError(msg)
        except IntegrityError as ie:
            msg = f"You entered an incorrect value \n{ie}"
            raise IntegrityError(msg)
        except Exception as e:
            raise e

    return inner_function


def handle_auth_exceptions(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except FileExistsError as ffe:
            print(ffe)

    return inner_function
