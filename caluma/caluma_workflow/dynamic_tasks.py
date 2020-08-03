from functools import wraps

name_attr = "_dynamic_task_name"


def register_dynamic_task(dynamic_task_name):
    """Decorate function to register a dynamic task."""

    def wrapper(fn, *arg, **kwarg):
        setattr(fn, name_attr, dynamic_task_name)

        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            return fn(self, *args, **kwargs)

        return wrapped

    return wrapper


class BaseDynamicTasks:
    """Basic dynamic tasks class to be extended by any dynamic tasks class implementation.

    In combination with the decorator `@register_dynamic_task` a dynamic task
    class can extend the JEXL `task` and `tasks` transform used in the `next`
    property of a task.

    A dynamic tasks class could look like this:

    >>> from caluma.caluma_workflow.dynamic_tasks import (
    ...     BaseDynamicTasks,
    ...     register_dynamic_task,
    ... )
    ...
    ...
    ... class CustomDynamicTasks(BaseDynamicTasks):
    ...     @register_dynamic_task("audit-forms")
    ...     def resolve_audit_forms(self, case, user, prev_work_item, context):
    ...         needs_extra_audit = case.document.answers.filter(
    ...             question_id="is-extra-complicated",
    ...             value="is-extra-complicated-yes"
    ...         ).exists()
    ...         next_tasks = ["audit"]
    ...
    ...         if needs_extra_audit:
    ...             next_tasks.append("extra-audit")
    ...
    ...         return next_tasks
    """

    def get_registered_dynamic_tasks(self):
        return filter(
            None,
            [
                getattr(getattr(self, methodname), name_attr, None)
                for methodname in dir(self)
            ],
        )

    def resolve(self, dynamic_task_name):
        for methodname in dir(self):
            method = getattr(self, methodname)

            if getattr(method, name_attr, None) == dynamic_task_name:
                return method
