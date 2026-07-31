"""
audit_logs/serializers.py
"""

from rest_framework import serializers
from apps.audit_logs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_mobile = serializers.CharField(source="user.mobile_number", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_name",
            "user_mobile",
            "action",
            "target_model",
            "target_id",
            "description",
            "ip_address",
            "user_agent",
            "changes",
            "created_at",
        ]
