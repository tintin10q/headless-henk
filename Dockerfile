FROM debian
WORKDIR /workdir
COPY requirements.txt .
RUN apt-get update && \
	apt-get install -y python3 python3-pip && \
	apt-get install -y libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev && \
	python3 -m pip install -r requirements.txt --break-system-packages && \
	apt-get purge -y libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev && \
	apt-get purge -y python3-pip && \
	apt-get autopurge -y && \
	apt-get clean
COPY . ./
ENTRYPOINT ["python3","-u","gaanmetdiebanaan.py"]
