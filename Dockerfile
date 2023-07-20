FROM python
WORKDIR /workdir
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY . .
RUN /root/.local/bin/poetry install
CMD /root/.local/bin/poetry run gaanmetdiebanaan
