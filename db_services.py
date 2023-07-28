from typing import Dict, Tuple, Union

from pydantic import BaseModel, Field

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


class JoinStructure(BaseModel):
    from_table: Tuple[str, str]
    select: Tuple[Tuple[str, str], ...]
    join: Tuple[Tuple[str, str], ...]
    on: Tuple[Tuple[Tuple[str, Union[str, int]], ...], ...]


# Should look like this:
# join_vars = {"from_table": ("devices_connections", "dc"),
#              "select": (
#                  ("d1.mac_address", "src_mac_address"),
#                  ("d2.mac_address", "dst_mac_address")),
#              "join": (("devices", "d1"),
#                       ("devices", "d2")),
#              "on": (
#                  (("dc.src_device_id", "d1.id"), ("network_id", 26)),
#                  (("dc.dst_device_id", "d2.id"),)
#              )
#              }
# js = JoinStructure(**join_vars)


@handle_db_exceptions
def join_tables(join_vars: JoinStructure):
    with connection.cursor() as cursor:
        # Should look like this:
        # join_query = """SELECT d1.mac_address AS src_mac_address, d2.mac_address AS dst_mac_address
        # FROM devices_connections dc
        # JOIN devices d1 ON dc.src_device_id = d1.id AND d1.network_id=26
        # JOIN devices d2 ON dc.dst_device_id = d2.id AND d2.network_id=26; """
        selects = [f"{s1} AS {s2}" for s1, s2 in join_vars.select]
        joins = [f"JOIN {j1} {j2} ON" for j1, j2 in join_vars.join]
        ons = [" AND ".join([f"{on1} = {on2}" for on1, on2 in on]) for on in join_vars.on]
        join_query = f"""SELECT {', '.join(selects)} \nFROM {join_vars.from_table[0]} {join_vars.from_table[1]}\n"""
        for join, on in zip(joins, ons):
            join_query += f"{join} {on}\n"
        cursor.execute(join_query)
        rows_lst = create_dicts_list_from_rows(cursor)
        return rows_lst


def close_connection():
    connection.close()


atexit.register(close_connection)
