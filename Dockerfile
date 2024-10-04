FROM python:3.12-slim

ENV POETRY_HOME=/app
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=true

RUN pip install poetry
WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

# Install etcd CLI based on the architecture
ARG TARGETPLATFORM
RUN apt-get update && apt-get install -y curl && \
    ARCH="$(echo ${TARGETPLATFORM} | awk -F '/' '{print $2}')" && \
    if [ "${ARCH}" = "amd64" ]; then \
        URL="https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-amd64.tar.gz"; \
    elif [ "${ARCH}" = "arm64" ]; then \
        URL="https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-arm64.tar.gz"; \
    else \
        echo "Unsupported architecture: ${ARCH}" && exit 1; \
    fi && \
    curl -L ${URL} -o etcd.tar.gz && \
    tar xzf etcd.tar.gz && \
    mv etcd-*/etcdctl /usr/local/bin/ && \
    rm -rf etcd.tar.gz etcd-*

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]
