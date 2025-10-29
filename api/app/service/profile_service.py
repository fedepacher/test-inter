""" doc """

import logging
from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse

from api.app.model.country_model import Countries as CountryModel
from api.app.model.gender_model import Genders as GenderModel
from api.app.model.institution_model import Institutions as InstitutionModel
from api.app.model.professional_role_model import Professional_Roles as ProfessionalRolesModel
from api.app.model.profile_model import Profiles as ProfileModel
from api.app.model.user_model import Users as UserModel
from api.app.schema import (country_schema, gender_schema, institution_schema, professional_role_schema, profile_schema,
                            user_schema)
from api.app.utils.functions import check_if_id_exist, get_language_fields


def get_profile_info(user: user_schema.User, accept_language: str) -> profile_schema.ProfileResponse | None:
    """Get user information in the DB.

        Args:
            user (user_schema.User): User.
            accept_language (str): Language.

        Returns:
            JSON: Profile information, User information and Institution information of the user.
        """
    logging.info(f"Loading profile information for user: {user.username}")
    try:
        language_fields = get_language_fields(accept_language)
        user_data = (
            UserModel
            .select(
                UserModel.username,
                UserModel.email.alias('email'),
                UserModel.created_at,
                UserModel.updated_at,
                UserModel.active,
                UserModel.status,
                ProfessionalRolesModel.id.alias('professional_role_id'),
                language_fields['professional_role'].alias('professional_role_name'),
                ProfileModel.email.alias('contact_email'),
                ProfileModel.name,
                ProfileModel.last_name,
                ProfileModel.document_number,
                ProfileModel.contact_number,
                ProfileModel.birthdate,
                GenderModel.id.alias('gender_id'),
                language_fields["gender"].alias('gender_name'),
                CountryModel.id.alias('country_id'),
                language_fields["country"].alias('country_name'),
                ProfileModel.created_at.alias('profile_created_at'),
                ProfileModel.updated_at.alias('profile_updated_at')
            )
            .join(ProfileModel, on=(UserModel.profile == ProfileModel.id))
            .left_outer_join(ProfessionalRolesModel, on=(UserModel.prof_role == ProfessionalRolesModel.id))
            .left_outer_join(GenderModel, on=(ProfileModel.gender == GenderModel.id))
            .left_outer_join(CountryModel, on=(ProfileModel.country == CountryModel.id))
            .where(UserModel.id == user.id)
            .dicts()
            .get()
        )

        if not user_data:
            logging.info(f"Profile for {user.email} does not exist.")
            return None

        logging.info(f"Profile for {user.email} exists.")

        institution = (
            InstitutionModel
            .select(
                InstitutionModel.id.alias('institution_id'),
                InstitutionModel.name.alias('institution_name'),
                InstitutionModel.category.alias('institution_category'),
                InstitutionModel.active.alias('institution_active'),
                InstitutionModel.status.alias('institution_status'),
                InstitutionModel.created_at.alias('created_at'),
                InstitutionModel.updated_at.alias('updated_at'),
                InstitutionModel.deleted_at.alias('deleted_at'),
                InstitutionModel.created_by.alias('created_by'),
                InstitutionModel.updated_by.alias('updated_by'),
                InstitutionModel.deleted_by.alias('deleted_by'),
            )
            .where(
                (InstitutionModel.active == True) &
                (InstitutionModel.deleted_by.is_null(True))
            )
            .dicts()
            .get()
        )

        new_institution = institution_schema.Institution(
            id=institution['institution_id'],
            name=institution['institution_name'],
            category=institution['institution_category'],
            active=institution['institution_active'],
            status=institution['institution_status'],
            created_at=institution['created_at'],
            updated_at=institution['updated_at'],
            deleted_at=institution['deleted_at'],
            created_by=institution['created_by'],
            updated_by=institution['updated_by'],
            deleted_by=institution['deleted_by'],
        )

        gender_obj = None
        if user_data['gender_id'] is not None:
            gender_obj = gender_schema.Gender(
                id=user_data['gender_id'],
                name=user_data['gender_name']
            )

        country_obj = None
        if user_data['country_id'] is not None:
            country_obj = country_schema.Country(
                id=user_data['country_id'],
                name=user_data['country_name']
            )

        professional_role_obj = None
        if user_data['professional_role_id'] is not None:
            professional_role_obj = professional_role_schema.ProfessionalRolesBase(
                id=user_data['professional_role_id'],
                name=user_data['professional_role_name']
            )

        new_profile = profile_schema.ProfileResponse(
            profile=profile_schema.Profile(
                contact_email=user_data['contact_email'],
                name=user_data['name'],
                last_name=user_data['last_name'],
                document_number=user_data['document_number'],
                contact_number=user_data['contact_number'],
                birthdate=user_data['birthdate'],
                gender=gender_obj,
                country=country_obj,
                created_at=user_data['profile_created_at'],
                updated_at=user_data['profile_updated_at'],
                professional_role=professional_role_obj
            ),
            user=user_schema.UserProfile(
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data['created_at'],
                updated_at=user_data['updated_at'],
                active=user_data['active'],
                status=user_data['status']
            ),
            institutions=new_institution
        )
        return new_profile

    except HTTPException as e:
        logging.error(f"HTTPException occurred: {e.detail}")
        raise e

    except Exception as e:
        logging.error(f"An error occurred while loading profile information: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing the request"
        )


async def update_profile(profile: profile_schema.ProfileIn,
                         user: user_schema.User,
                         accept_language: str,
                         image: UploadFile) -> JSONResponse:
    """Update an existing profile in the database.

    Args:
        profile (profile_schema.ProfileIn): Profile data to update in the DB.
        user (user_schema.User): Current user.
        accept_language (str): Language preference.
        image (UploadFile): Profile image file.

    Returns:
        JSONResponse: Success message with status.
    """
    if image is not None:
        if image.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail="File must be a valid image format")
    else:
        logging.info(f"No image file provided for username {user.username}")

    logging.info(f"Getting current user information for user: {user.username}")
    existing_profile = get_profile_info(user, accept_language)

    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    professional_role_id = None
    professional_role_name = "No role assigned"
    if existing_profile.profile.professional_role:
        professional_role_id = existing_profile.profile.professional_role.id
        professional_role_name = existing_profile.profile.professional_role.name

    logging.info(f"Current professional role: {professional_role_name} (ID: {professional_role_id})")

    logging.info(f"Updating profile for user: {user.username}")

    existing_user = UserModel.get_or_none(UserModel.id == user.id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_profile = ProfileModel.get_or_none(ProfileModel.id == existing_user.profile)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    db_profile.email = profile.email if profile.email is not None else db_profile.email
    db_profile.name = profile.name if profile.name is not None else db_profile.name
    db_profile.last_name = profile.last_name if profile.last_name is not None else db_profile.last_name

    db_profile.document_number = (profile.document_number
                                  if profile.document_number is not None
                                  else db_profile.document_number)

    db_profile.birthdate = (profile.birthdate
                            if profile.birthdate is not None
                            else db_profile.birthdate)

    if profile.gender_id is not None:
        check_if_id_exist(profile.gender_id, GenderModel)
        db_profile.gender = profile.gender_id

    db_profile.contact_number = (profile.contact_number
                                 if profile.contact_number is not None
                                 else db_profile.contact_number)

    if profile.country_id is not None:
        check_if_id_exist(profile.country_id, CountryModel)
        db_profile.country = profile.country_id

    db_profile.updated_at = datetime.now()
    db_profile.updated_by = user.id

    logging.info(f"Updating profile for user: {user.username}")
    try:
        db_profile.save()
        logging.info(f"Successfully updated profile for user: {user.username}")
    except Exception as e:
        logging.error(f"Error updating ProfileModel table: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the profile."
        )

    logging.info("Updating user professional role")
    if profile.professional_role_id is not None:
        logging.info(f"Updating professional role for user: {user.username}")
        check_if_id_exist(profile.professional_role_id, ProfessionalRolesModel)
        existing_user.prof_role = profile.professional_role_id
        existing_user.updated_at = datetime.now()

        try:
            existing_user.save()
            logging.info(f"Successfully updated professional role for user: {user.username}")
        except Exception as e:
            logging.error(f"Error updating UserModel table: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating the user professional role."
            )

    return JSONResponse(
        content={"msg": "Profile updated successfully"},
        status_code=status.HTTP_200_OK
    )
