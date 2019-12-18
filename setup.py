"""Setuptools package definition."""

import distutils.cmd
import os

from setuptools import find_packages, setup

version = {}
with open("caluma/caluma_metadata.py") as fp:
    exec(fp.read(), version)

pipenv_setup = """
echo UID=$(id --user) > .env
echo ENV=dev >> .env
docker-compose up -d db
rm -f Pipfile*
touch Pipfile
pipenv install --python 3.6 -r requirements.txt
pipenv install -d -r requirements-dev.txt
""".strip().splitlines()


def deps_from_file(filename):
    lines = [line.strip().split("#")[0] for line in open(filename).readlines()]
    # filter out comment lines
    return [line for line in lines if line]


dependencies = deps_from_file("requirements.txt")
dev_dependencies = deps_from_file("requirements-dev.txt")


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
    url="https://projectcaluma.github.io/",
    license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    packages=find_packages(),
    install_requires=dependencies,
)
