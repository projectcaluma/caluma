FROM python:3.6@sha256:a01b318f4768a20a679da7d901de1676de0079bf85a01179611dd3fec67d5d66

RUN wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin \
  && chmod +x /usr/local/bin/wait-for-it.sh \
  && mkdir -p /app \
  && groupadd -r caluma -g 901 && useradd -u 901 -r -g 901 caluma

WORKDIR /app

ARG REQUIREMENTS=requirements.txt

ENV PYTHONUNBUFFERED=1
ENV HOME=/home/caluma
ENV APP_HOME=/app
ENV DJANGO_SETTINGS_MODULE caluma.settings
ENV UWSGI_INI /app/uwsgi.ini

COPY requirements.txt requirements-dev.txt $APP_HOME/
RUN pip install --no-cache-dir --upgrade -r $REQUIREMENTS --disable-pip-version-check

USER caluma

COPY . $APP_HOME

EXPOSE 8000

CMD /bin/sh -c "wait-for-it.sh $DATABASE_HOST:${DATABASE_PORT:-5432} -- ./manage.py migrate && uwsgi"
