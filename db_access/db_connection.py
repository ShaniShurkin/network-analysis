import configparser
import os

import mysql.connector


def connect():
    config_data = configparser.ConfigParser()
    root_dir = os.path.dirname(
        os.path.abspath(__file__)
    )
    config_data.read(f"{root_dir}/db_config.ini")
    database = config_data["database"]
    cnx = mysql.connector.connect(
        user=database["user"],
        database=database["database"],
        password=database["password"])
    return cnx
