# Generated by Django 3.2.6 on 2022-01-07 18:08
import hashlib
from tqdm import tqdm

from django.db import migrations, connection


# noinspection DuplicatedCode
def split_identifier(identifier):
    """
    Split an SQL identifier into a two element tuple of (namespace, name).

    The identifier could be a table, column, or sequence name might be prefixed
    by a namespace.
    """
    try:
        namespace, name = identifier.split('"."')
    except ValueError:
        namespace, name = "", identifier
    return namespace.strip('"'), name.strip('"')


def names_digest(*args, length):
    """
    Generate a 32-bit digest of a set of arguments that can be used to shorten
    identifying names.
    """
    h = hashlib.md5()
    for arg in args:
        h.update(arg.encode())
    return h.hexdigest()[:length]


def _copied_django_internal_index_name_calculator(table_name, column_names, suffix=""):
    """
    COPIED FROM https://github.com/django/django/blob
    /ba9ced3e9a643a05bc521f0a2e6d02e3569de374/django/db/backends/base/schema.py#L989

    Generate a unique name for an index/unique constraint.
    The name is divided into 3 parts: the table name, the column names,
    and a unique digest and suffix.
    """
    _, table_name = split_identifier(table_name)
    hash_suffix_part = "%s%s" % (
        names_digest(table_name, *column_names, length=8),
        suffix,
    )
    max_length = connection.ops.max_name_length() or 200
    # If everything fits into max_length, use that name.
    index_name = "%s_%s_%s" % (table_name, "_".join(column_names), hash_suffix_part)
    if len(index_name) <= max_length:
        return index_name
    # Shorten a long suffix.
    if len(hash_suffix_part) > max_length / 3:
        hash_suffix_part = hash_suffix_part[: max_length // 3]
    other_length = (max_length - len(hash_suffix_part)) // 2 - 1
    index_name = "%s_%s_%s" % (
        table_name[:other_length],
        "_".join(column_names)[:other_length],
        hash_suffix_part,
    )
    # Prepend D if needed to prevent the name from starting with an
    # underscore or a number (not permitted on Oracle).
    if index_name[0] == "_" or index_name[0].isdigit():
        index_name = "D%s" % index_name[:-1]
    return index_name


def _copied_django_index_class_naming_func(table_name, column_names, suffix):
    """
    COPIED AND MODIFIED FROM
    https://github.com/django/django/blob/7119f40c9881666b6f9b5cf7df09ee1d21cc8344/django/db/models/indexes.py#L153

    Generate a unique name for the index.

    The name is divided into 3 parts - table name (12 chars), field name
    (8 chars) and unique hash + suffix (10 chars). Each part is made to
    fit its size by truncating the excess length.
    """
    fields_orders = [
        (field_name[1:], "DESC") if field_name.startswith("-") else (field_name, "")
        for field_name in column_names
    ]
    _, table_name = split_identifier(table_name)
    # The length of the parts of the name is based on the default max
    # length of 30 characters.
    column_names_with_order = [
        (("-%s" if order else "%s") % column_name)
        for column_name, (field_name, order) in zip(column_names, fields_orders)
    ]
    hash_data = [table_name] + column_names_with_order + [suffix]
    name = "%s_%s_%s" % (
        table_name[:11],
        column_names[0][:7],
        "%s_%s" % (names_digest(*hash_data, length=6), suffix),
    )
    assert len(name) <= 30, (
        "Index too long for multiple database support. Is self.suffix "
        "longer than 3 characters?"
    )
    if name[0] == "_" or name[0].isdigit():
        name = "D%s" % name[1:]
    return name


# noinspection PyPep8Naming
def forward(apps, schema_editor):
    Table = apps.get_model("database", "Table")

    for table in tqdm(
        Table.objects.all().order_by("id"), desc="Renaming old table indexes"
    ):
        field_names = ["order", "id"]
        table_name = f"database_table_{table.id}"
        index_from_old_migration = _copied_django_internal_index_name_calculator(
            table_name, field_names
        )
        new_index_made_by_django = _copied_django_index_class_naming_func(
            table_name, field_names, "idx"
        )
        new_index_name = f"tbl_order_id_{table.id}_idx"
        schema_editor.execute(
            f"ALTER INDEX IF EXISTS "
            f"{index_from_old_migration} RENAME TO {new_index_name}"
        )
        schema_editor.execute(
            f"ALTER INDEX IF EXISTS "
            f"{new_index_made_by_django} RENAME TO {new_index_name}"
        )


# noinspection PyPep8Naming
def reverse(apps, schema_editor):
    # We can't safely rollback the index renames above
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("database", "0064_add_aggregation_field_options"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
