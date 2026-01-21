FROM python:3.12-alpine AS base

RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add wait4ports shadow libpq-dev --no-cache && \
    useradd -m -r -u 1001 caluma && \
    apk del shadow && \
    rm -rf /var/cache/apk/*

ENV DJANGO_SETTINGS_MODULE=caluma.settings.django \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

EXPOSE 8000

FROM base AS build


WORKDIR /app

COPY . ./

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install -U poetry

FROM build AS wheel
WORKDIR /app

RUN poetry build -f wheel && mv ./dist/*.whl /tmp/
RUN pip uninstall -y poetry

FROM build AS dev

WORKDIR /app

RUN poetry install --no-root

USER 1001

CMD [\
    "/bin/sh", "-c", \
    "wait4ports -s 15 tcp://${DATABASE_HOST:-db}:${DATABASE_PORT:-5432} && \
    ./manage.py migrate --no-input && \
    ./manage.py runserver 0.0.0.0:8000 -v 3" \
    ]

FROM base AS prod

COPY manage.py /usr/local/bin
COPY --from=wheel /tmp/*.whl /tmp/

RUN pip install /tmp/*.whl && rm /tmp/*.whl

USER 1001

CMD [\
    "/bin/sh", "-c", \
    "wait4ports -s 15 tcp://${DATABASE_HOST:-db}:${DATABASE_PORT:-5432} && \
    manage.py migrate --no-input && \
    gunicorn --workers 10 --access-logfile - --limit-request-line 16384 --bind :8000 caluma.wsgi" \
    ]
