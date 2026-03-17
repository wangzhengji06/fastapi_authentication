class InvalidCredentials(Exception):
    error_code = "invalid_credentials"
    message = "Invalid email or password"


class PermissionDenied(Exception):
    error_code = "permission_denied"
    message = "Not authorized"


class UserAlreadyExists(Exception):
    error_code = "user_already_exists"
    message = "Username or Email already exists"
