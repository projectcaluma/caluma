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

After installing and configuring those requirements, you should be able to run the following
commands to complete the installation:

```bash
make start
```

And access GraphiQL at [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Development

### Testing
Run tests by executing:

```bash
make install-dev
make test
```

### Setup pre commit

Pre commit hooks is an additional option instead of excuting checks in your editor of choice.

```bash
pip install pre-commit
pre-commit install
```

## License
Code released under the [MIT license](LICENSE).
