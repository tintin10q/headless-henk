FROM ubuntu
RUN apt-get update && apt-get install -y python3 curl && apt-get clean
WORKDIR /workdir
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY . .
RUN /root/.local/bin/poetry install
CMD /root/.local/bin/poetry run gaanmetdiebanaan
