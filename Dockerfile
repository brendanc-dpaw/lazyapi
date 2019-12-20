FROM tiangolo/uvicorn-gunicorn:python3.7

COPY . /app
RUN pip install -r /app/requirements.txt
