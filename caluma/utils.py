def is_iterable_and_no_string(value):
    try:
        iter(value)
        return not isinstance(value, str)
    except TypeError:
        return False
