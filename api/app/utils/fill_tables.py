import logging
from peewee import IntegrityError, ModelBase

from api.app.model.country_model import Countries
from api.app.model.gender_model import Genders
from api.app.model.professional_role_model import Professional_Roles


def fill_table(table: ModelBase, table_content):
    """
    Fills table {table} with table {table_content}.

    :param table: Class name
    :param table_content: content of the table
    """
    logging.info(f"fill_table(table: {table}, table_content)")

    try:
        # Check if the table contains at least one element
        if table.select().exists():
            logging.info(f"The table {table.__name__} already contains data. Skipping table filling.")
            return
    except Exception as e:
        logging.error(f"Error checking if table {table.__name__} contains data: {e}")

    # Get the list of fields (column names) for the table
    table_fields = set(table._meta.fields.keys())

    for content in table_content:
        try:
            # Filter content to include only valid table fields
            valid_data = {k: v for k, v in content.items() if k in table_fields}

            # Create new record (auto id)
            table.create(**valid_data)
            logging.info(f"Inserted {content} into {table.__name__} table.")
        except IntegrityError:
            logging.error(f"Error while inserting/updating {content} in {table.__name__} table.")
        except Exception as e:
            logging.error(f"Unexpected error while inserting {content} into {table.__name__}: {e}")


def fill_country_table():
    data = [
        {"name": "Germany", "spanish_name": "Alemania", "english_name": "Germany", "portuguese_name": "Alemanha"},
        {"name": "Argentina", "spanish_name": "Argentina", "english_name": "Argentina",
         "portuguese_name": "Argentina"},
        {"name": "Australia", "spanish_name": "Australia", "english_name": "Australia",
         "portuguese_name": "Austrália"},
        {"name": "Brazil", "spanish_name": "Brasil", "english_name": "Brazil", "portuguese_name": "Brasil"},
        {"name": "China", "spanish_name": "China", "english_name": "China", "portuguese_name": "China"},
        {"name": "Colombia", "spanish_name": "Colombia", "english_name": "Colombia",
         "portuguese_name": "Colômbia"},
        {"name": "Spain", "spanish_name": "España", "english_name": "Spain", "portuguese_name": "Espanha"},
        {"name": "United States", "spanish_name": "Estados Unidos", "english_name": "United States",
         "portuguese_name": "Estados Unidos"},
    ]

    fill_table(Countries, data)


def fill_gender_table():
    data = [
        {"name": "male", "spanish_name": "Masculino", "english_name": "Male", "portuguese_name": "Masculino"},
        {"name": "female", "spanish_name": "Femenino", "english_name": "Female", "portuguese_name": "Feminino"}
    ]
    fill_table(Genders, data)


def fill_professional_roles_table():
    data = [
        {"name": "physical trainer", "spanish_name": "Preparador Físico", "english_name": "Physical Trainer",
         "portuguese_name": "Treinador Físico"},
        {"name": "kinesiologist", "spanish_name": "Kinesiólogo", "english_name": "Kinesiologist",
         "portuguese_name": "Kinesiologista"},
        {"name": "administrative", "spanish_name": "Administrativo", "english_name": "Administrative",
         "portuguese_name": "Administrativo"},
        {"name": "doctor", "spanish_name": "Médico", "english_name": "Doctor", "portuguese_name": "Médico"},
        {"name": "manager", "spanish_name": "Gerente", "english_name": "Manager",
         "portuguese_name": "Gerente"},
        {"name": "researcher", "spanish_name": "Investigador", "english_name": "Researcher",
         "portuguese_name": "Pesquisador"},
        {"name": "sports doctor", "spanish_name": "Médico Deportivo", "english_name": "Sports Doctor",
         "portuguese_name": "Médico Esportivo"},
        {"name": "nutritionist", "spanish_name": "Nutricionista", "english_name": "Nutritionist",
         "portuguese_name": "Nutricionista"},
        {"name": "psychologist", "spanish_name": "Psicólogo", "english_name": "Psychologist",
         "portuguese_name": "Psicólogo"}
    ]

    fill_table(Professional_Roles, data)


def fill_all_tables():
    fill_country_table()
    fill_gender_table()
    fill_professional_roles_table()
