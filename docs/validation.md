# Validation

## Javascript Expression Language

Caluma relies on Javascript Expression Language alias
[JEXL](https://github.com/TomFrost/Jexl) for defining powerful yet simple
expressions for complex validation and flow definitions.  Reason for
using JEXL over other languages is that it can be simply implemented
in the backend and frontend as of its defined small scope. This allows
frontends in the browser to validate data in exactly the same way as
the server will, while not limiting validation to simple regexes.

This speeds up user interaction a good deal


## FormatValidators

FormatValidator classes can validate input data for answers, based on rules set on the question.

There are a variety of base FormatValidators ready to use. There is also an [extension
point](extending.md#formatvalidator-classes) for them.

List of built-in base FormatValidators:

* email
* phone-number
