FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11


COPY /app/requirements.txt ./requirements.txt

COPY ./app /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt


