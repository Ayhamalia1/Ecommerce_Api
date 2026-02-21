from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManagerOrReadOnly(BasePermission):
    """
    يسمح بالقراءة للجميع
    والتعديل / الحذف للمانجر فقط
    """

    def has_permission(self, request, view):
        # السماح بالقراءة فقط (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # التعديل أو الحذف → مانجر فقط
        return (
            request.user.is_authenticated and
            getattr(request.user, "role", None) == "manager"
        )
