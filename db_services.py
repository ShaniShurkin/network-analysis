from db_connection import connect
from exceptions_handling import handle_db_exceptions
import atexit

connection = connect()


@handle_db_exceptions
def get_all(table_name):
    with connection.cursor() as cursor:
        select_all_sql = f"SELECT * FROM {table_name}"
        cursor.execute(select_all_sql)
        rows_lst = create_dicts_list_from_rows(cursor)
        return rows_lst


@handle_db_exceptions
def add_row(table_name, obj):
    with connection.cursor() as cursor:
        data = dict(obj)
        insert_query = "INSERT INTO {} ({}) VALUES ({})".format(
            table_name, ", ".join(data.keys()), ", ".join(["%s"] * len(data))
        )
        cursor.execute(insert_query, tuple(data.values()))
        connection.commit()
        return cursor.lastrowid


@handle_db_exceptions
def add_rows(table_name, obj_lst):
    with connection.cursor() as cursor:
        data = dict(obj_lst[0])
        insert_query = "INSERT INTO {} ({}) VALUES ({})".format(
            table_name, ", ".join(data.keys()), ", ".join(["%s"] * len(data))
        )
        vals = [tuple(dict(obj).values()) for obj in obj_lst]
        cursor.executemany(insert_query, vals)
        connection.commit()
        return cursor.lastrowid


@handle_db_exceptions
def get_one_by_condition(table_name, **kwargs):
    with connection.cursor() as cursor:
        select_query = create_query_with_conditions("SELECT *", table_name, **kwargs)
        cursor.execute(select_query)
        row = cursor.fetchone()
        if not row:
            raise Exception(f"Error: no such row in {table_name}")
        column_names = [column[0] for column in cursor.description]
        row_dict = dict(zip(column_names, row))
        return row_dict


@handle_db_exceptions
def get_many_by_condition(table_name, **kwargs):
    with connection.cursor() as cursor:
        select_query = create_query_with_conditions("SELECT *", table_name, **kwargs)
        cursor.execute(select_query)
        rows_lst = create_dicts_list_from_rows(cursor)
        return rows_lst


@handle_db_exceptions
def delete_one_by_condition(table_name, **kwargs):
    with connection.cursor() as cursor:
        delete_query = create_query_with_conditions("DELETE FROM", table_name, **kwargs)
        cursor.execute(delete_query)
        connection.commit()
        return cursor.lastrowid


@handle_db_exceptions
def create_query_with_conditions(query_start, table_name, **kwargs):
    query = f"{query_start} FROM {table_name} WHERE"
    for key, value in kwargs.items():
        if type(value) is str:
            value = f"'{value}'"
        query += f" {key}={value} AND "
    query = query[:-5]
    return query


@handle_db_exceptions
def create_dicts_list_from_rows(cursor):
    column_names = [column[0] for column in cursor.description]
    rows_lst = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    return rows_lst


def close_connection():
    connection.close()


atexit.register(close_connection)
