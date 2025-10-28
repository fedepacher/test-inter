import peewee
from datetime import datetime

from api.app.model.base_model import BaseModel


class Sports(BaseModel):
    """DB sport columns definition.

    Args:
        BaseModel: Database connection reference.
    """
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField(max_length=50, unique=True, null=False)
    spanish_name = peewee.TextField(null=True)
    english_name = peewee.TextField(null=True)
    portuguese_name = peewee.TextField(null=True)
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    updated_at = peewee.DateTimeField(default=datetime.now, null=False)

    class Meta:
        """ doc """
        table_name = "sports"  # Explicitly set table name

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
