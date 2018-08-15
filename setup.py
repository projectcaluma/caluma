"""Setuptools package definition."""

from setuptools import find_packages, setup

setup(
    name='caluma',
    version='0.0.0',
    description='Caluma Service providing GraphQL API ',
    url='https://projectcaluma.github.io/',
    license='MIT',
    packages=find_packages(),
)
