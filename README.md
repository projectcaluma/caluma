# Caluma Service

[![Build Status](https://travis-ci.com/projectcaluma/caluma.svg?branch=master)](https://travis-ci.org/projectcaluma/caluma)
[![Codecov](https://codecov.io/gh/projectcaluma/caluma/branch/master/graph/badge.svg)](https://codecov.io/gh/projectcaluma/caluma)
[![Pyup](https://pyup.io/repos/github/projectcaluma/caluma/shield.svg)](https://pyup.io/account/repos/github/projectcaluma/caluma/)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/projectcaluma/caluma)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A collaborative form editing service. See [project site](https://projectcaluma.github.io/) for more details.

## Installation

**Requirements**
* docker
* docker-compose

After installing and configuring those requirements, you can download [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) and run the following command:


```bash
docker-compose up -d --build
```

You can now access GraphiQL at [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Development

### Clone

To work on Caluma you first need to clone

```bash
git clone https://github.com/projectcaluma/caluma.git
cd caluma
```

### Open Shell

Once it is cloned you can easily open a shell in the docker container to
open an development environment.

```bash
# needed for permission handling
# only needs to be run once
echo UID=$UID > .env
# open shell
docker-compose run --rm caluma bash
```

### Testing

Once you have shelled in docker container as described above
you can use common python tooling for formatting, linting, testing
etc.

```bash
# linting
flake8
# format code
black .
# running tests
pytest
# create migrations
./manage.py makemigrations
```

### Install new requirements

In case you needed to add new requirements you simply need to build the docker container
again for those to be installed and re-open shell.

```bash
docker-compose build --pull
```

### Setup pre commit

Pre commit hooks is an additional option instead of executing checks in your editor of choice.

```bash
# create virtualenv with tool of your choice
pip install pre-commit
pip install -r requiements-dev.txt -U
pre-commit install
```

## License
Code released under the [MIT license](LICENSE).
