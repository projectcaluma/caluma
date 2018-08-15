# Caluma Service

[![Build Status](https://travis-ci.com/projectcaluma/caluma.svg?branch=master)](https://travis-ci.org/projectcaluma/caluma)
[![Codecov](https://codecov.io/gh/projectcaluma/caluma/branch/master/graph/badge.svg)](https://codecov.io/gh/projectcaluma/caluma)
[![Pyup](https://pyup.io/repos/github/projectcaluma/caluma/shield.svg)](https://pyup.io/account/repos/github/projectcaluma/caluma/)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/projectcaluma/caluma)

A collaborative form editing service. See [project site](https://projectcaluma.github.io/) for more dedtails.

## Installation

**Requirements**
* docker
* docker-compose

After installing and configuring those requirements, you should be able to run the following
commands to complete the installation:

```bash
make start
```

## Testing
Run tests by executing:

```bash
make install-dev
make test
```

## License
Code released under the [MIT license](LICENSE).
