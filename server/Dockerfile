FROM python:3.11-alpine
WORKDIR /code
COPY . /code

# RUN pip install  --upgrade pip

COPY ./certificates/auth_cert.pem /usr/local/share/ca-certificates
RUN update-ca-certificates

RUN pip3 install -r requirements.txt
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${API_PORT}"]
