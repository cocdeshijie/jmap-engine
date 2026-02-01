"""
JMAP Engine exceptions
"""


class JMAPError(Exception):
    """Base exception for all JMAP errors"""
    pass


class JMAPAuthError(JMAPError):
    """Authentication error"""
    pass


class JMAPNetworkError(JMAPError):
    """Network communication error"""
    pass


class JMAPServerError(JMAPError):
    """Server-side error"""
    
    def __init__(self, message, error_type=None, status=None):
        super().__init__(message)
        self.error_type = error_type
        self.status = status


class JMAPInvalidRequestError(JMAPError):
    """Invalid request error"""
    pass


class JMAPMethodError(JMAPError):
    """Method-specific error"""
    
    def __init__(self, message, error_type=None):
        super().__init__(message)
        self.error_type = error_type
