FROM python:3.8.12-slim@sha256:8be266ad3b9d0381396ad4fe705d39217773343fdb1efdf909c23daa1fcdf3ac

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential \
&& wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin \
&& chmod +x /usr/local/bin/wait-for-it.sh \
&& mkdir -p /app \
&& useradd -u 901 -r caluma --create-home \
# all project specific folders need to be accessible by newly created user but also for unknown users (when UID is set manually). Such users are in group root.
&& chown -R caluma:root /home/caluma \
&& chmod -R 770 /home/caluma

# needs to be set for users with manually set UID
ENV HOME=/home/caluma

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV DJANGO_SETTINGS_MODULE caluma.settings.django
ENV UWSGI_INI /app/uwsgi.ini

RUN pip install -U poetry

ARG INSTALL_DEV_DEPENDENCIES=false
COPY pyproject.toml poetry.lock $APP_HOME/
RUN if [ "$INSTALL_DEV_DEPENDENCIES" = "true" ]; then poetry install; else poetry install --no-dev; fi

USER caluma

COPY . $APP_HOME

EXPOSE 8000

CMD /bin/sh -c "wait-for-it.sh $DATABASE_HOST:${DATABASE_PORT:-5432} -- poetry run python manage.py migrate && poetry run uwsgi"
