import csv
import logging
from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from io import StringIO
from typing import List, Optional

from api.app.schema import athlete_schema, country_schema, gender_schema, institution_schema, user_schema
from api.app.model.athlete_model import Athletes as AthleteModel
from api.app.model.country_model import Countries as CountryModel
from api.app.model.gender_model import Genders as GenderModel
from api.app.utils.global_def import StatusEnum, ResultEnum
from api.app.model.institution_model import Institutions as InstitutionModel
from api.app.model.profile_model import Profiles as ProfileModel
from api.app.utils.athlete_validations import (
    parse_birthdate,
    validate_required_athlete_fields,
    validate_country_id_required,
    validate_athlete_foreign_keys
)
from api.app.utils.db_functions import hard_delete_row
from api.app.utils.functions import check_if_id_exist, get_language_fields, parse_date


athlete_not_found_msg = "Athlete not found"


def create_athlete_complete(
    form_data: athlete_schema.AthleteCreateForm,
    institution_id: int,
    current_user: user_schema.User
) -> athlete_schema.AthleteResponse:
    """
    Complete athlete creation with all validations and data processing.

    NOTE: The first status of any athlete is ALWAYS set to 01-01-2025 00:00:00
    regardless of the status_date parameter provided.

    Args:
        form_data: Athlete creation form with personal and sports information
        institution_id: ID of the institution where athlete will be created
        current_user: Authenticated user performing the creation

    Returns:
        AthleteResponse: Created athlete ID and operation status

    Raises:
        HTTPException 400: Invalid data, missing required fields, or duplicate email
        HTTPException 404: Referenced foreign key entities not found
        HTTPException 500: Server error during creation process
    """
    logging.info(f"Creating athlete: {form_data.name} for user: {current_user.username}")

    birthdate_parsed = parse_birthdate(form_data.birthdate) if form_data.birthdate else None

    validate_required_athlete_fields(form_data.email, form_data.name, form_data.last_name)
    validate_country_id_required(form_data.country_id)
    validate_athlete_foreign_keys(
        country_id=form_data.country_id,
        gender_id=form_data.gender_id
    )

    athlete_data = athlete_schema.AthleteInput(
        email=form_data.email,
        name=form_data.name,
        last_name=form_data.last_name,
        birthdate=birthdate_parsed,
        country_id=form_data.country_id,
        document_number=form_data.document_number,
        gender_id=form_data.gender_id,
        contact_number=form_data.contact_number,
        institution_id=institution_id,
    )

    return create_athlete(athlete_data, current_user)


def create_athlete(
    athlete: athlete_schema.AthleteInput,
    user: user_schema.User
) -> athlete_schema.AthleteResponse:
    """
    Create a new athlete in the database or reactivate a previously deleted athlete.

    Args:
        athlete: Complete athlete data including personal and sports information
        user: User creating the athlete (for permissions and audit trail)

    Returns:
        AthleteResponse: Created or reactivated athlete ID with success status

    Raises:
        HTTPException 400: Email already registered for active athlete
        HTTPException 500: Database or file system errors during creation
    """
    logging.info(f"Checking existing profile for {athlete.name}")

    existing_profile = ProfileModel.select().where(ProfileModel.email == athlete.email).first()

    if existing_profile:
        logging.info(f"Profile for {athlete.email} exists.")

        existing_athlete = AthleteModel.select().where(
            AthleteModel.profile_id == existing_profile.id
        ).first()

        if existing_athlete:
            if existing_athlete.deleted_by_id is None:
                msg = f"Email {athlete.email} is already registered for the user {user.username}."
                logging.debug(msg)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
            else:
                logging.info(
                    f"Reactivating athlete {athlete.email} previously deleted by "
                    f"user: {existing_athlete.deleted_by_id}.")
                reactivate_athlete(existing_athlete, user.id)
                return athlete_schema.AthleteResponse(id=existing_athlete.id, status=ResultEnum.SUCCESS)

        else:
            logging.info(f"Creating new athlete record for {athlete.email} under user {user.username}.")
            return create_new_athlete(existing_profile.id, user, athlete, existing_profile=True)

    else:
        logging.info(f"Creating new profile for {athlete.email}.")
        try:
            profile_id = create_profile(athlete, user)
            return create_new_athlete(profile_id, user, athlete, existing_profile=False)
        except Exception as e:
            logging.error(f"Error creating profile: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while creating the athlete.")


def reactivate_athlete(athlete: AthleteModel, user_id: int) -> None:
    """
    Reactivate a previously soft-deleted athlete.

    Args:
        athlete: Athlete model instance to reactivate
        user_id: ID of user performing the reactivation

    Raises:
        HTTPException 500: Database error during reactivation
    """
    try:
        athlete.updated_by_id = user_id
        athlete.updated_at = datetime.now()
        athlete.deleted_by_id = None
        athlete.deleted_at = None
        athlete.status = StatusEnum.ACTIVE.value
        athlete.save()
        logging.info(f"Athlete {athlete.id} reactivated with status: {athlete.status}")
    except Exception as e:
        logging.error(f"Error reactivating athlete: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while reactivating the athlete.")


def create_profile(athlete: athlete_schema.AthleteInput, user: user_schema.User) -> int:
    """
    Create a new profile in the database and return its ID.

    Handles optional fields gracefully by only setting non-None values.

    Args:
        athlete: Athlete input data with optional fields
        user: User creating the profile

    Returns:
        int: Created profile ID
    """
    try:
        if athlete.country_id:
            check_if_id_exist(athlete.country_id, CountryModel)
        if athlete.gender_id:
            check_if_id_exist(athlete.gender_id, GenderModel)

        profile_data = {
            'email': athlete.email,
            'name': athlete.name,
            'last_name': athlete.last_name,
            'updated_at': datetime.now(),
            'created_at': datetime.now(),
            'updated_by': user.id,
            'created_by': user.id,
            'deleted_by': None
        }

        if athlete.document_number is not None:
            profile_data['document_number'] = athlete.document_number
        if athlete.contact_number is not None:
            profile_data['contact_number'] = athlete.contact_number
        if athlete.birthdate is not None:
            profile_data['birthdate'] = athlete.birthdate
        if athlete.gender_id is not None:
            profile_data['gender'] = athlete.gender_id
        if athlete.country_id is not None:
            profile_data['country'] = athlete.country_id

        profile = ProfileModel.create(**profile_data)
        logging.info(f"Profile for {athlete.email} created with ID {profile.id}.")
        return profile.id

    except Exception as e:
        logging.error(f"Error creating profile for {athlete.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


def create_new_athlete(
    profile_id: int, user: user_schema.User,
    athlete: athlete_schema.AthleteInput,
    existing_profile: bool
) -> athlete_schema.AthleteResponse:
    """Create a new athlete entry in the database with consistent status values."""
    try:
        institution_id = athlete.institution_id

        new_athlete = AthleteModel(
            institution_id=institution_id,
            profile_id=profile_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
            updated_by=user.id,
            created_by=user.id,
            deleted_by=None,
            active=True,
            status=StatusEnum.ACTIVE.value,
        )

        new_athlete.save()
        logging.info(f"Created athlete {new_athlete.id} with status: {new_athlete.status}")

    except Exception as e:
        logging.error(f"Error creating athlete: {e}")
        if not existing_profile:
            logging.error(f"Removing profile created for profile ID: {profile_id}.")
            hard_delete_row(profile_id, ProfileModel)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while creating the athlete.")

    return athlete_schema.AthleteResponse(id=new_athlete.id, status=ResultEnum.SUCCESS)


async def get_athletes(
    user: user_schema.User,
    institution_id: int = 0,
    name: str = ''
) -> List[athlete_schema.AthleteBasicData]:
    """
    Get all the user's athletes in the DB.

    Args:
        user (user_schema.User): User.
        institution_id (int): Institution ID.
        name (str): Athlete's name.

    Returns:
        list: List of athletes filtered by user.
    """
    logging.info(f"Getting athletes for user: {user.username}")

    query_athletes = (
        AthleteModel
        .select(
            AthleteModel.id.alias('athlete_id'),
            ProfileModel.name,
            ProfileModel.last_name,
            AthleteModel.institution_id,
            AthleteModel.updated_at,
            AthleteModel.updated_by,
            ProfileModel.email,
            AthleteModel.active,
            AthleteModel.status
        )
        .join(ProfileModel, on=(AthleteModel.profile_id == ProfileModel.id))
        .where(
            AthleteModel.deleted_by.is_null(True)
        )
        .order_by(AthleteModel.created_at.desc())
    )

    if institution_id:
        logging.info(f"Filtering athletes by institution_id: {institution_id}")
        query_athletes = query_athletes.where(AthleteModel.institution_id == institution_id)

    if name:
        query_athletes = query_athletes.where(
            (ProfileModel.name + " " + ProfileModel.last_name).contains(name)
        )

    athlete_list = []
    for raw_athlete in query_athletes.dicts():
        try:
            athlete_data = transform_raw_athlete_to_basic_data(raw_athlete)
            athlete_list.append(athlete_data)
        except ValueError as e:
            logging.error(f"Skipping athlete due to transformation error: {e}")
            continue

    logging.info(f"Successfully transformed {len(athlete_list)} athletes")
    return athlete_list


def fetch_athlete_data(
    athlete_email: Optional[str],
    athlete_id: Optional[int],
    user_id: int,
    language_fields: dict
) -> Optional[dict] | None:
    """
    Query athlete data from database with localized field names.

    Performs optimized query combining athlete, profile, and current status data
    with LEFT JOINs to handle optional relationships gracefully.

    Args:
        athlete_email: Email to search by (optional)
        athlete_id: ID to search by (optional)
        user_id: ID of requesting user for permission filtering
        language_fields: Dictionary with localized field mappings

    Returns:
        Optional[dict] or None: Athlete data with all related information or None if not found

    Raises:
        ValueError: Neither email nor ID provided
    """
    if not athlete_email and not athlete_id:
        raise ValueError("Either athlete_email or athlete_id must be provided.")

    query = (
        AthleteModel
        .select(
            AthleteModel.id.alias("athlete_id"),
            AthleteModel.updated_at,
            AthleteModel.updated_by,
            AthleteModel.active,
            AthleteModel.status,
            AthleteModel.institution_id,
            ProfileModel.name,
            ProfileModel.last_name,
            ProfileModel.birthdate,
            ProfileModel.document_number,
            ProfileModel.contact_number,
            ProfileModel.email,
            CountryModel.id.alias("country_id"),
            language_fields["country"].alias("country_name"),
            GenderModel.id.alias("gender_id"),
            language_fields["gender"].alias("gender_name")
        )
        .join(ProfileModel, on=(AthleteModel.profile_id == ProfileModel.id))
        .left_outer_join(CountryModel, on=(ProfileModel.country == CountryModel.id))
        .left_outer_join(GenderModel, on=(ProfileModel.gender == GenderModel.id))
        .where(
            AthleteModel.created_by == user_id,
            AthleteModel.deleted_by.is_null(True)
        )
    )

    if athlete_email:
        query = query.where(ProfileModel.email == athlete_email)
    if athlete_id:
        query = query.where(AthleteModel.id == athlete_id)

    athlete_data = query.dicts().first()

    if not athlete_data:
        return None

    return athlete_data


def get_athlete(
        athlete_email: Optional[str],
        athlete_id: Optional[int],
        user: user_schema.User,
        accept_language: str
):
    """
    Retrieves an athlete's data by email or ID for a given user.

    Updated with proper handling and better error management.

    Args:
        athlete_email (Optional[str]): Email of the athlete.
        athlete_id (Optional[int]): ID of the athlete.
        user (user_schema.User): Authenticated user object.
        accept_language (str): Language preference for localized fields.

    Returns:
        athlete_schema.Athlete | athlete_schema.AthleteId: Complete athlete data or minimal if institution not found.

    Raises:
        HTTPException: If the athlete is not found or an unexpected error occurs.
        ValueError: If both athlete_email and athlete_id are missing, or user is None.
    """
    if not athlete_email and not athlete_id:
        raise ValueError("Either athlete_email or athlete_id must be provided.")
    if not user:
        raise ValueError("User data is required.")

    language_fields = get_language_fields(accept_language)

    try:
        logging.info(f"Getting athlete with email {athlete_email} or ID {athlete_id} for user {user.username}")

        athlete = fetch_athlete_data(athlete_email, athlete_id, user.id, language_fields)

        if not athlete:
            raise_athlete_not_found(athlete_email, athlete_id)

        institution = InstitutionModel.get_or_none(InstitutionModel.id == athlete['institution_id'])
        if not institution:
            logging.warning(f"Institution {athlete['institution_id']} not found for athlete {athlete['athlete_id']}")
            return athlete_schema.AthleteId(id=athlete['athlete_id'])

        return build_athlete_response(athlete, institution)

    except HTTPException:
        raise
    except Exception as e:
        log_unexpected_error(athlete_email, athlete_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the athlete."
        )


def raise_athlete_not_found(email: Optional[str], athlete_id: Optional[int]):
    """
    Raises a 404 HTTPException when the athlete is not found.

    Args:
        email (Optional[str]): Email of the athlete.
        athlete_id (Optional[int]): ID of the athlete.

    Raises:
        HTTPException: With 404 status code and formatted message.
    """
    identifier = f"email {email}" if email else f"ID {athlete_id}"
    msg = f"Athlete with {identifier} not found"
    logging.warning(msg)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


def build_athlete_response(athlete, institution):
    """
    Builds a complete athlete response object with nested schemas.

    Enhanced with proper data transformation to handle legacy data
    and NULL values consistently.

    Args:
        athlete (dict): Raw athlete data from DB containing both profile and status data.
        institution (InstitutionModel): Institution object from DB.

    Returns:
        athlete_schema.Athlete: Formatted response object.
    """
    try:
        logging.info(f"Building Athlete response for ID: {athlete.get('athlete_id')}")

        def create_nested_field(schema_class, id_key, name_key):
            """Helper function to create nested schema objects only if ID exists"""
            id_value = athlete.get(id_key)
            name_value = athlete.get(name_key)
            if id_value is not None:
                nested_obj = schema_class(id=id_value, name=name_value or '')
                logging.debug(f"Created {schema_class.__name__}: {nested_obj}")
                return nested_obj
            return None

        country_obj = create_nested_field(
            country_schema.Country,
            'country_id',
            'country_name'
        )

        gender_obj = create_nested_field(
            gender_schema.Gender,
            'gender_id',
            'gender_name'
        )

        athlete_obj = athlete_schema.Athlete(
            id=athlete['athlete_id'],
            name=athlete['name'],
            last_name=athlete['last_name'],
            birthdate=athlete.get('birthdate'),
            updated_at=athlete['updated_at'],
            updated_by=safe_get_optional_int(athlete.get('updated_by')),
            active=bool(athlete.get('active', True)),
            status=athlete.get('status', StatusEnum.ACTIVE.value),
            country=country_obj,
            document_number=athlete.get('document_number'),
            gender=gender_obj,
            contact_number=athlete.get('contact_number'),
            email=athlete['email'],
            institution=institution_schema.InstitutionBase(
                id=athlete['institution_id'],
                name=institution.name
            )
        )

        logging.info("Successfully created Athlete object with proper transformations")
        return athlete_obj

    except Exception as e:
        logging.error(f"Error in build_athlete_response: {str(e)}")
        logging.error(f"Athlete data keys: {list(athlete.keys()) if isinstance(athlete, dict) else 'Not a dict'}")
        logging.error(f"Institution: {institution}")
        raise ValueError(f"Failed to build athlete response: {str(e)}")


def log_unexpected_error(email: Optional[str], athlete_id: Optional[int], error: Exception):
    """
    Logs unexpected errors during athlete retrieval.

    Args:
        email (Optional[str]): Email used in the lookup.
        athlete_id (Optional[int]): ID used in the lookup.
        error (Exception): Exception instance.
    """
    identifier = f"email {email}" if email else f"ID {athlete_id}"
    logging.error(f"Error retrieving athlete with {identifier}: {str(error)}")


def update_athlete_personal_data_complete(
    athlete_id: int,
    form_data: athlete_schema.AthletePersonalDataForm,
    institution_id: int,
    current_user: user_schema.User,
    accept_language: str
) -> athlete_schema.AthleteResponse:
    """
    Complete athlete personal data update with all validations and processing.

    Handles the full update workflow including data retrieval, validation,
    permission checks, and data transformation. Supports partial updates
    where only provided fields are modified.

    Args:
        athlete_id: ID of the athlete to update
        form_data: Form data with updated information (all fields optional)
        institution_id: Institution ID for permission validation
        current_user: User performing the update (for audit trail)
        accept_language: Language preference for error messages and responses

    Returns:
        AthleteResponse: Update operation result with athlete ID and status

    Raises:
        HTTPException 403: Athlete not accessible or institution permission denied
        HTTPException 404: Athlete not found or referenced entities not found
        HTTPException 500: Server error during update process
    """
    try:
        logging.info(f"Updating athlete {athlete_id} for user {current_user.username}")

        # Get existing athlete data for validation and permission check
        existing_athlete = get_athlete(
            athlete_email=None,
            athlete_id=athlete_id,
            user=current_user,
            accept_language=accept_language
        )

        logging.info(f"Retrieved existing_athlete of type: {type(existing_athlete)}")

        # Validate athlete type and institution access
        if isinstance(existing_athlete, athlete_schema.Athlete):
            logging.info("Got full Athlete object - proceeding with validation")

            if existing_athlete.institution:
                logging.info(f"Athlete institution ID: {existing_athlete.institution.id}")
                logging.info(f"Requested institution ID: {institution_id}")

                if existing_athlete.institution.id != institution_id:
                    logging.warning(
                        f"Institution mismatch: athlete belongs to {existing_athlete.institution.id}, "
                        f"requested {institution_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Athlete {athlete_id} does not belong to institution {institution_id}."
                    )

                logging.info("Institution validation passed - proceeding with update")
            else:
                logging.error(f"Athlete {athlete_id} has no institution data")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Athlete {athlete_id} has no institution associated."
                )

        elif isinstance(existing_athlete, athlete_schema.AthleteId):
            logging.warning(f"Got AthleteId only for athlete {athlete_id} - no access to full data")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Athlete {athlete_id} is not accessible with your current permissions."
            )

        else:
            logging.error(f"Unexpected athlete data type: {type(existing_athlete)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to process athlete data for ID {athlete_id}."
            )

        # Build updated athlete input data
        updated_data = build_updated_athlete_input(form_data, existing_athlete, institution_id)

        # Perform the update
        logging.info(f"Updating athlete {athlete_id}")
        updated_athlete = update_athlete_personal(
            athlete_id,
            updated_data,
            current_user
        )

        logging.info(f"Successfully updated athlete {athlete_id}")
        return updated_athlete

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logging.error(f"Unexpected error in update_athlete_personal_data_complete: {str(e)}")
        logging.error(f"athlete_id: {athlete_id}, user: {current_user.username}, institution_id: {institution_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating the athlete: {str(e)}"
        )


def update_athlete_personal(
    athlete_id: int,
    athlete: athlete_schema.AthleteInput,
    user: user_schema.User
) -> athlete_schema.AthleteResponse:
    """
    Update an existing athlete's profile in the database.

    Performs the actual database update operations including profile data
    modification. Validates foreign key references
    and handles partial updates gracefully.

    Args:
        athlete_id: ID of the athlete to update
        athlete: Complete athlete data with updated values
        user: User performing the update (for audit trail)

    Returns:
        AthleteResponse: Update result with athlete ID and success status

    Raises:
        HTTPException 404: Athlete or profile not found
        HTTPException 500: Database or file system errors during update
    """
    try:
        logging.info(f"Updating athlete: {athlete.name} for user: {user.username}")

        # Find athlete record
        athlete_record = AthleteModel.get_or_none(AthleteModel.id == athlete_id)
        if not athlete_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

        # Find associated profile
        db_profile = ProfileModel.get_or_none(ProfileModel.id == athlete_record.profile_id)
        if not db_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        # Validate foreign key references
        validate_athlete_foreign_keys(
            country_id=athlete.country_id,
            gender_id=athlete.gender_id
        )

        # Update profile fields if provided (partial update support)
        if athlete.email is not None:
            db_profile.email = athlete.email
        if athlete.name is not None:
            db_profile.name = athlete.name
        if athlete.last_name is not None:
            db_profile.last_name = athlete.last_name
        if athlete.document_number is not None:
            db_profile.document_number = athlete.document_number
        if athlete.birthdate is not None:
            db_profile.birthdate = athlete.birthdate
        if athlete.gender_id is not None:
            db_profile.gender = athlete.gender_id
        if athlete.contact_number is not None:
            db_profile.contact_number = athlete.contact_number
        if athlete.country_id is not None:
            db_profile.country = athlete.country_id

        # Update audit fields
        db_profile.updated_at = datetime.now()
        db_profile.updated_by = user.id
        db_profile.save()

        logging.info(f"Successfully updated profile for athlete {athlete_id}")
        return athlete_schema.AthleteResponse(id=athlete_id, status=ResultEnum.SUCCESS)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating athlete {athlete_id} for user {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the athlete."
        )


def soft_delete_athlete(athlete_id: int, user: user_schema.User) -> athlete_schema.AthleteResponse:
    """
    Soft delete an athlete by updating the deleted_by and deleted_at fields.

    Marks athlete as deleted without removing data from database. Only the athlete
    creator can delete their own athletes. Sets status to DELETED and updates
    audit fields for tracking purposes.

    Args:
        athlete_id: ID of the athlete to be deleted
        user: User who is performing the deletion (must be the creator)

    Returns:
        AthleteResponse: Response with deleted athlete ID and success status

    Raises:
        HTTPException 404: Athlete not found or not owned by current user
        HTTPException 500: Database error during deletion process
    """
    try:
        logging.info(f"Deleting athlete ID: {athlete_id} by user: {user.username}")

        # Find athlete owned by current user and not already deleted
        athlete = AthleteModel.get_or_none(
            AthleteModel.id == athlete_id,
            AthleteModel.created_by == user.id,
            AthleteModel.deleted_by.is_null(True)
        )

        if not athlete:
            msg = "Athlete not found or not associated with the current user."
            logging.debug(msg)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

        # Perform soft delete by updating audit fields with consistent status value
        athlete.deleted_by_id = user.id
        athlete.deleted_at = datetime.now()
        athlete.status = StatusEnum.DELETED.value
        athlete.save()

        logging.info(f"Athlete ID: {athlete_id} was successfully soft-deleted with status: {athlete.status}")

        return athlete_schema.AthleteResponse(
            id=athlete.id,
            status=ResultEnum.SUCCESS
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting athlete {athlete_id} for user {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the athlete."
        )


def build_updated_athlete_input(
    form_data: athlete_schema.AthletePersonalDataForm,
    existing_athlete: athlete_schema.Athlete,
    institution_id: int
) -> athlete_schema.AthleteInput:
    """
    Build athlete input data combining form updates with existing data.

    Creates a complete AthleteInput object by merging new form data with
    existing athlete information. Only non-null form fields override
    existing values, supporting partial updates.

    Args:
        form_data: Form data with updated fields (all optional)
        existing_athlete: Current athlete data from database
        institution_id: Institution ID for the update operation

    Returns:
        AthleteInput: Complete athlete data ready for database update

    Raises:
        HTTPException 500: Invalid athlete data type for update operation
    """
    if not isinstance(existing_athlete, athlete_schema.Athlete):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid athlete data type for update operation"
        )

    # Parse birthdate if provided
    birthdate_parsed = parse_birthdate(form_data.birthdate) if form_data.birthdate else None

    # Extract IDs from existing nested objects, handling None cases
    country_id = existing_athlete.country.id if existing_athlete.country else None
    gender_id = existing_athlete.gender.id if existing_athlete.gender else None
    institution_id_from_athlete = existing_athlete.institution.id if existing_athlete.institution else None

    # Build complete athlete input with form data taking precedence
    return athlete_schema.AthleteInput(
        email=form_data.email or existing_athlete.email,
        name=form_data.name or existing_athlete.name,
        last_name=form_data.last_name or existing_athlete.last_name,
        birthdate=birthdate_parsed or existing_athlete.birthdate,
        country_id=form_data.country_id or country_id,
        document_number=form_data.document_number or existing_athlete.document_number,
        gender_id=form_data.gender_id or gender_id,
        contact_number=form_data.contact_number or existing_athlete.contact_number,
        institution_id=institution_id or institution_id_from_athlete,
    )


def safe_get_optional_int(value) -> Optional[int]:
    """
    Safely convert database value to Optional[int].

    Handles NULL/None values from database foreign keys that allow NULL.

    Args:
        value: Database value (could be int, None, or string representation)

    Returns:
        Optional[int]: Integer value or None if input was NULL/None
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (ValueError, TypeError):
        logging.warning(f"Could not convert value to int: {value}")
        return None


def transform_raw_athlete_to_basic_data(raw_athlete: dict) -> athlete_schema.AthleteBasicData:
    """
    Transform raw database athlete data to AthleteBasicData schema.

    Handles all data transformations needed to convert database results
    into properly formatted schema objects, including:
    - Legacy status value normalization
    - Optional field handling
    - Type conversions

    Args:
        raw_athlete: Dictionary with raw athlete data from database query

    Returns:
        AthleteBasicData: Properly formatted athlete data

    Raises:
        ValueError: If required fields are missing from raw data
    """
    required_fields = ['athlete_id', 'name', 'last_name', 'email', 'institution_id', 'updated_at']
    missing_fields = [field for field in required_fields if field not in raw_athlete]
    if missing_fields:
        raise ValueError(f"Missing required fields in raw athlete data: {missing_fields}")

    try:
        return athlete_schema.AthleteBasicData(
            id=raw_athlete['athlete_id'],
            name=raw_athlete['name'],
            last_name=raw_athlete['last_name'],
            email=raw_athlete['email'],
            institution_id=raw_athlete['institution_id'],
            updated_at=raw_athlete['updated_at'],
            updated_by=safe_get_optional_int(raw_athlete.get('updated_by')),
            active=bool(raw_athlete.get('active', True)),
            status=raw_athlete.get('status', StatusEnum.ACTIVE.value)
        )
    except Exception as e:
        logging.error(f"Error transforming athlete data: {e}")
        logging.error(f"Raw athlete data: {raw_athlete}")
        raise ValueError(f"Failed to transform athlete data: {e}")


async def upload_dataset(file: UploadFile, current_user: user_schema.User):
    """
    Create athletes based on the contents of the file.

    Args:
        file (UploadFile): Uploaded file.
        current_user (user_schema.User): Current user.

    Returns:

    """
    content = await file.read()
    decoded_content = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded_content))

    inserted_profiles = 0
    inserted_athletes = 0

    for row in reader:
        try:
            institution_name = row.get("institution")
            institution = InstitutionModel.get_or_none(
                    (InstitutionModel.name == institution_name)
                    & (InstitutionModel.created_by == current_user.id)
                )
            if not institution:
                logging.warning(f"Institution '{institution_name}' not found for user {current_user.id}.")
                continue

            country_name = row.get("country").lower()
            country = None
            if country_name:
                country = CountryModel.get(name=country_name)

            gender_value = row.get("gender", "female").lower()
            gender = GenderModel.get(name=gender_value)

            inserted_profiles += 1
            inserted_athletes += 1

            athlete = athlete_schema.AthleteCreateForm(
                email=row.get("email"),
                name=row.get("name"),
                last_name=row.get("last_name"),
                birthdate=str(parse_date(row.get("birthdate"))),
                country_id=country.id,
                document_number=row.get("document_number"),
                gender_id=gender.id,
                contact_number=row.get("contact_number"),
            )
            create_athlete_complete(athlete, institution.id, current_user)

        except Exception as e:
            logging.warning(f"Error uploading athlete data: {e}")

    return {
        "message": "CSV processed successfully",
        "inserted_profiles": inserted_profiles,
        "inserted_athletes": inserted_athletes,
    }