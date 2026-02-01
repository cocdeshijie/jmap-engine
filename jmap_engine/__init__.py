"""
JMAP Engine - Python library for JMAP protocol (RFC 8620, RFC 8621)
"""

__version__ = "0.1.0"
__author__ = "cocdeshijie"
__license__ = "MIT"

from .client import JMAPClient
from .email import Email, EmailQuery, EmailSubmission
from .exceptions import (
    JMAPError,
    JMAPAuthError,
    JMAPNetworkError,
    JMAPServerError,
)

__all__ = [
    "JMAPClient",
    "Email",
    "EmailQuery",
    "EmailSubmission",
    "JMAPError",
    "JMAPAuthError",
    "JMAPNetworkError",
    "JMAPServerError",
]
