# Some common exceptions


class ConfigurationError(Exception):
    """Invalid configuration detected.

    Use this exception type if a configuration does not make
    sense or is generally un-processable.

    For example: circular dependencies in JEXL expressions,
    invalid form hierarchies etc
    """


class QuestionMissing(Exception):
    pass
