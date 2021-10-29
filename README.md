# ![Caluma Service](https://user-images.githubusercontent.com/6150577/60805422-51b1bf80-a180-11e9-9ae5-c794249c7a98.png)

[![Build Status](https://github.com/projectcaluma/caluma/workflows/Tests/badge.svg)](https://github.com/projectcaluma/caluma/actions?query=workflow%3ATests)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/projectcaluma/caluma/blob/main/setup.cfg#L57)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![PyPI](https://img.shields.io/pypi/v/caluma)](https://pypi.org/project/caluma/)
[![License: GPL-3.0-or-later](https://img.shields.io/github/license/projectcaluma/caluma)](https://spdx.org/licenses/GPL-3.0-or-later.html)

A collaborative form editing service.

## What is Caluma Service?

Caluma Service is the core part of the Caluma project providing a
[GraphQL API](https://graphql.org/). For a big picture and to learn what Caluma
does for you, have a look at [caluma.io](https://caluma.io)

## Getting started

### Installation

NOTE: We recommend using Caluma as a dedicated service. However, it is possible to integrate
Caluma into a django project. You can read about this [here](docs/django-apps.md).

**Requirements**

- docker
- docker-compose

After installing and configuring those, download [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/main/docker-compose.yml) and run the following command:

```bash
docker-compose up -d
```
Schema introspection and documentation is available at http://localhost:8000/graphql and can be accessed using a GraphQL client such as [Altair](https://altair.sirmuel.design/). The API allows to query and mutate form and workflow entities which are described below.

Caluma is a [12factor app](https://12factor.net/) which
means that configuration is stored in environment variables.
Different environment variable types are explained at
[django-environ](https://github.com/joke2k/django-environ#supported-types).

You can read more about running and configuring Caluma under
[docs/configuration.md](docs/configuration.md)

### Debugging

Set environment variable `ENV` to `dev` to enable debugging capabilities. Don't use this in production as it exposes confidential information!

This enables [Django Debug Middleware](https://docs.graphene-python.org/projects/django/en/latest/debug/).

For profiling you can use `./manage.py runprofileserver`. See [docker-compose.override.yml](docker-compose.override.yml) for
an example.

## License

Code released under the [GPL-3.0-or-later license](LICENSE).

For further information on our license choice, you can read up on the [corresponding GitHub issue](https://github.com/projectcaluma/caluma/issues/751#issuecomment-547974930).

## Further reading

- [Installation & Configuration](docs/configuration.md) - Get started installing
  Caluma in a production context
- [Contributing](CONTRIBUTING.md) - If you want to help us, here's
  how to start with your first contribution.
- [Caluma Guide](docs/guide.md) - How to get up and running with Caluma
- [Workflow Concepts](docs/workflow-concepts.md) - How to use caluma workflows
- [Historical Records](docs/historical-records.md) - Undo and audit trail
  functionality
- [GraphQL](docs/graphql.md) - Further information on how to use the GraphQL
  interface
- [Validation](docs/validation.md) - Validation of user input
- [Extending Caluma](docs/extending.md) - Extensions: Data visibility and
  permissions
- [Caluma Events](docs/events.md) - Reacting upon Caluma Events
- [Using Caluma as django apps](docs/django-apps.md)
- [Interfaces](docs/interfaces.md)
- [Maintainer's Handbook](docs/maintainers.md) - HOWTO for various maintainer's
  tasks
