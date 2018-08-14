"""Setuptools package definition."""

from setuptools import find_packages, setup

setup(
    name='caluma',
    version='0.0.0',
    author='Adfinis SyGroup AG',
    author_email='https://adfinis-sygroup.ch/',
    description='Caluma Service providing GraphQL API ',
    url='https://adfinis-sygroup.ch/',
    packages=find_packages(),
)
