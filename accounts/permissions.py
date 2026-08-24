from rest_framework.permissions import BasePermission

# The three roles an admin appoints, as opposed to STUDENT (self-registered,
# no internal access). Every permission class below that gates ledger/budget/
# dashboard data checks against this set, not just "is authenticated".
INTERNAL_ROLES = ('ADMIN', 'FINANCE_OFFICER', 'COMMITTEE_MEMBER')


# Before saving or deleting anything, the brain always asks "is this
# person allowed?" - these are that check, reused by every app instead of
# re-implementing role logic per view.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class IsAdminOrFinanceOfficer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('ADMIN', 'FINANCE_OFFICER')
        )


# Any admin-appointed role can view; self-registered students cannot -
# there's no public/curated view built yet, so the alternative would be
# leaking the full ledger to anyone who signs up.
class IsInternalUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in INTERNAL_ROLES)


class ReadOnlyOrAdminFinance(BasePermission):
    """Admin-appointed roles can view (GET); only admins/finance officers can write."""

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role in INTERNAL_ROLES):
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return request.user.role in ('ADMIN', 'FINANCE_OFFICER')
