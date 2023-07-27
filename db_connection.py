import configparser

import mysql.connector


def connect():
    config_data = configparser.ConfigParser()
    config_data.read("config.ini")
    database = config_data["database"]
    cnx = mysql.connector.connect(
        user=database["user"],
        database=database["database"],
        password=database["password"])
    return cnx
# my_cursor.execute("CREATE DATABASE network_analysis")

# mysql_create_table_query = """CREATE TABLE technicians (
#                              id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#                              name VARCHAR(40) NOT NULL,
#                              email VARCHAR(35),
#                              phone_number VARCHAR(10) NOT NULL,
#                              hashed_password VARCHAR(255) NOT NULL);
#                              ALTER TABLE technicians
#                              ADD CONSTRAINT phone_number_format CHECK (phone_number REGEXP '^[0-9]{10}$');"""
