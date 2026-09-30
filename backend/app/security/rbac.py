from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User


def require_role(*allowed_roles: str):
    """
    Usage in a route:
        @router.get("/admin/users")
        def list_users(user: User = Depends(require_role("system_admin"))):
            ...

    This is the SAME mechanism every protected route in later phases will use —
    it is enforced on the backend, never relies on the frontend hiding a button.
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency
