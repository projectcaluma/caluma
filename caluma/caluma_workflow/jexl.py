from functools import partial
from itertools import chain

from django.core.exceptions import ValidationError
from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.evaluator import Context
from pyjexl.parser import Literal

from ..caluma_core.jexl import JEXL, ExtractTransformSubjectAnalyzer
from .models import Task


def task_exists(slug):
    return (
        slug in FlowJexl.get_all_registered_dynamic_tasks()
        or Task.objects.filter(pk=slug).exists()
    )


def parse_literal(value):
    if isinstance(value, Literal):
        return value.value

    if isinstance(value, list):
        return [parse_literal(item) for item in value]

    return value


class GroupValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "groups" and not isinstance(transform.subject.value, list):
            yield f"{transform.subject.value} is not a valid list of groups."

        yield from super().visit_Transform(transform)


class TaskValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        value = parse_literal(transform.subject.value)

        if transform.name == "tasks":
            if not isinstance(value, list):
                yield f"`{value}` is not a valid list of tasks."
            else:
                for slug in value:
                    if not task_exists(slug):
                        yield f"The task `{slug}` does not exist or is not registered as dynamic task"

        elif transform.name == "task":
            if not isinstance(value, str):
                yield f"`{value}` is not a valid task slug."
            elif not task_exists(value):
                yield f"The task `{value}` does not exist or is not registered as dynamic task"

        yield from super().visit_Transform(transform)


class GroupJexl(JEXL):
    """
    Class for evaluating GroupJexl.

    validation_context is expected to be the following:

    {
        "case": {
            "created_by_group": str,
        },
        "work_item": {
            "created_by_group": str,
        },
        "prev_work_item": {
            "controlling_groups": list of str,
        },
    }
    """

    def __init__(
        self,
        validation_context=None,
        task=None,
        case=None,
        work_item_created_by_user=None,
        prev_work_item=None,
        dynamic_context=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        context_data = None

        if validation_context:
            context_data = {"info": validation_context}

        self.context = Context(context_data)

        self.task = task
        self.case = case
        self.work_item_created_by_user = work_item_created_by_user
        self.prev_work_item = prev_work_item
        self.dynamic_context = dynamic_context

        self.add_transform("groups", self.groups_transform)

    def validate(self, expression):
        return super().validate(expression, GroupValidatingAnalyzer)

    def evaluate(self, expression, context=None):
        value = super().evaluate(expression, context)
        if isinstance(value, list) or value is None:
            return value
        return [value]

    def groups_transform(self, group_names):
        evaluated = [self._get_dynamic_group(group_name) for group_name in group_names]

        return sorted(set(chain(*evaluated)))

    def _get_dynamic_group(self, name):
        for dynamic_groups_class in self.dynamic_groups_classes:
            method = dynamic_groups_class().resolve(name)
            if method:
                value = method(
                    self.task,
                    self.case,
                    self.work_item_created_by_user,
                    self.prev_work_item,
                    self.dynamic_context,
                )

                if not isinstance(value, list):
                    value = [value]

                return value

        return [name]


class FlowJexl(JEXL):
    def __init__(
        self, case=None, user=None, prev_work_item=None, dynamic_context=None, **kwargs
    ):
        super().__init__(**kwargs)

        self.case = case
        self.user = user
        self.prev_work_item = prev_work_item
        self.dynamic_context = dynamic_context

        self.add_transform("task", self.task_transform)
        self.add_transform("tasks", self.tasks_transform)

    def validate(self, expression):
        return super().validate(expression, TaskValidatingAnalyzer)

    def extract_tasks(self, expr):
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=["task"])
        )

        # tasks transforms return a list of literals
        yield from (
            literal.value
            for literal in chain(
                *self.analyze(
                    expr, partial(ExtractTransformSubjectAnalyzer, transforms=["tasks"])
                )
            )
        )

    @classmethod
    def get_all_registered_dynamic_tasks(cls):
        return chain(
            *[
                dynamic_tasks_class().get_registered_dynamic_tasks()
                for dynamic_tasks_class in cls.dynamic_tasks_classes
            ]
        )

    def task_transform(self, task_name):
        all_tasks = self.tasks_transform([task_name])

        if len(all_tasks) > 1:
            raise ValidationError(
                f"The dynamic task `{task_name}` used by the `task` transform should "
                f"not return more than one task -- it returned {len(all_tasks)}"
            )

        return all_tasks[0] if len(all_tasks) else []

    def tasks_transform(self, task_names):
        evaluated = [self._get_dynamic_task(task_name) for task_name in task_names]

        # transform all evaluated tasks into a sorted, unique and flat list
        return sorted(set(chain(*evaluated)))

    def _get_dynamic_task(self, name):
        for dynamic_tasks_class in self.dynamic_tasks_classes:
            method = dynamic_tasks_class().resolve(name)

            if method:
                value = method(
                    self.case, self.user, self.prev_work_item, self.dynamic_context
                )

                if not isinstance(value, list):
                    value = [value]

                return value

        return [name]
