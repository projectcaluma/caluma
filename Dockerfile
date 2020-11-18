FROM python:3.7.6@sha256:af8fc40f758a1847b87db6c0239f2a5fb70622adc95a68bf1b736fa57ad332bc

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
