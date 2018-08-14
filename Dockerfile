FROM python:3.6

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE caluma.settings
ENV UWSGI_INI /app/uwsgi.ini

COPY requirements.txt /app
RUN pip install -U -r requirements.txt

COPY . /app

EXPOSE 80
CMD ["uwsgi"]
