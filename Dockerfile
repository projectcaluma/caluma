FROM python:3.6

WORKDIR /app

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin \
&& chmod +x /usr/local/bin/wait-for-it.sh

ENV DJANGO_SETTINGS_MODULE caluma.settings
ENV UWSGI_INI /app/uwsgi.ini

COPY requirements.txt /app
RUN pip install --upgrade -r requirements.txt

COPY . /app

EXPOSE 80
CMD /bin/sh -c "wait-for-it.sh $DATABASE_HOST:$DATABASE_PORT -- ./manage.py migrate && uwsgi"
