from functools import wraps

from mysql.connector import ProgrammingError, IntegrityError


class EmptyRowError(Exception):
    """Exception raised when there are no rows as required.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Error: no rows as required"):
        self.message = message
        super().__init__(self.message)


def handle_app_exceptions(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except Exception as e:
            print(e)
            return e

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
            msg = f"{te}\nyou are recomanded to check what you send"
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
