class SinkConfigError(ValueError):
    pass


class PyConnectException(Exception):
    """
    Base Class for all exceptions raised by the PyConnect framework.
    """

    pass


class NoCrashInfo(PyConnectException):
    """
    Exception that says that a callback returned `Status.CRASHED` without supplying any exception for status_info.
    """

    pass
