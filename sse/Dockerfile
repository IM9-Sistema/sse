FROM python:latest

COPY . /sse/.

RUN python3 -m pip install /sse/requirements.txt

CMD cd /sse/ && uvicorn main:app --host 0.0.0.0