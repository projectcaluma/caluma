"""Setuptools package definition."""

import distutils.cmd
import os
from os import path

from setuptools import find_packages, setup

version = {}
with open("caluma/caluma_metadata.py") as fp:
    exec(fp.read(), version)

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


pipenv_setup = """
echo UID=$(id -u) > .env
echo ENV=dev >> .env
docker-compose up -d db
rm -f Pipfile*
touch Pipfile
pipenv install --python 3.7 -r requirements.txt
pipenv install -d -r requirements-dev.txt
""".strip().splitlines()


class PipenvCommand(distutils.cmd.Command):
    description = "setup local development with pipenv"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for cmd in pipenv_setup:
            assert os.system(cmd) == 0
        print(
            "\npipenv run pytest      runs the tests"
            "\npipenv shell           enters the virtualenv"
        )


setup(
    cmdclass={"pipenv": PipenvCommand},
    name=version["__title__"],
    version=version["__version__"],
    description=version["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://projectcaluma.github.io/",
    download_url="https://github.com/projectcaluma/caluma",
    license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    python_requires=">=3.6, <4",
    install_requires=[
        "dateparser<2",
        "django~=2.2",
        "django-cors-headers<4",
        "django-environ<0.5",
        "django-extensions<4",
        "django-filter<3",
        "django-localized-fields<7",
        "django-postgres-extra<3",
        "django-watchman~=1.2.0",
        "djangorestframework<4",
        "django_simple_history<3",
        "graphene-django<=2.8.2",
        "idna<3",
        "minio >= 7, < 8",
        "psycopg2-binary >= 2.8, <2.9",
        "pyjexl<0.3",
        "python-memcached<2",
        "requests<3",
        "urllib3<2",
        "uwsgi<2.1",
    ],
)
