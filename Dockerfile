FROM docker-registry.mw.local/python:3.12-3

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

# Install etcd CLI
RUN apt-get update && apt-get install -y curl && \
    curl -L https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-arm64.tar.gz -o etcd.tar.gz && \
    tar xzf etcd.tar.gz && \
    mv etcd-v3.5.0-linux-arm64/etcdctl /usr/local/bin/ && \
    rm -rf etcd.tar.gz etcd-v3.5.0-linux-arm64

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]
