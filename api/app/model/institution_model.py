""" Model representing institutions or organizations. """

import peewee
from datetime import datetime

from api.app.model.base_model import BaseModel
from api.app.model.user_model import Users


class Institutions(BaseModel):
    """ Represents an institution or organization. """

    id = peewee.AutoField()
    name = peewee.CharField(max_length=100, null=False)
    category = peewee.CharField(max_length=50, default='ND', null=True)
    active = peewee.BooleanField(default=True, null=False)
    status = peewee.CharField(max_length=20, null=True)
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    updated_at = peewee.DateTimeField(default=datetime.now, null=False)
    deleted_at = peewee.DateTimeField(null=True)
    created_by = peewee.ForeignKeyField(Users, backref='created_institutions', null=True)
    updated_by = peewee.ForeignKeyField(Users, backref='updated_institutions', null=True)
    deleted_by = peewee.ForeignKeyField(Users, backref='deleted_institutions', null=True)

    class Meta:
        """ doc """
        table_name = "institutions"  # Explicitly set table name

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
