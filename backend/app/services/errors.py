"""Domain service errors that are safe for future API adapters to handle."""


class OrganizationNotFoundError(LookupError):
    """Raised when an organization-scoped action references no organization."""


class DuplicateUserEmailError(ValueError):
    """Raised when an email is already used within an organization."""


class MachineNotFoundError(LookupError):
    """Raised when a machine-scoped action references no machine."""


class DuplicateDeviceIdError(ValueError):
    """Raised when a device_id is already assigned to another machine."""

