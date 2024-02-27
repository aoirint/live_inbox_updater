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

ARG CONTAINER_UID=1000
ARG CONTAINER_GID=1000
RUN <<EOF
    set -eu

    groupadd --non-unique --gid "${CONTAINER_GID}" user
    useradd --non-unique --uid "${CONTAINER_UID}" --gid "${CONTAINER_GID}" --create-home user
EOF

ARG POETRY_VERSION=1.8.1
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "${CONTAINER_UID}:${CONTAINER_GID}" /home/user/.cache
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/live_inbox_updater
    chown -R "${CONTAINER_UID}:${CONTAINER_GID}" /code/live_inbox_updater
EOF

WORKDIR /code/live_inbox_updater
ADD ./pyproject.toml ./poetry.lock /code/live_inbox_updater/

RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --only main
EOF

ADD ./README.md /code/live_inbox_updater/
ADD ./live_inbox_updater /code/live_inbox_updater/live_inbox_updater
ADD ./scripts /code/live_inbox_updater/scripts

RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --only main
EOF

ENTRYPOINT [ "gosu", "user", "poetry", "run", "python", "-m", "live_inbox_updater" ]
CMD [ "update" ]
