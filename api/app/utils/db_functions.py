import logging
from api.app.utils.create_tables import create_tables
from api.app.utils.fill_tables import fill_all_tables


def hard_delete_row(id: int, table):
    """
    Permanently deletes a row from the specified database table.

    This function removes a row identified by its `id` from the given table.
    It logs the operation for auditing purposes.

    Args:
        id (int): The ID of the row to be deleted.
        table: The database table object (e.g., a Peewee model) where the row resides.

    Example:
        Suppose `User` is a Peewee model:
        ```
        hard_delete_row(123, User)
        ```
        This will delete the row with ID 123 from the `User` table.

    Note:
        Ensure the `table` parameter supports the `delete` and `where` methods,
        such as Peewee model classes.
    """
    logging.info(f"Deleting from table {table} ID {id} because of an exception")
    table.delete().where(table.id == id).execute()


def handler_db():
    """Create tables and fill them."""
    logging.info("Handling database tables")
    create_tables()
    fill_all_tables()
