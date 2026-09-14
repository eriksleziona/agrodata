"""Domain service errors that are safe for future API adapters to handle."""


class OrganizationNotFoundError(LookupError):
    """Raised when an organization-scoped action references no organization."""


class DuplicateUserEmailError(ValueError):
    """Raised when an email is already used within an organization."""


class MachineNotFoundError(LookupError):
    """Raised when a machine-scoped action references no machine."""


class DuplicateDeviceIdError(ValueError):
    """Raised when a device_id is already assigned to another machine."""


class ImplementNotFoundError(LookupError):
    """Raised when an implement-scoped action references no implement."""


class InvalidWorkingWidthError(ValueError):
    """Raised when an implement has a non-positive working width."""


class JobNotFoundError(LookupError):
    """Raised when a job-scoped action references no job."""


class InvalidJobStateTransitionError(ValueError):
    """Raised when an illegal lifecycle transition is attempted on a job."""


class InvalidCredentialsError(ValueError):
    """Raised when login credentials do not match any user."""


class InsufficientPermissionsError(PermissionError):
    """Raised when a user's role does not permit the requested action."""




