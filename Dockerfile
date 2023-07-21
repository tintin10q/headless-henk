FROM debian
WORKDIR /workdir
COPY requirements.txt .
RUN apt-get update && \
	apt-get install -y python3 python3-pip && \
	python3 -m pip install -r requirements.txt --break-system-packages && \
	apt-get purge -y python3-pip && \
	apt-get autopurge -y && \
	apt-get clean
COPY . ./
ENTRYPOINT python3 gaanmetdiebanaan.py