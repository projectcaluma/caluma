from functools import wraps
from logging import getLogger

from django.db.models import Model

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
                assert (
                    fk_params["type"] == target_params["type"]
                ), f"Foreign key field {field}: type mismatch with destination in django-internal representation"

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
