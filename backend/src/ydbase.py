import json
import os
from datetime import datetime
import ydb
from config_reader import config

key_path = os.path.join(os.path.dirname(__file__), '..', 'authorized_key.json')

async def run():
    async with ydb.aio.Driver(
          endpoint = config.ydb_endpoint, 
          database = config.ydb_database, 
          credentials=ydb.iam.ServiceAccountCredentials.from_file(key_file=key_path)
          ) as driver:
             await driver.wait(timeout=5, fail_fast=True)

             async with ydb.aio.QuerySessionPool(driver) as pool:
                pass


