from mysql.connector import ProgrammingError, IntegrityError


def handle_app_exceptions(func):
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except Exception as e:
            print(e)

    return inner_function


def handle_db_exceptions(func):
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except TypeError as te:
            msg = f"{te}\n you are recomanded to check what you send"
            print(msg)
            return msg
        except ProgrammingError as pe:
            msg = f"Check your SQL syntax \n{pe}"
            print(msg)
            return msg
        except IntegrityError as ie:
            msg = f"You entered an incorrect value \n{ie}"
            print(msg)
            return msg
        except Exception as e:
            print(e)
            return e

    return inner_function


def handle_auth_exceptions(func):
    def inner_function(*args, **kwargs):
        try:
            func_res = func(*args, **kwargs)
            return func_res
        except FileExistsError as ffe:
            print(ffe)

    return inner_function
