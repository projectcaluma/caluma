from collections import Counter


def list_duplicates(iterable):
    """Return a set of duplicates in given iterator."""
    return {key for key, count in Counter(iterable).items() if count > 1}
