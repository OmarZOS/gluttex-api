FROM python:3.10-alpine
WORKDIR /code
COPY . /code

COPY ./certificates/auth_cert.pem /usr/local/share/ca-certificates
RUN update-ca-certificates

RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "server:app","--host","0.0.0.0"]
