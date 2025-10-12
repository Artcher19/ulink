import asyncio
import sqlalchemy
import ydb
from config_reader import config
import base64


def initializator(endpoint, database):
    with ydb.Driver(
        endpoint=endpoint,
        database=database,
        credentials=ydb.iam.ServiceAccountCredentials.from_file('../authorized_key.json')
    ) as driver:
        try:
            driver.wait(timeout=5)
        except TimeoutError:
            print("Connect failed to YDB")
            print("Last reported errors by discovery:")
            print(driver.discovery_debug_details())
            exit(1)

initializator(endpoint=config.ydb_endpoint, database=config.ydb_database)