import logging
from typing import List

from api.app.schema import professional_role_schema
from api.app.model.professional_role_model import Professional_Roles as ProfessionalRoleModel
from api.app.utils.functions import get_generic_list


async def get_professional_roles(accept_language: str) -> List[professional_role_schema.ProfessionalRolesBase]:
    """Get all the countries in the DB.

    Returns:
        list: List of countries.
    """
    logging.info("Getting all countries")
    return await get_generic_list(name='professional_role', model=ProfessionalRoleModel,
                                  schema=professional_role_schema.ProfessionalRolesBase,
                                  accept_language=accept_language)
