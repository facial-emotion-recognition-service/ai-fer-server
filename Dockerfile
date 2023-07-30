FROM python:3.10-buster

ADD ai_fers ./ai_fers

COPY requirements.txt .
COPY setup.py .

RUN pip install --upgrade pip
RUN pip install .

EXPOSE 8000

WORKDIR /ai_fers/server

CMD ["python", "main_server.py", "runserver", "0.0.0.0:8000"]
