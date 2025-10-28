import logging
from peewee import IntegrityError, DoesNotExist, ModelBase

from api.app.model.sport_model import Sports
from api.app.model.position_model import Positions
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





def fill_sport_table():
    data = [
        {"name": "soccer", "spanish_name": "Fútbol", "english_name": "Soccer", "portuguese_name": "Futebol"},
        {"name": "basketball", "spanish_name": "Basketball", "english_name": "Basketball",
         "portuguese_name": "Basquetebol"},
        {"name": "tennis", "spanish_name": "Tenis", "english_name": "Tennis", "portuguese_name": "Tênis"},
        {"name": "handball", "spanish_name": "Handball", "english_name": "Handball", "portuguese_name": "Handebol"},
        {"name": "athletics", "spanish_name": "Atletismo", "english_name": "Athletics", "portuguese_name": "Atletismo"},
        {"name": "softball", "spanish_name": "Sóftbol", "english_name": "Softball", "portuguese_name": "Softbol"},
        {"name": "baseball", "spanish_name": "Béisbol", "english_name": "Baseball", "portuguese_name": "Beisebol"},
        {"name": "hockey", "spanish_name": "Hockey", "english_name": "Hockey", "portuguese_name": "Hóquei"},
        {"name": "rugby", "spanish_name": "Rugby", "english_name": "Rugby", "portuguese_name": "Rugby"},
        {"name": "taekwondo", "spanish_name": "Taekwondo", "english_name": "Taekwondo", "portuguese_name": "Taekwondo"},
        {"name": "BMX", "spanish_name": "BMX", "english_name": "BMX", "portuguese_name": "BMX"},
        {"name": "judo", "spanish_name": "Judo", "english_name": "Judo", "portuguese_name": "Judô"},
        {"name": "squash", "spanish_name": "Squash", "english_name": "Squash", "portuguese_name": "Squash"},
        {"name": "paddle", "spanish_name": "Pádel", "english_name": "Paddle", "portuguese_name": "Paddle"},
        {"name": "artistic gymnastics", "spanish_name": "Gimnasia Artística", "english_name": "Artistic Gymnastics",
         "portuguese_name": "Ginástica Artística"},
        {"name": "fencing", "spanish_name": "Esgrima", "english_name": "Fencing", "portuguese_name": "Esgrima"},
        {"name": "Olympic weightlifting", "spanish_name": "Halterofilia Olímpica",
         "english_name": "Olympic Weightlifting", "portuguese_name": "Halterofilismo Olímpico"},
        {"name": "swimming", "spanish_name": "Natación", "english_name": "Swimming", "portuguese_name": "Natação"}

    ]

    fill_table(Sports, data)


def fill_position_table():
    sports_positions = {
        'soccer': [
            (1, 'gk', 'goalkeeper', 'Arquero', 'Goalkeeper', 'Goleiro'),
            (2, 'cb', 'central defender', 'Defensa Central', 'Central Defender', 'Zagueiro Central'),
            (3, 'fb', 'fullback', 'Lateral', 'Fullback', 'Lateral'),
            (4, 'cdm', 'defensive midfielder', 'Mediocentro Defensivo', 'Defensive Midfielder', 'Volante Defensivo'),
            (5, 'cam', 'offensive midfielder', 'Mediocentro Ofensivo', 'Offensive Midfielder', 'Meia Ofensivo'),
            (6, 'wing', 'winger', 'Extremo', 'Winger', 'Extremo'),
            (7, 'cf', 'center forward', 'Delantero Centro', 'Center Forward', 'Centroavante')
        ],
        'basketball': [
            (8, 'pg', 'point guard', 'Base', 'Point Guard', 'Armador'),
            (9, 'sg', 'shooting guard', 'Escolta', 'Shooting Guard', 'Ala-armador'),
            (10, 'sf', 'small forward', 'Alero', 'Small Forward', 'Ala'),
            (11, 'c', 'center', 'Pivot', 'Center', 'Pivô'),
            (12, 'pf', 'power forward', 'Ala-Pívot', 'Power Forward', 'Ala-pivô')
        ],
        'tennis': [
            (13, 'tennis', '', 'Tenis', 'Tennis', 'Tênis')
        ],
        'handball': [
            (14, 'pivot', '', 'Pivote', 'Pivot', 'Pivô'),
            (15, 'wing', '', 'Extremo', 'Winger', 'Extremo'),
            (16, 'center', '', 'Central', 'Center', 'Central'),
            (17, 'extreme', '', 'Extremo', 'Extreme', 'Extremo'),
            (18, 'goalkeeper', '', 'Portero', 'Goalkeeper', 'Goleiro')
        ],
        'athletics': [
            (19, 'jumps', '', 'Saltos', 'Jumps', 'Saltos'),
            (20, 'throwing', '', 'Lanzamiento', 'Throwing', 'Arremesso'),
            (21, 'running', '', 'Carreras', 'Running', 'Corrida')
        ],
        'softball': [
            (22, 'infielder', '', 'Infielder', 'Infielder', 'Infielder'),
            (23, 'pitcher', '', 'Lanzador', 'Pitcher', 'Arremessador'),
            (24, 'catcher', '', 'Catcher', 'Catcher', 'Catcher'),
            (25, 'utility', '', 'Utility', 'Utility', 'Utility'),
            (26, 'outfielder', '', 'Outfielder', 'Outfielder', 'Outfielder')
        ],
        'baseball': [
            (27, 'infielder', '', 'Infielder', 'Infielder', 'Infielder'),
            (28, 'pitcher', '', 'Lanzador', 'Pitcher', 'Arremessador'),
            (29, 'catcher', '', 'Catcher', 'Catcher', 'Catcher'),
            (30, 'utility', '', 'Utility', 'Utility', 'Utility'),
            (31, 'outfielder', '', 'Outfielder', 'Outfielder', 'Outfielder')
        ],
        'hockey': [
            (32, 'gk', 'goalkeeper', 'Arquero', 'Goalkeeper', 'Goleiro'),
            (33, 'cb', 'central defender', 'Defensa Central', 'Central Defender', 'Zagueiro Central'),
            (34, 'fb', 'fullback', 'Lateral', 'Fullback', 'Lateral'),
            (35, 'cdm', 'defensive midfielder', 'Mediocentro Defensivo', 'Defensive Midfielder', 'Volante Defensivo'),
            (36, 'cam', 'offensive midfielder', 'Mediocentro Ofensivo', 'Offensive Midfielder', 'Meia Ofensivo'),
            (37, 'wing', 'winger', 'Extremo', 'Winger', 'Extremo'),
            (38, 'cf', 'center forward', 'Delantero Centro', 'Center Forward', 'Centroavante')
        ],
        'rugby': [
            (39, '1st row', '', 'Primera Línea', '1st Row', 'Primeira Linha'),
            (40, '2nd row', '', 'Segunda Línea', '2nd Row', 'Segunda Linha'),
            (41, '3rd row', '', 'Tercera Línea', '3rd Row', 'Terceira Linha'),
            (42, 'scrum-half', '', 'Medio de Melé', 'Scrum-Half', 'Scrum-Half'),
            (43, 'fly-half', '', 'Apertura', 'Fly-Half', 'Fly-Half'),
            (44, 'center', '', 'Centro', 'Center', 'Centro'),
            (45, 'wing', '', 'Ala', 'Wing', 'Ala'),
            (46, 'fullback', '', 'Zaguero', 'Fullback', 'Fullback')
        ],
        'taekwondo': [
            (47, 'taekwondo', '', 'Taekwondo', 'Taekwondo', 'Taekwondo')
        ],
        'bmx': [
            (48, 'bmx', '', 'BMX', 'BMX', 'BMX')
        ],
        'judo': [
            (49, 'judo', '', 'Judo', 'Judo', 'Judô')
        ],
        'squash': [
            (50, 'squash', '', 'Squash', 'Squash', 'Squash')
        ],
        'paddle': [
            (51, 'forehand', '', 'Drive', 'Forehand', 'Forehand'),
            (52, 'backhand', '', 'Reves', 'Backhand', 'Backhand')
        ],
        'artistic gymnastics': [
            (53, 'floor', '', 'Suelo', 'Floor', 'Solo'),
            (54, 'rings', '', 'Anillas', 'Rings', 'Argolas'),
            (55, 'vault', '', 'Salto', 'Vault', 'Salto'),
            (56, 'high bar', '', 'Barra Fija', 'High Bar', 'Barra Fixa'),
            (57, 'parallel bars', '', 'Barras Paralelas', 'Parallel Bars', 'Barras Paralelas'),
            (58, 'uneven bars', '', 'Barras Asimétricas', 'Uneven Bars', 'Barras Assimétricas'),
            (59, 'beam', '', 'Viga', 'Beam', 'Trave')
        ],
        'fencing': [
            (60, 'fencing', '', 'Esgrima', 'Fencing', 'Esgrima')
        ],
        'Olympic weightlifting': [
            (61, 'Olympic weightlifting', '', 'Halterofilia Olímpica', 'Olympic Weightlifting',
             'Halterofilismo Olímpico')
        ],
        'swimming': [
            (62, 'swimming', '', 'Natación', 'Swimming', 'Natação')
        ]
    }

    try:
        # Check if the table contains at least one element
        if Positions.select().exists():
            logging.info(f"The table {Positions.__name__} already contains data. Skipping table filling.")
            return
    except Exception as e:
        logging.error(f"Error checking if table {Positions.__name__} contains data: {e}")

    logging.info("Filling position table.")
    for sport_name, positions in sports_positions.items():
        # Ensure the sport exists or create it if it doesn't
        sport, created = Sports.get_or_create(name=sport_name)
        if created:
            logging.info(f"Created new sport: {sport_name}")
        else:
            logging.info(f"Sport {sport_name} already exists.")

        for id, position_name, description, spanish_name, english_name, portuguese_name in positions:
            try:
                # Check if the position exists by ID
                position = Positions.get_or_none(Positions.id == id)

                if position:
                    # Update existing position
                    position.name = position_name
                    position.description = description
                    position.sport_id = sport
                    position.spanish_name = spanish_name
                    position.english_name = english_name
                    position.portuguese_name = portuguese_name
                    position.save()
                    logging.info(f"Updated position ID {id}: {position_name}.")
                else:
                    # Insert new position
                    Positions.create(
                        id=id,
                        name=position_name,
                        description=description,
                        sport_id=sport,
                        spanish_name=spanish_name,
                        english_name=english_name,
                        portuguese_name=portuguese_name
                    )
                    logging.info(f"Inserted new position ID {id}: {position_name}.")
            except Exception as e:
                logging.error(f"Failed to insert/update position ID {id}: {e}")


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
    fill_sport_table()
    fill_position_table()
    fill_country_table()
    fill_gender_table()
    fill_professional_roles_table()
