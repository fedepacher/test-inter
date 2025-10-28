import peewee
from datetime import datetime

from api.app.model.base_model import BaseModel
from api.app.model.user_model import Users
from api.app.model.institution_model import Institutions
from api.app.model.profile_model import Profiles


class Athletes(BaseModel):
    """DB athlete columns definition.

    Args:
        BaseModel: Database connection reference.
    """
    id = peewee.AutoField(primary_key=True)
    institution_id = peewee.ForeignKeyField(Institutions, backref='athletes', null=False)
    profile_id = peewee.ForeignKeyField(Profiles, backref='athletes', null=False)
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    updated_at = peewee.DateTimeField(default=datetime.now, null=False)
    deleted_at = peewee.DateTimeField(null=True)
    updated_by = peewee.ForeignKeyField(Users, backref='updated_athletes', null=True, column_name='updated_by_id')
    created_by = peewee.ForeignKeyField(Users, backref='created_athletes', null=True, column_name='created_by_id')
    deleted_by = peewee.ForeignKeyField(Users, backref='deleted_athletes', null=True, column_name='deleted_by_id')
    active = peewee.BooleanField(default=True)
    status = peewee.CharField(max_length=20, null=True)

    class Meta:
        """ doc """
        table_name = "athletes"  # Explicitly set table name

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
