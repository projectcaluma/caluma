"""Setuptools package definition."""

from setuptools import find_packages, setup

version = {}
with open("caluma/caluma_metadata.py") as fp:
    exec(fp.read(), version)

setup(
    name=version["__title__"],
    version=version["__version__"],
    description=version["__description__"],
    url="https://projectcaluma.github.io/",
    license="MIT",
    packages=find_packages(),
)
