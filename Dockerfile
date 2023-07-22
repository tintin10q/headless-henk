FROM python:alpine3.17
WORKDIR /workdir
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --break-system-packages
COPY . ./
ENTRYPOINT ["python3","-u","gaanmetdiebanaan.py"]
