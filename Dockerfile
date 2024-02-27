# syntax=docker/dockerfile:1.6
FROM python:3.11

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/user/.local/bin:${PATH}

RUN <<EOF
    set -eu

    apt-get update

    apt-get install -y \
        gosu

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    groupadd -o -g 1000 user
    useradd -m -o -u 1000 -g user user
EOF

ARG POETRY_VERSION=1.8.1
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/live_inbox_updater
    chown -R user:user /code
EOF

WORKDIR /code/live_inbox_updater
ADD ./pyproject.toml ./poetry.lock /code/live_inbox_updater/

RUN <<EOF
    set -eu

    gosu user poetry install --no-cache --only main
EOF

ADD ./live_inbox_updater /code/live_inbox_updater/live_inbox_updater
ADD ./scripts /code/live_inbox_updater/scripts

ENTRYPOINT [ "gosu", "user", "poetry", "run", "python", "-m", "live_inbox_updater" ]
CMD [ "update" ]
