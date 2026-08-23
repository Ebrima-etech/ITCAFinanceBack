from rest_framework.permissions import BasePermission


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


class ReadOnlyOrAdminFinance(BasePermission):
    """Anyone authenticated can view (GET); only admins/finance officers can write."""

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return request.user.role in ('ADMIN', 'FINANCE_OFFICER')
