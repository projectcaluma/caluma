# ![Caluma Service](https://user-images.githubusercontent.com/6150577/60805422-51b1bf80-a180-11e9-9ae5-c794249c7a98.png)

[![Build Status](https://github.com/projectcaluma/caluma/workflows/Tests/badge.svg)](https://github.com/projectcaluma/caluma/actions?query=workflow%3ATests)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/projectcaluma/caluma/blob/main/setup.cfg#L57)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![PyPI](https://img.shields.io/pypi/v/caluma)](https://pypi.org/project/caluma/)
[![License: GPL-3.0-or-later](https://img.shields.io/github/license/projectcaluma/caluma)](https://spdx.org/licenses/GPL-3.0-or-later.html)

Caluma is a collaborative form editing and workflow service.

- Website: [caluma.io](https://caluma.io)
- Documentation: [caluma.gitbook.io](https://caluma.gitbook.io)

## Getting started

**Requirements**

- docker
- docker-compose

After installing and configuring those, download [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/main/docker-compose.yml) and run the following command:

```bash
docker-compose up -d
```
Schema introspection and documentation is available at [http://localhost:8000/graphql](localhost:8000/graphql) and can be accessed using a GraphQL client such as [Altair](https://altair.sirmuel.design/). The API allows to query and mutate form and workflow entities which are described below.

You can read more about running and configuring Caluma in the [documentation](https://caluma.gitbook.io).

## License

Code released under the [GPL-3.0-or-later license](LICENSE).

For further information on our license choice, you can read up on the [corresponding GitHub issue](https://github.com/projectcaluma/caluma/issues/751#issuecomment-547974930).

---

- Contributing guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Maintainer's Handbook: [MAINTAINING.md](MAINTAINING.md)
