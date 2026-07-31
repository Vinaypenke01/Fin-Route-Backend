"""
common/models.py

Abstract base models inherited by every model in the project.
These ensure every table has standard audit fields and UUID identifiers.
"""

import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model that provides standard audit timestamp fields.
    Every model in the project must inherit from BaseModel or BasePublicModel.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last modified.",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class BasePublicModel(BaseModel):
    """
    Abstract base model that adds a UUID public identifier.
    Used for models whose primary key should not be exposed externally.
    The `public_id` is safe to use in API URLs and external references.
    """

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        help_text="External-facing UUID identifier, safe to expose in APIs.",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
