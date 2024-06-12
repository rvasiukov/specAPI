FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Set the working directory inside the container
WORKDIR /home/ya-user

COPY /app/requirements.txt ./requirements.txt

COPY ./app /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt


