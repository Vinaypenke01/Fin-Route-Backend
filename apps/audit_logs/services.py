"""
audit_logs/services.py

AuditLogService for recording user activities (logins, creates, updates, deletes, exports).
"""

import logging
from apps.audit_logs.models import AuditLog, ActionType

logger = logging.getLogger(__name__)


class AuditLogService:
    @staticmethod
    def log_action(
        user,
        action: str,
        target_model: str,
        description: str,
        target_id: str = "",
        ip_address: str = None,
        user_agent: str = None,
        changes: dict = None,
    ) -> AuditLog:
        """
        Record a user activity audit log entry.
        """
        try:
            log = AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action=action,
                target_model=target_model,
                target_id=str(target_id) if target_id else "",
                description=description,
                ip_address=ip_address,
                user_agent=user_agent or "",
                changes=changes or {},
            )
            return log
        except Exception as e:
            logger.error("Failed to write audit log: %s", e)
            return None
