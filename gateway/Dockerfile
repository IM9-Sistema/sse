FROM python:3.12.2-bookworm

WORKDIR /gateway/
COPY requirements.txt /requirements.txt

RUN python3 -m pip install -r /requirements.txt

COPY . .
CMD uvicorn main:app --host 0.0.0.0 --workers 20