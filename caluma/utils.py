from functools import wraps
from logging import getLogger

from django.db.models import Model

from caluma.caluma_core.types import Node

log = getLogger(__name__)


def is_iterable_and_no_string(value):
    try:
        iter(value)
        return not isinstance(value, str)
    except TypeError:
        return False


def _field_name(db_field):
    if db_field.is_relation:
        return db_field.db_column or f"{db_field.name}_id"
    return db_field.db_column or db_field.name


def col_type_from_db(field, connection):
    """Return a (type, length) tuple for the given field."""

    sql_extract_type = """
        SELECT data_type, character_maximum_length
        FROM information_schema.columns
        WHERE
            column_name = %s AND
            table_name = %s
    """

    cursor = connection.cursor()
    cursor.execute(sql_extract_type, [_field_name(field), field.model._meta.db_table])
    res = cursor.fetchone()
    return res


def fix_foreign_key_types(apps, connection):
    """Ensure all foreign keys pointing to slug fields are correct type."""

    # I'm really not happy that this code needs to exist. I'ts a sign that
    # we somehow messed up and I couldn't reproduce exactly why this even
    # happened in the first place.  Figuring out why it happened would be
    # good, but since the broken version is out there anyway, we need the
    # fix no matter what.

    fix_sql = """
        ALTER TABLE %s
        ALTER COLUMN %s TYPE %s
    """

    for models in apps.all_models.values():
        for model in models.values():
            slug_fks = [
                field
                for field in model._meta.fields
                if field.is_relation and field.target_field.name == "slug"
            ]

            for field in slug_fks:
                # ok we have a slug foreign key
                fk_params = field.db_parameters(connection)
                target_params = field.target_field.db_parameters(connection)

                # verify django-internal specified type
                assert fk_params["type"] == target_params["type"], (
                    f"Foreign key field {field}: type mismatch with destination in django-internal representation"
                )

                # check if the DB agrees
                fk_dbtype = col_type_from_db(field, connection)
                target_dbtype = col_type_from_db(field.target_field, connection)
                if fk_dbtype != target_dbtype:  # pragma: no cover
                    # seems to be fixed upstream
                    cursor = connection.cursor()
                    type_, length = target_dbtype
                    new_type = f"{type_}({length})"
                    log.warning(f"Correcting data type of {field} to {new_type}")
                    # not using the parametrized syntax here (sql, params) as
                    # we do NOT want escaping here
                    cursor.execute(
                        fix_sql % (model._meta.db_table, _field_name(field), new_type)
                    )


def update_model(model: Model, data: dict) -> Model:
    for key, value in data.items():
        setattr(model, key, value)

    model.save()


def disable_raw(signal_handler):  # pragma: no cover
    """Disable signal handlers during loaddata."""

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw"):
            return
        signal_handler(*args, **kwargs)

    return wrapper


def suppressable_visibility_resolver():
    """Make a resolver that can be suppressed in the visibility layer.

    The visibility layer may cause additional load on the database, so
    in cases where it's not needed, the visibility classes can choose to
    skip filtering where it's not absolutely needed.

    For example, if the visibility of a child case is always dependent
    on the associated work item, you can disable enforcing visibility
    on that relationship.

    Example in the GraphQL schema:

    >>> class Form(FormDjangoObjectType):
    >>>     ...
    >>>     resolve_child_case = suppressable_visibility_resolver()

    Example in the visibility class:

    >>> class MyCustomVisibility(BaseVisibility):
    >>>     @filter_queryset_for(Case)
    >>>     def filter_queryset_for_case(self, node, queryset, info):
    >>>         # do the filtering as usual
    >>>         ...
    >>>     ...
    >>>     suppress_visibilities = [
    >>>         "WorkItem.child_case",
    >>>         ...
    >>>     ]

    With the above setting, when looking up child cases from work items,
    the visibility layer would not be run, and the child case would always
    be shown (if the workitem can be shown, of course).

    You may also define it as a `@property` on the visibility class. Note
    however that it's initialized on app startup, you can't change it during
    runtime and make suppression work in some cases and not in others.
    """

    # Avoid circular imports
    from caluma.caluma_core.visibilities import BaseVisibility

    # TODO: This is currently untested (as in unit test), because
    # the checks are done at startup (where the schema is initialized)
    # and we can't swap out the visibility class during test runs
    # to validate the behavour as we'd usually do.
    class SuppressableResolver:
        def __call__(self, inner_self, *args, **kwargs):
            return getattr(inner_self, self.prop, None)

        @property
        def _bypass_get_queryset(self):  # pragma: no cover
            """Tell Graphene to bypass get_queryset()."""
            # If any visibility class tells us to bypass the
            # queryset of this property, we return True
            return any(
                self.qualname in vis_class().suppress_visibilities
                for vis_class in Node.visibility_classes
            )

        def __repr__(self):  # pragma: no cover
            return f"SuppressableResolver({self.qualname})"

        def __set_name__(self, owner, name):
            # Magic. This is called by Python after setting the attribute on
            # the node class, and we use it to figure out which resolver we're
            # building.
            self.name = owner.__name__
            self.prop = name.replace("resolve_", "")
            self.qualname = f"{self.name}.{self.prop}"
            BaseVisibility._suppressable_visibilities.add(self.qualname)

    return SuppressableResolver()
