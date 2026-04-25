class InvalidCredentials(Exception):
    error_code = "invalid_credentials"
    message = "Invalid email or password"


class PermissionDenied(Exception):
    error_code = "permission_denied"
    message = "Not authorized"


class UserAlreadyExists(Exception):
    error_code = "user_already_exists"
    message = "Username or Email already exists"


class UserNotFound(Exception):
    error_code = "user_not_found"
    message = "User Not Found"


class ProjectNotFound(Exception):
    error_code = "project_not_found"
    message = "Project Not Found"


class ShareDenied(Exception):
    error_code = "share_denied"
    message = "Invalid share target"
