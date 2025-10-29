""" doc """

import logging

from api.app.model.athlete_model import Athletes
from api.app.model.country_model import Countries
from api.app.model.gender_model import Genders
from api.app.model.institution_model import Institutions
from api.app.model.professional_role_model import Professional_Roles
from api.app.model.profile_model import Profiles
from api.app.model.user_model import Users
from api.app.utils.db import db


def create_tables():
    """Create DB tables if they do not exist."""
    logging.info("Creating database tables...")
    with db:
        db.create_tables([
            Athletes,
            Countries,
            Genders,
            Institutions,
            Professional_Roles,
            Profiles,
            Users,
        ], safe=True)  # `safe=True` will not raise an exception if tables already exist
