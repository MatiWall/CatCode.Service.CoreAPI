FROM docker-registry.mw.local/python:3.12-3

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]
