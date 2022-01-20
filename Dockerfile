FROM python:3.7.12@sha256:3908249ce6b2d28284e3610b07bf406c3035bc2e3ce328711a2b42e1c5a75fc1

WORKDIR /app

RUN wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin \
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

ARG REQUIREMENTS=requirements.txt
COPY requirements.txt requirements-dev.txt requirements-all.txt $APP_HOME/
RUN pip install --no-cache-dir --upgrade -r $REQUIREMENTS --disable-pip-version-check

USER caluma

COPY . $APP_HOME

EXPOSE 8000

CMD /bin/sh -c "wait-for-it.sh $DATABASE_HOST:${DATABASE_PORT:-5432} -- ./manage.py migrate && uwsgi"
