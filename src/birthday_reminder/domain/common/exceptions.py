class DomainException(Exception):
    """Base Domain Exception"""

    @property
    def title(self) -> str:
        return "A domain error occurred"
