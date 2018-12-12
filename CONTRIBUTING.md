# Contributing

Contributions to Caluma Service are very welcome! Best have a look at the open [issues](https://github.com/projectcaluma/caluma/issues)
and open a [GitHub pull request](https://github.com/projectcaluma/caluma/compare). See instructions below how to setup development
environment.

## Setup development environment

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
