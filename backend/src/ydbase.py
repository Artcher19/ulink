import asyncio
import os
import ydb
from config_reader import config

key_path = os.path.join(os.path.dirname(__file__), '..', 'authorized_key.json')

driver_config = ydb.DriverConfig(
    endpoint = config.ydb_endpoint, database = config.ydb_database, 
        credentials=ydb.iam.ServiceAccountCredentials.from_file(key_file=key_path)
    )

driver = ydb.aio.Driver(driver_config)

# async def run(endpoint, database):
#     driver_config = ydb.DriverConfig(
#         endpoint = endpoint, database = database, 
#         credentials=ydb.iam.ServiceAccountCredentials.from_file(key_file=key_path)
#     )
    
#     async with ydb.aio.Driver(driver_config) as driver:
#         try:
#             return driver
#         except TimeoutError:
#             print("Connect failed to YDB")
#             print("Last reported errors by discovery:")
#             print(driver.discovery_debug_details())
#             exit(1)

async def get_session_pool():
    async with ydb.aio.QuerySessionPool(driver) as pool:
        yield pool

async def select_simple():
    """Пример использования пула сессий"""
    async for pool in get_session_pool():
        print("\nCheck series table...")
        result_sets = await pool.execute_with_retries(
            """
            SELECT *
            FROM links
            """,
        )
        print(result_sets[0])
    
asyncio.run(select_simple())


# # Чтение закрытого ключа из JSON-файла
# with open(key_path, 'r') as f:
#   obj = f.read() 
#   obj = json.loads(obj)
#   private_key = obj['private_key']
#   key_id = obj['id']
#   service_account_id = obj['service_account_id']

# sa_key = {
#     "id": key_id,
#     "service_account_id": service_account_id,
#     "private_key": private_key
# }

# def create_jwt():
#     now = int(time.time())
#     payload = {
#             'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
#             'iss': service_account_id,
#             'iat': now,
#             'exp': now + 3600
#         }

#     # Формирование JWT.
#     encoded_token = jwt.encode(
#         payload,
#         private_key,
#         algorithm='PS256',
#         headers={'kid': key_id}
#     )

#     print(encoded_token)

#     return encoded_token

# def create_iam_token():
#   jwt = create_jwt()
  
#   sdk = yandexcloud.SDK(service_account_key=sa_key, endpoint="api.yandexcloud.kz") # type: ignore
#   iam_service = sdk.client(IamTokenServiceStub)
#   iam_token = iam_service.Create(
#       CreateIamTokenRequest(jwt=jwt)
#   )
  
#   print("Your iam token:")
#   print(iam_token.iam_token)

#   return iam_token.iam_token

# def run(endpoint, database):
#     driver_config = ydb.DriverConfig(
#         endpoint = endpoint, 
#         database = database,
#         credentials=ydb.iam.ServiceAccountCredentials.from_file(key_file=key_path)
#     )
#     with ydb.Driver(driver_config) as driver:
#         try:
#             driver.wait(timeout=5)
#         except TimeoutError:
#             print("Connect failed to YDB")
#             print("Last reported errors by discovery:")
#             print(driver.discovery_debug_details())
#             exit(1)