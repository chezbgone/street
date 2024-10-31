FROM python:3.12-alpine as builder

RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY bot/pyproject.toml bot/poetry.lock ./bot/
COPY common ./common

WORKDIR bot

RUN touch README.md

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# make runtime image, without build dependencies for size
FROM python:3.12-alpine as runtime

ENV VIRTUAL_ENV=/app/bot/.venv \
    PATH="/app/bot/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /bot

COPY common ../common
COPY bot .

ENTRYPOINT ["python", "bot.py"]
