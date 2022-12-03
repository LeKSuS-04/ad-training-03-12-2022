FROM python:3.10.8-alpine

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD src /app

WORKDIR /app

CMD ["gunicorn", "main:app", "--workers=2", "-b", "0.0.0.0:5000"]
