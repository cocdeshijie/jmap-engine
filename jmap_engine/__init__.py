"""
JMAP Engine - Python library for JMAP protocol (RFC 8620, RFC 8621)
"""

__version__ = "0.2.1"
__author__ = "cocdeshijie"
__license__ = "MIT"

from .client import JMAPClient
from .email import Email, EmailQuery, EmailSubmission, EmailAddress, EmailBodyPart
from .mailbox import Mailbox, MailboxTree
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
    "EmailAddress",
    "EmailBodyPart",
    "Mailbox",
    "MailboxTree",
    "JMAPError",
    "JMAPAuthError",
    "JMAPNetworkError",
    "JMAPServerError",
]
