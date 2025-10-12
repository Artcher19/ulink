# Описание

Сервис предназначен для сокращения ссылок. Особенности:
- Доступ к формированию ссылок по белому списку IPv4;
- Присвоение контрольного разряда к сокращенной ссылке;

## Стек

| Компонент     | ПО            |
| ------------- | ------------- |
| Backend (API) | FastAPI       |
| Database      | SQLite        |
| Frontend      | HTML, CSS, JS |
| Web-server    | Nginx         |

# Развертывание

Для автоматизированного развертывания сервиса потребуется установленная на вашу виртуальную машину утилита docker и nginx.
## 1. Backend

``` bash
docker run -d \
  --name=ulink-backend \
  -e domain=ulinktest.duckdns.org\
  -e protocol=http\
  -p 8000:8000\
  --restart unless-stopped \
darkbishop19/ulink-backend:latest
```

`domain` - ваш публичный домен.\n
`protocol` - прикладной протокол модели OSI (http/https), который будет использовать ваш сервис

## 2. Frontend

Необходимо установить [index.html](https://github.com/Artcher19/ulink/blob/main/frontend/index.html) в `/var/www/<название вашей папки>`. 
## 3. Nginx

```
geo $restricted_access {
    default 0;
    # Добавьте IP-адреса для белого списка
    10.0.0.1 1;
    46.8.233.148 1;
    # ... другие IP-адреса
}

server {
    listen 80;
    server_name http://ulinktest.duckdns.org;
    
    #backend
    
    # GET /{short_link}
    location ~ ^/(?<short_link>[0-9]+)$ {
        # Разрешаем только GET запросы
        limit_except GET { deny all; }

        proxy_pass http://localhost:8000/$short_link;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # GET /docs - только белый список
    location = /docs {
        # Проверяем IP для доступа
        if ($restricted_access = 0) {
            return 403;
        }

        # Разрешаем только POST
        limit_except GET { deny all; }

        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # POST /links - только белый список
    location = /links {
        # Проверяем IP для доступа
        if ($restricted_access = 0) {
            return 403;
        }

        # Разрешаем только POST
        limit_except POST { deny all; }

        proxy_pass http://localhost:8000/links;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # POST /setup_sqlite - только белый список
    location = /setup_sqlite {
        if ($restricted_access = 0) {
            return 403;
        }

        limit_except POST { deny all; }

        proxy_pass http://localhost:8000/setup_sqlite;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    #frontend - только белый список
    location / {
        if ($restricted_access = 0) {
            return 403;
        }

        root /var/www/ulink-frontend;
        try_files $uri $uri/ /index.html;
    }
}

```
### Привязка SSL

### Белый список

Управление белым списком через конфиг nginx в функции $restricted_access:
```
geo $restricted_access {
    default 0;
    # Добавьте IP-адреса для белого списка
    10.0.0.1 1;
    46.8.233.148 1;
    # ... другие IP-адреса
}
```
