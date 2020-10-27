FROM tiangolo/uvicorn-gunicorn:python3.7
LABEL org.opencontainers.image.source https://github.com/dbca-wa/lazyapi

COPY . /app
RUN pip install -r /app/requirements.txt
