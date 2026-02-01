"""
JMAP Client - Main client class for JMAP operations
"""

import requests
from typing import Dict, List, Any, Optional
from .session import JMAPSession
from .mailbox import MailboxTree
from .exceptions import JMAPNetworkError, JMAPServerError, JMAPMethodError


class JMAPClient:
    """
    Main JMAP client class.
    
    Implements the JMAP protocol as specified in RFC 8620 (core) and RFC 8621 (mail).
    
    Example:
        >>> client = JMAPClient('https://jmap.example.com', 'user@example.com', 'password')
        >>> client.connect()
        >>> mailboxes = client.get_mailboxes()
        >>> emails = client.query_emails(filter={'inMailbox': 'inbox-id'})
    """
    
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30,
        use_bearer_token: bool = False
    ):
        """
        Initialize JMAP client.
        
        Args:
            base_url: Base URL of the JMAP server (e.g., 'https://jmap.example.com')
            username: Username or email address (not used with Bearer token)
            password: Password, app password, or API token (e.g., Fastmail API key)
            timeout: HTTP request timeout in seconds
            use_bearer_token: Use Bearer token auth (auto-detected for Fastmail API keys)
        """
        self.session = JMAPSession(base_url, username, password, timeout, use_bearer_token)
        self._request_id = 0
    
    def connect(self) -> None:
        """
        Connect to JMAP server and discover capabilities.
        
        This must be called before making any API requests.
        """
        self.session.discover_session()
    
    def close(self) -> None:
        """Close the JMAP client session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def _next_request_id(self) -> str:
        """Generate next request ID"""
        self._request_id += 1
        return f"req{self._request_id}"
    
    def make_request(
        self,
        method_calls: List[List[Any]],
        using: Optional[List[str]] = None
    ) -> Dict:
        """
        Make a JMAP API request.
        
        Args:
            method_calls: List of method calls [methodName, arguments, callId]
            using: List of capability URIs to declare
        
        Returns:
            Dict containing server response
        
        Raises:
            JMAPNetworkError: On network errors
            JMAPServerError: On server errors
        """
        if using is None:
            using = [
                'urn:ietf:params:jmap:core',
                'urn:ietf:params:jmap:mail'
            ]
        
        request_data = {
            'using': using,
            'methodCalls': method_calls
        }
        
        try:
            response = self.session.session.post(
                self.session.api_url,
                json=request_data,
                timeout=self.session.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise JMAPNetworkError(f"Request failed: {e}")
        
        try:
            response_data = response.json()
        except ValueError as e:
            raise JMAPServerError(f"Invalid JSON response: {e}")
        
        # Check for errors in method responses
        if 'methodResponses' in response_data:
            for method_response in response_data['methodResponses']:
                if method_response[0] == 'error':
                    error_type = method_response[1].get('type', 'unknown')
                    description = method_response[1].get('description', 'Unknown error')
                    raise JMAPMethodError(
                        f"Method error: {description}",
                        error_type=error_type
                    )
        
        return response_data
    
    def get_mailboxes(self, account_id: Optional[str] = None) -> List[Dict]:
        """
        Get all mailboxes.
        
        Args:
            account_id: Account ID (uses primary if not specified)
        
        Returns:
            List of mailbox objects
        """
        if account_id is None:
            account_id = self.session.get_account_id()
        
        method_calls = [
            [
                'Mailbox/get',
                {
                    'accountId': account_id,
                    'ids': None  # Get all mailboxes
                },
                self._next_request_id()
            ]
        ]
        
        response = self.make_request(method_calls)
        
        # Extract mailbox list from response
        for method_response in response['methodResponses']:
            if method_response[0] == 'Mailbox/get':
                return method_response[1]['list']
        
        return []
    
    def get_mailbox_tree(self, account_id: Optional[str] = None) -> MailboxTree:
        """
        Get mailbox tree structure for easy navigation.
        
        Args:
            account_id: Account ID (uses primary if not specified)
        
        Returns:
            MailboxTree object with hierarchical mailbox structure
        
        Example:
            >>> tree = client.get_mailbox_tree()
            >>> tree.print_tree()
            >>> inbox = tree.get_by_role('inbox')
            >>> print(f"Inbox has {inbox.total_emails} emails")
        """
        mailboxes = self.get_mailboxes(account_id)
        return MailboxTree(mailboxes)
    
    def query_emails(
        self,
        filter: Optional[Dict] = None,
        sort: Optional[List[Dict]] = None,
        limit: Optional[int] = None,
        account_id: Optional[str] = None
    ) -> List[str]:
        """
        Query email IDs matching criteria.
        
        Args:
            filter: Filter criteria (e.g., {'inMailbox': 'mailbox-id'})
            sort: Sort criteria (e.g., [{'property': 'receivedAt', 'isAscending': False}])
            limit: Maximum number of results
            account_id: Account ID (uses primary if not specified)
        
        Returns:
            List of email IDs
        """
        if account_id is None:
            account_id = self.session.get_account_id()
        
        query_args = {
            'accountId': account_id
        }
        
        if filter is not None:
            query_args['filter'] = filter
        if sort is not None:
            query_args['sort'] = sort
        if limit is not None:
            query_args['limit'] = limit
        
        method_calls = [
            ['Email/query', query_args, self._next_request_id()]
        ]
        
        response = self.make_request(method_calls)
        
        for method_response in response['methodResponses']:
            if method_response[0] == 'Email/query':
                return method_response[1]['ids']
        
        return []
    
    def get_emails(
        self,
        ids: List[str],
        properties: Optional[List[str]] = None,
        account_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get email objects by IDs.
        
        Args:
            ids: List of email IDs
            properties: Properties to fetch (fetches all if None)
            account_id: Account ID (uses primary if not specified)
        
        Returns:
            List of email objects
        """
        if account_id is None:
            account_id = self.session.get_account_id()
        
        get_args = {
            'accountId': account_id,
            'ids': ids
        }
        
        if properties is not None:
            get_args['properties'] = properties
        
        method_calls = [
            ['Email/get', get_args, self._next_request_id()]
        ]
        
        response = self.make_request(method_calls)
        
        for method_response in response['methodResponses']:
            if method_response[0] == 'Email/get':
                return method_response[1]['list']
        
        return []
    
    def send_email(
        self,
        email: Dict,
        identity_id: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> Dict:
        """
        Send an email.
        
        Args:
            email: Email object to send
            identity_id: Identity ID to send from (uses default if None)
            account_id: Account ID (uses primary if not specified)
        
        Returns:
            EmailSubmission object
        """
        if account_id is None:
            account_id = self.session.get_account_id()
        
        # Create email draft first
        create_args = {
            'accountId': account_id,
            'create': {
                'draft': email
            }
        }
        
        submission_args = {
            'accountId': account_id,
            'create': {
                'submission': {
                    'emailId': '#draft',
                    'identityId': identity_id or '$default'
                }
            },
            'onSuccessDestroyEmail': ['#submission']
        }
        
        method_calls = [
            ['Email/set', create_args, 'c1'],
            ['EmailSubmission/set', submission_args, 'c2']
        ]
        
        response = self.make_request(method_calls)
        
        # Extract submission result
        for method_response in response['methodResponses']:
            if method_response[0] == 'EmailSubmission/set':
                created = method_response[1].get('created', {})
                if 'submission' in created:
                    return created['submission']
        
        return {}
