import logging
from fastapi import APIRouter, Depends, status, Path, UploadFile, File, HTTPException, Request
from typing import Optional, Union

from api.app.schema import athlete_schema
from api.app.service import athlete_service
from api.app.schema.user_schema import User
from api.app.service.auth_service import get_current_user
from api.app.utils.decorators import paginate


athlete_id_msg = "The athlete's ID."
router = APIRouter(prefix="/athlete")


@router.post(
    "/",
    tags=["athlete"],
    status_code=status.HTTP_201_CREATED,
    response_model=athlete_schema.AthleteResponse,
    summary="Create a new athlete with profile and initial status",
    description="Creates a new athlete record including profile information and initial status data."
)
def create_athlete(
    institution_id: int,
    form_data: athlete_schema.AthleteCreateForm = Depends(athlete_schema.AthleteCreateForm.as_form),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new athlete record in the database.

    This endpoint:
    - Creates a new athlete profile with personal information
    - Creates an initial status record with date fixed to 01-01-2025 00:00:00
    - Validates all required fields and foreign key references
    - Handles athlete reactivation if previously soft-deleted

    IMPORTANT: The status_date parameter is ignored. The first status of any athlete
    is always set to 01-01-2025 00:00:00 for consistency.

    Args:
        form_data: Athlete personal and sports information
        institution_id: Institution ID
        current_user: Authenticated user

    Returns:
        AthleteResponse: Created athlete ID and operation status

    Raises:
        HTTPException 400: Invalid data or duplicate email
        HTTPException 404: Referenced entities not found
        HTTPException 500: Server error during creation
    """
    return athlete_service.create_athlete_complete(
        form_data=form_data,
        institution_id=institution_id,
        current_user=current_user,
    )


@router.get(
    "/",
    tags=["athlete"],
    status_code=status.HTTP_200_OK,
    response_model=athlete_schema.PaginatedAthletesResponse
)
@paginate(athlete_schema.PaginatedAthletesResponse)
async def get_all_athletes(
    institution_id: int, # Rewrite in the decorator
    name: Optional[str] = '',
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all athletes associated with the authenticated user.

    Args:
        current_user (User): The currently authenticated user.
        institution_id (Optional[int]): ID of the institution to filter athletes. Defaults to 0 (no filter).
        name (Optional[str]): Athlete's name.
        page (int): Page number for pagination.
        limit (int): Maximum number of athletes to retrieve per page.

    Returns:
        athlete_schema.PaginatedAthletesResponse: A paginated response containing the list of athletes.
    """
    logging.info(f"Getting athletes for user {current_user.username} with filters: institution_id={institution_id}")

    athletes = await athlete_service.get_athletes(
        current_user,
        institution_id=institution_id,
        name=name
    )

    if not athletes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No athletes found for the specified filters."
        )

    return athletes


@router.get(
    "/{athlete_id}",
    tags=["athlete"],
    status_code=status.HTTP_200_OK,
    response_model=Union[athlete_schema.AthleteId, athlete_schema.Athlete],
    summary="Get athlete by ID",
    description="Retrieve complete athlete information including profile, current status, and sports data"
)
def get_athlete_by_id(
    request: Request,
    athlete_id: int = Path(
        ...,
        description="Unique identifier of the athlete",
        example=1,
        gt=0
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve athlete information by ID.

    Returns complete athlete data including personal information, current status,
    and sports-related data. The response type depends on data availability:

    - AthleteId: When only basic athlete ID is accessible (limited permissions)
    - Athlete: Complete athlete information with all related data

    Args:
        request: HTTP request containing language preferences
        athlete_id: Unique identifier of the athlete to retrieve
        current_user: Authenticated user making the request

    Returns:
        Union[AthleteId, Athlete]: Either basic ID info or complete athlete data

    Raises:
        HTTPException 404: Athlete not found or not accessible to user
        HTTPException 500: Server error during data retrieval
    """
    return athlete_service.get_athlete(
        athlete_email=None,
        athlete_id=athlete_id,
        user=current_user,
        accept_language=request.state.accept_language
    )


@router.get(
    "/email/{athlete_email}",
    tags=["athlete"],
    status_code=status.HTTP_200_OK,
    response_model=Union[athlete_schema.AthleteId, athlete_schema.Athlete]
)
def get_athlete_by_email(
    request: Request,
    athlete_email: str = Path(..., description="The athlete's email address."),
    current_user: User = Depends(get_current_user)
):
    """Get athlete by email in the DB."""
    return athlete_service.get_athlete(
        athlete_email=athlete_email,
        athlete_id=None,
        user=current_user,
        accept_language=request.state.accept_language
    )


@router.patch(
    "/{athlete_id}",
    tags=["athlete"],
    status_code=status.HTTP_200_OK,
    response_model=athlete_schema.AthleteResponse,
    summary="Update athlete personal information",
    description="Update athlete profile data including personal details. All fields are optional for partial updates."
)
def update_athlete_personal_data(
    institution_id: int,
    request: Request,
    athlete_id: int = Path(
        ...,
        description="Unique identifier of the athlete to update",
        example=1,
        gt=0
    ),
    form_data: athlete_schema.AthletePersonalDataForm = Depends(
        athlete_schema.AthletePersonalDataForm.as_form_base
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Update athlete personal information.

    Allows partial updates of athlete profile data. Only provided fields will be updated,
    existing data is preserved for null/empty fields. Validates institution permissions
    and foreign key references.

    Args:
        request: HTTP request containing language preferences
        athlete_id: Unique identifier of the athlete to update
        form_data: Form data with fields to update (all optional)
        institution_id: Institution ID for permission validation (injected by decorator)
        current_user: Authenticated user performing the update

    Returns:
        AthleteResponse: Updated athlete ID and operation status

    Raises:
        HTTPException 403: Athlete not accessible or institution mismatch
        HTTPException 404: Athlete or referenced entities not found
        HTTPException 500: Server error during update
    """
    return athlete_service.update_athlete_personal_data_complete(
        athlete_id=athlete_id,
        form_data=form_data,
        institution_id=institution_id,
        current_user=current_user,
        accept_language=request.state.accept_language
    )


@router.delete(
    "/{athlete_id}",
    tags=["athlete"],
    status_code=status.HTTP_200_OK,
    response_model=athlete_schema.AthleteResponse,
    summary="Soft delete athlete by ID",
    description="Soft delete athlete record by marking it as deleted. The athlete data is preserved but becomes inaccessible."
)
def delete_athlete(
    athlete_id: int = Path(
        ...,
        description="Unique identifier of the athlete to delete",
        example=1,
        gt=0
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete athlete by ID.

    Marks the athlete as deleted without removing data from the database.
    Only the athlete creator can delete their own athletes. Deleted athletes
    can be reactivated during creation if the same email is used.

    Args:
        athlete_id: Unique identifier of the athlete to delete
        current_user: Authenticated user performing the deletion

    Returns:
        AthleteResponse: Deleted athlete ID and operation status

    Raises:
        HTTPException 404: Athlete not found or not owned by current user
        HTTPException 500: Server error during deletion
    """
    return athlete_service.soft_delete_athlete(athlete_id, current_user)


@router.post(
    "/upload_athletes",
    status_code=status.HTTP_201_CREATED,
    summary="Load athletes from CSV file",
    description="Load athletes from CSV file."
)
async def upload_athletes_csv(
        file: UploadFile,
        current_user: User = Depends(get_current_user)):
    """
    Upload a CSV with athlete data and load it into the database.
    The 'birthdate' field is transformed to ISO format.

    Args:
        file: CSV file with athlete data
        current_user: Authenticated user

    Returns:

    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported.")

    result = await athlete_service.upload_dataset(file, current_user)
    return result