FROM python:3.12-alpine AS builder

RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY server/pyproject.toml server/poetry.lock ./server/
COPY common ./common

WORKDIR server

RUN touch README.md

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# make runtime image, without build dependencies for size
FROM python:3.12-alpine AS runtime

ENV VIRTUAL_ENV=/app/server/.venv \
    PATH="/app/server/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /server

COPY common ../common
COPY server .

ENTRYPOINT ["hypercorn", "--bind", "0.0.0.0:3000", "server:app"]
