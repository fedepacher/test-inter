import peewee
from datetime import datetime

from api.app.model.base_model import BaseModel
from api.app.model.gender_model import Genders
from api.app.model.country_model import Countries


class Profiles(BaseModel):
    """DB profile role columns definition.

    Args:
        BaseModel: Database connection reference.
    """
    id = peewee.AutoField()
    email = peewee.CharField(max_length=50, null=True)
    name = peewee.CharField(max_length=50, null=False)
    last_name = peewee.CharField(max_length=50, null=False)
    document_number = peewee.CharField(max_length=50, null=True)
    contact_number = peewee.CharField(max_length=15, null=True)
    birthdate = peewee.DateField(null=True)
    gender = peewee.ForeignKeyField(Genders, backref='profile', null=True)
    country = peewee.ForeignKeyField(Countries, backref='profile', null=True)
    updated_at = peewee.DateTimeField(default=datetime.now, null=False)
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    deleted_at = peewee.DateTimeField(null=True, default=None)
    # The following field are not foreign key because a circular imports
    updated_by = peewee.IntegerField(null=True, default=None)
    created_by = peewee.IntegerField(null=True, default=None)
    deleted_by = peewee.IntegerField(null=True, default=None)

    class Meta:
        """ doc """
        table_name = "profiles"  # Explicitly set table name

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
