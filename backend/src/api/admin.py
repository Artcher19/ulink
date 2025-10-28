from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import basic_auth, SessionDep
from database import setup_database, reload_database_connection, engine
from config_reader import config
from s3_functions import s3client
from datetime import datetime
from api import crud, utils
router = APIRouter(tags=['admin'], prefix='/admin')

@router.post('/setup_database', summary='Создать базу данных', description='Создаете БД на ВМ, если БД не создана')
async def post_database(auth: str = Depends(basic_auth)):
    try:
        await setup_database()
        return {"detail": "База данных создана успешно"}
    except Exception as e:
        if str(e) == "База данных уже создана":
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=f"Ошибка при создании базы данных: {str(e)}")
        
@router.post('/backup_database', summary='Создать backup базы данных', description='Отправляет файл базы данных в S3 по текущей дате')
async def post_database_backup(auth: str = Depends(basic_auth)):
    try:
        file_path = config.sqlite_database_path
        file_name, file_format = file_path.split("/")[-1].split(".")
        s3_folder_name = "database_backups/"
        object_name = f"{s3_folder_name}{file_name}_{datetime.now().strftime('%Y-%m-%d')}.{file_format}"
        await s3client.upload_file(file_path, object_name)
        return {"detail": "Бекап создан"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка создания backup: {str(e)}")
    
@router.post('/recover_database', summary='Восстановить базу данных из backup', description='Восстанавливает на сервере базу данных из backup в s3')
async def post_recover_database(object_name: str, auth: str = Depends(basic_auth)):
    try:
        object_name = f"{object_name}"
        content = await s3client.get_file(object_name)
        await engine.dispose()
        await utils.delete_current_db_files(config.sqlite_database_path)
        with open(config.sqlite_database_path, 'wb') as local_file:
            local_file.write(content)
        await reload_database_connection()
        return {"detail": f"База данных восстановлена из {object_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка восстановления базы данных: {str(e)}")
    
@router.get('/healthcheck')
async def get_healthcheck(session: SessionDep, auth: str = Depends(basic_auth)):
    try:
        await crud.get_full_link_by_short_link(100014, session)
        await utils.calculate_control_digit(10001)
        return {"detail": "Success"}
    except Exception as e:
        raise HTTPException(status_code = 400, detail=f"База данных недоступна: {str(e)}")