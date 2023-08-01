import configparser

# creating object of configparser
config = configparser.ConfigParser()

config.add_section("database")

config.set("database", "user", "root")
config.set("database", "password", "")
config.set("database", "database", "network_analysis")

with open("../db_access/db_config.ini", 'w') as conf:
    config.write(conf)
