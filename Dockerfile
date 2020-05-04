
FROM segment/chamber:2.7.5 as build

FROM python:3.7 as base

LABEL "com.datadoghq.ad.logs"='[{"source": "python", "service": "fracfocus"}]'

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.0

# ENV PYTHONPATH "/app:/app/fracfocus:${PYTHONPATH}"
ENV PYTHONPATH=/app/fracfocus

RUN pip install "poetry==$POETRY_VERSION"
ENV PATH "/root/.poetry/bin:/opt/venv/bin:/:${PATH}"

# copy only requirements to cache them in docker layer
WORKDIR /app

# copy deps to cache in separate layer
COPY poetry.lock pyproject.toml /app/

# create placeholder source file
RUN mkdir /app/fracfocus && touch /app/fracfocus/__init__.py

# force symlinks
RUN poetry install --no-dev --no-interaction

# copy project files
COPY . /app

# run again to install app from source
RUN poetry install --no-dev --no-interaction

COPY --from=build /chamber /chamber