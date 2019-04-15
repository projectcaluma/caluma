class BaseDataSource:
    """Basic data source class to be extended by any data source implementation.

    The `get_data`-method should return an iterable. This iterable can contain strings,
    ints, floats and also iterables. Those contained iterables can consist of maximally
    two items. The first will be used for the option name, the second one for it's
    value. If only one value is provided, this value will also be used as choice name.

    Examples:
        ["some", "strings", ...]
        ["some", "strings", ("now", 5), ["and", "that"], ...]

    Properties:
        info: Informational string about this data source
        timeout: timeout seconds for the cache (defaults to 2600)
        default: default value to return if execution of `get_data()` fails
                 (defaults to [])

    A custom data source class could look like this:
    ```
    >>> from caluma.core.data_sources import BaseDataSource
    ... import requests
    ...
    ...
    ... class CustomDataSource(BaseDataSource):
    ...     info = 'User choices from "someapi"'
    ...     timeout = 3600
    ...     default = []
    ...
    ...     def get_data(self, info):
    ...         response = requests.get(
    ...             f"https://someapi/?user={info.context.request.user.username}"
    ...         )
    ...         return [result["value"] for result in response.json()["results"]]
    ```

    """

    info = None
    timeout = 3600
    default = []

    def __init__(self):
        pass

    def get_data(self, info):  # pragma: no cover
        raise NotImplementedError()
