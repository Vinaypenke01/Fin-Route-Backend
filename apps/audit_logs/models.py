"""
audit_logs/models.py

Audit log model for capturing security and system administrative actions across the platform.
"""

from django.db import models
from apps.common.models import BaseModel


class ActionType(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    QUOTA_OVERRIDE = "quota_override", "Quota Override"
    STATUS_CHANGE = "status_change", "Status Change"
    EXPORT = "export", "Export"


class AuditLog(BaseModel):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ActionType.choices, db_index=True)
    target_model = models.CharField(max_length=100, db_index=True)
    target_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["target_model"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"AuditLog({self.action}, {self.target_model}, {self.created_at})"
