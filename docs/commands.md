# Commands

A set of custom commands that can help with routine tasks around a caluma installation.

## `cleanup_history`

Cleanup historical records, eg. historical answers for old, inexistent questions.
See [Historical Records](historical-records.md) for details.


## `dump_caluma_config`

Similarly to djangos built-in `dumpdata`, `dump_caluma_config` dumps database entries to django fixtures.
It's tailored for the usage of (design-time) configuration and currently supports dumping of forms with all its attached questions, options etc.

Example usage:
`python manage.py dump_caluma_config --model caluma_form.Form my-form other-form`

For more options see `python manage.py dump_caluma_config --help`
