"""Domain service errors that are safe for future API adapters to handle."""


class OrganizationNotFoundError(LookupError):
    """Raised when an organization-scoped action references no organization."""


class DuplicateUserEmailError(ValueError):
    """Raised when an email is already used within an organization."""
