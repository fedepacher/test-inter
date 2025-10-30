"""
Utility for database record existence validation.

This module contains a function to verify the existence of a record in a database table.
If the record does not exist, an appropriate HTTP exception is raised.
"""
import logging
from datetime import datetime
from fastapi import HTTPException, status

from api.app.model.gender_model import Genders as GenderModel
from api.app.model.country_model import Countries as CountryModel
from api.app.model.professional_role_model import Professional_Roles as ProfessionalRolesModel


def check_if_id_exist(element_id, table_name):
    """
    Checks whether a specific ID exists in the given database table.

    This function queries the specified table to verify if a record with the
    provided ID exists. If not, it logs an error and raises an HTTP 404 exception.

    Args:
        element_id (int): The ID of the record to check.
        table_name: The database table object (e.g., a Peewee model) where the check is performed.

    Raises:
        HTTPException: If the record does not exist, raises a 404 Not Found error with a descriptive message.

    Example:
        Suppose `User` is a Peewee model:
        ```
        check_if_id_exist(123, User)
        ```
        This will verify if a record with ID 123 exists in the `User` table.

    Note:
        The `table_name` parameter must support the `select`, `where`, and `exists` methods,
        such as Peewee model classes.
    """
    if not table_name.select().where(table_name.id == element_id).exists():
        msg = f"{table_name.__name__} ID {element_id} does not exist"
        logging.error(msg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )


def get_language_fields(accept_language: str):
    """Map language to corresponding field names."""
    logging.info(f"get_language_fields(accept_language: {accept_language})")
    models = {
        "country": CountryModel,
        "gender": GenderModel,
        "professional_role": ProfessionalRolesModel
    }

    # Language suffix map
    suffixes = {
        "en": "english_name",
        "es": "spanish_name",
        "pt": "portuguese_name",
    }

    # Build the dictionary dynamically
    language_fields = {
        lang: {
            key: getattr(model, attr)
            for key, model in models.items()
        }
        for lang, attr in suffixes.items()
    }
    language = language_fields.get(accept_language, language_fields["es"])
    logging.info(f"Language selected {language}")
    return language


async def get_generic_list(name: str, model, schema, accept_language):
    logging.info(f"get_generic_list(name: {name}, "
                 f"model: {model}, "
                 f"schema: {schema}, "
                 f"accept_language: {accept_language})")
    language_fields = get_language_fields(accept_language)

    try:
        alias = f'{name}_name'
        query = model.select(model.id, language_fields[name].alias(alias)).order_by(language_fields[name].asc())
        results = list(query)  # Execute the query and fetch results
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {name} found."
            )

        elements_list = []
        for record in results:
            element = schema(
                id=record.id,
                name=getattr(record, alias)
            )
            elements_list.append(element)

        return elements_list
    except HTTPException as e:
        logging.error(f"HTTPException occurred while fetching {name}: {str(e)}")
        raise e  # Re-raise the HTTPException if triggered
    except Exception as e:
        logging.error(f"Error occurred while fetching {name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


def parse_date(date_str: str):
    """
    Try to parse various date formats into a normalized ISO date (YYYY-MM-DD).

    Args::
        date_str (str): The date to parse.

    Returns:
        datetime: The normalized ISO date (YYYY-MM-DD).
    """
    if not date_str:
        return None

    date_formats = [
        "%Y-%m-%d",     # 1992-12-11
        "%d/%m/%Y",     # 11/12/1992
        "%m-%d-%Y",     # 12-11-1992
        "%B %d, %Y",    # December 11, 1992
        "%B %d %Y",     # December 11 1992
        "%b %d, %Y",    # Dec 11, 1992
        "%b %d %Y",     # Dec 11 1992
        "%d-%m-%Y",     # 11-12-1992
        "%Y/%m/%d",     # 1992/12/11
        "%d.%m.%Y",     # 11.12.1992
        "%Y.%m.%d",     # 1992.12.11
        "%d %B %Y",     # 11 December 1992
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{date_str}'")
