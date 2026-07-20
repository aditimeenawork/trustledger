from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.roles import (
    COMPLIANCE_OFFICER,
    DEVELOPER,
    READ_ONLY_AUDITOR,
)


def user_in_group(user, group_name):
    return (
        user
        and user.is_authenticated
        and user.groups.filter(name=group_name).exists()
    )


def is_developer(user):
    return user_in_group(user, DEVELOPER)


def is_compliance_officer(user):
    return user_in_group(user, COMPLIANCE_OFFICER)


def is_read_only_auditor(user):
    return user_in_group(user, READ_ONLY_AUDITOR)


def is_internal_user(user):
    return (
        is_developer(user)
        or is_compliance_officer(user)
        or is_read_only_auditor(user)
    )


class IsNotReadOnlyAuditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not is_read_only_auditor(request.user)


class IsInternalRole(BasePermission):
    """
    Developer and ComplianceOfficer can access.
    ReadOnlyAuditor can access only safe methods.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if is_developer(request.user) or is_compliance_officer(request.user):
            return True

        return request.method in SAFE_METHODS and is_read_only_auditor(request.user)


class IsOwnerOrInternalRole(BasePermission):
    """
    Normal users can access their own records.
    Internal users can access broader records.
    ReadOnlyAuditor remains read-only.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if is_read_only_auditor(request.user) and request.method not in SAFE_METHODS:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if is_developer(request.user) or is_compliance_officer(request.user):
            return True

        if is_read_only_auditor(request.user):
            return request.method in SAFE_METHODS

        owner = getattr(obj, "user", None)

        if owner is None and hasattr(obj, "transaction"):
            owner = obj.transaction.user

        return owner == request.user