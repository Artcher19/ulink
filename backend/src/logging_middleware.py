from datetime import datetime, timedelta, timezone
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов в JSON формате"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Читаем тело запроса для не-GET запросов
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8')[:1000]  # Ограничиваем размер
            except Exception:
                body = "[unable to read body]"
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Определяем уровень логирования на основе статус кода
        status_code = response.status_code
        if 200 <= status_code < 400:
            log_level = "INFO"
        elif 400 <= status_code < 500:
            log_level = "WARN"
        else:
            log_level = "ERROR"

        moscow_tz = timezone(timedelta(hours=3))
        moscow_time = datetime.now(moscow_tz)

        # Формируем структурированный лог
        process_time = time.time() - start_time
        log_data = {
            "timestamp": moscow_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "level": log_level,  # Динамический уровень на основе статус кода
            "type": "http_request",
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": status_code,
            "response_time_ms": round(process_time * 1000, 2),
            "content_length": response.headers.get("content-length", 0),
        }
        
        # Добавляем тело запроса если есть
        if body:
            log_data["request_body"] = body
        
        # Выводим JSON напрямую в stdout для Fluent Bit
        print(json.dumps(log_data, ensure_ascii=False), flush=True)
        
        return response