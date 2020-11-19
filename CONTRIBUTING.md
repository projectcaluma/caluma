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
flake8
# format code
black .
# running tests
pytest
# create migrations
./manage.py makemigrations
# install debugger or other temporary dependencies
pip install --user pdbpp
```

Writing of code can still happen outside the docker container of course.

We run pytests in parallel with xdist by default. pytest-django will create
a database per xdist-worker.

To disable xdist completely run:

```bash
pytest -n 0
```

This is especially important when you're updating snapshot tests, because this will fail with
multiple workers:

```bash
pytest --snapshot-update -n 0
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
pip install pre-commit
pip install -r requirements-all.txt -U
pre-commit install --hook=pre-commit
pre-commit install --hook=commit-msg
```

This will activate commit hooks to validate your code as well as your commit
messages.

### Using pipenv

Docker is the way to run and test caluma, but you can install the requirements
for your IDE/editor using pipenv:

```bash
pipenv install --python 3.7 -r requirements.txt
pipenv install -d -r requirements-dev.txt
```

You can also run tests without the caluma-container:

```bash
echo UID=$(id -u) > .env
echo ENV=dev >> .env
docker-compose up -d db
pipenv install --python 3.7 -r requirements.txt
pipenv install -d -r requirements-dev.txt
pipenv shell
pytest
```

or you can use the setup.py command:

```bash
python3 setup.py pipenv
```

You can add any configuration supported by the caluma-container to the .env file.
