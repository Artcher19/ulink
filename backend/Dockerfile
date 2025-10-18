FROM python:3.12.3

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["python", "src/main.py"]
