import logging
from fastapi import APIRouter, status, Request
from typing import List

from api.app.schema import professional_role_schema
from api.app.service import professional_role_service


router = APIRouter(prefix="/professional-roles")


@router.get(
    "/",
    tags=["professional roles"],
    status_code=status.HTTP_200_OK,
    response_model=List[professional_role_schema.ProfessionalRolesBase]
)
async def get_professional_role_list(request: Request) -> list:
    """
    Get all DB professional roles.

    Returns:
    - **list**: A list containing all the professional roles.
    """
    logging.info("Getting professional roles")
    accept_language = request.state.accept_language
    professional_role = await professional_role_service.get_professional_roles(accept_language)
    return professional_role
