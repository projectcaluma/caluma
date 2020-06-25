from functools import wraps


def register_dynamic_group(dynamic_group_name):
    def wrapper(fn, *arg, **kwarg):
        fn._dynamic_group_name = dynamic_group_name

        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            return fn(self, *args, **kwargs)

        return wrapped

    return wrapper


class BaseDynamicGroups:
    def resolve(self, dynamic_group_name):
        for methodname in dir(self):
            method = getattr(self, methodname)
            if (
                hasattr(method, "_dynamic_group_name")
                and method._dynamic_group_name == dynamic_group_name
            ):
                return method
