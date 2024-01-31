# Contributing

Contributions to Caluma Service are very welcome! Best have a look at the open [issues](https://github.com/projectcaluma/caluma/issues)
and open a [GitHub pull request](https://github.com/projectcaluma/caluma/compare). See instructions below how to setup development
environment. Before writing any code, best discuss your proposed change in a GitHub issue to see if the proposed change makes sense for the project.

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
poetry run ruff check .
# format code
poetry run ruff format .
# running tests
poetry run pytest
# create migrations
poetry run python manage.py makemigrations
```

Writing of code can still happen outside the docker container of course.

We run pytests in parallel with xdist by default. pytest-django will create
a database per xdist-worker.

To disable xdist completely run:

```bash
poetry run pytest -n 0
```

This is especially important when you're updating snapshot tests, because this will fail with
multiple workers:

```bash
poetry run pytest --snapshot-update -n 0
```

### Install new requirements

In case you're adding new requirements you simply need to build the docker container
again for those to be installed and re-open shell.

```bash
docker-compose build --pull
```

### Setup pre commit

Pre commit hooks is an additional option instead of executing checks in your editor of choice.

First create a virtualenv with the tool of your choice before running below commands:

```bash
poetry install
poetry run pre-commit install --hook=pre-commit
poetry run pre-commit install --hook=commit-msg
```

This will activate commit hooks to validate your code as well as your commit
messages.
