FROM python:3-alpine

ENV PYTHONUNBUFFERED 1

COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

CMD python /app/run.py