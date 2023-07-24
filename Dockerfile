FROM python:3-slim
WORKDIR /workdir
COPY requirements.txt .
RUN apt-get update && \
        apt-get install -y libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev --no-install-recommends && rm -rf /var/lib/apt/lists/* &&\
        pip install --no-cache-dir -r requirements.txt  && \
        apt-get purge -y libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev && \
    apt-get autopurge -y && apt-get clean
COPY . ./
ENTRYPOINT ["python3","-u","gaanmetdiebanaan.py"]
