FROM python:3.9-slim

WORKDIR /code
COPY . /code
RUN pip3 install -r requirements.txt
CMD ["uvicorn", "server:app","--host","0.0.0.0"]
