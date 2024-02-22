class ApplicationException(Exception):
    """Base Application Exception"""

    @property
    def title(self) -> str:
        return "An application error occurred"


class UnexpectedError(ApplicationException):
    pass


class CommitError(UnexpectedError):
    pass


class RollbackError(UnexpectedError):
    pass


class RepoError(UnexpectedError):
    pass
