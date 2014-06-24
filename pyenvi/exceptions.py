class MultipleInstanceError(Exception):
    """
    Raised when another instance of PyEnvi is instantiated.
    """
    pass

class NotRunningError(Exception):
    """
    Raised when PyEnvi is not running
    """
    pass

class AlreadyRunningError(Exception):
    """
    Raised when PyEnvi is not running
    """
    pass

class NotSetError(Exception):
    """
    Raised when trying to get a variable that doesn't exist.
    """
    pass
