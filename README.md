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

After installing and configuring those, download [compose.yaml](https://github.com/projectcaluma/caluma/blob/main/compose.yaml) and run the following command:

```bash
docker compose up -d
```
Schema introspection and documentation is available at [http://localhost:8000/graphql](localhost:8000/graphql) and can be accessed using a GraphQL client such as [Altair](https://altair.sirmuel.design/). The API allows to query and mutate form and workflow entities which are described below.

You can read more about running and configuring Caluma in the [documentation](https://caluma.gitbook.io).

## YAML scaffold import command

You can scaffold forms, questions and options with a YAML file via Django management command:

```bash
./manage.py import_forms /path/to/forms.yaml
```

Use `--update` to allow updating already existing entities. Without this flag, the command aborts on the first existing form/question/option slug.

Use `--dry-run` to validate the file (schema, references, duplicates, conflicts) without persisting any changes.

The YAML format is optimized for fast initial scaffolding:

- Top-level key is `forms`.
- Form `slug` is optional and defaults to slugified `label`/`name`.
- Question `type` defaults to `text`.
- If `options` are defined and `type` is omitted, question type defaults to `choice`.
- Question `required` defaults to `false` and maps to Caluma `is_required` JEXL (`\"true\"`/`\"false\"`).
- Option entries can be plain strings or objects (`label`, `slug`, `is_hidden`, `meta`).
- Option slugs default to question-scoped values: `<question-slug>-<option-label-slug>`.
- Localized fields can be plain strings or language maps; a top-level `language` key (or `--language`) converts plain strings to localized values for that language.

Example:

```yaml
language: de
forms:
  - label: Hauptformular
    questions:
      - label: Freitext
      - label: Auswahl
        options:
          - Erste Option
          - label: Zweite Option
  - label: Übergeordnete Form
    questions:
      - label: Zeilen
        type: table
        row_form: hauptformular
```

## License

Code released under the [GPL-3.0-or-later license](LICENSE).

For further information on our license choice, you can read up on the [corresponding GitHub issue](https://github.com/projectcaluma/caluma/issues/751#issuecomment-547974930).

---

- Contributing guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Maintainer's Handbook: [MAINTAINING.md](MAINTAINING.md)
