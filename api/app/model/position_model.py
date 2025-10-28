import peewee
from datetime import datetime

from api.app.model.base_model import BaseModel
from api.app.model.sport_model import Sports


class Positions(BaseModel):
    """DB position columns definition.

    Args:
        BaseModel: Database connection reference.
    """
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=10, null=False)
    spanish_name = peewee.TextField(null=True)
    english_name = peewee.TextField(null=True)
    portuguese_name = peewee.TextField(null=True)
    description = peewee.CharField(max_length=30, null=True)
    sport_id = peewee.ForeignKeyField(Sports, backref='position', null=False)
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    updated_at = peewee.DateTimeField(default=datetime.now, null=False)

    class Meta:
        """ doc """
        table_name = "positions"  # Explicitly set table name

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
