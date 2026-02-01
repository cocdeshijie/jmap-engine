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
    
    def get_permissions(self) -> Dict[str, Any]:
        """
        Get detailed information about API key permissions and capabilities.
        
        Returns:
            Dictionary containing:
            - capabilities: Server capabilities
            - accounts: Available accounts and their features
            - primary_accounts: Primary account IDs for each capability
            - supported_features: Human-readable list of what you can do
        
        Example:
            >>> perms = client.get_permissions()
            >>> print(f"Capabilities: {perms['supported_features']}")
            >>> for account_id, info in perms['accounts'].items():
            >>>     print(f"Account: {info['name']}")
        """
        result = {
            'capabilities': self.session.capabilities,
            'accounts': self.session.accounts,
            'primary_accounts': self.session.primary_accounts,
            'supported_features': []
        }
        
        # Parse capabilities into human-readable features
        cap_descriptions = {
            'urn:ietf:params:jmap:core': 'Core JMAP protocol',
            'urn:ietf:params:jmap:mail': 'Email reading and management',
            'urn:ietf:params:jmap:submission': 'Email sending',
            'urn:ietf:params:jmap:vacationresponse': 'Vacation responses',
            'urn:ietf:params:jmap:contacts': 'Contact management',
            'urn:ietf:params:jmap:calendars': 'Calendar management',
            'urn:ietf:params:jmap:quota': 'Storage quota information',
            'urn:ietf:params:jmap:blob': 'File upload/download',
            'https://www.fastmail.com/dev/maskedemail': 'Fastmail masked email',
        }
        
        for cap in self.session.capabilities.keys():
            feature = cap_descriptions.get(cap, cap)
            result['supported_features'].append(feature)
        
        return result
    
    def print_permissions(self) -> None:
        """
        Print a human-readable summary of API key permissions.
        
        Shows what operations are allowed with the current API key.
        """
        perms = self.get_permissions()
        
        print("=" * 70)
        print("              JMAP API Key Permissions")
        print("=" * 70)
        print("\n💡 This shows what YOUR API KEY can do (not account properties).")
        print("   The permissions below reflect your API token's scope.\n")
        
        # Capabilities
        print("✅ API Key Has Access To:")
        for feature in perms['supported_features']:
            print(f"   • {feature}")
        
        # Accounts
        print(f"\n👤 Accounts ({len(perms['accounts'])}):")
        for account_id, account_info in perms['accounts'].items():
            name = account_info.get('name', 'Unknown')
            is_personal = account_info.get('isPersonal', False)
            is_readonly = account_info.get('isReadOnly', False)
            
            account_type = []
            if is_personal:
                account_type.append('Personal')
            # Note: isReadOnly is an account property, not API key permission
            # Don't display it as it's confusing - check capabilities instead
            
            type_str = f" ({', '.join(account_type)})" if account_type else ""
            print(f"   • {name}{type_str}")
            print(f"     ID: {account_id}")
            
            # Account capabilities
            account_caps = account_info.get('accountCapabilities', {})
            if account_caps:
                print(f"     Features:")
                displayed_features = set()  # Track what we've shown
                
                for cap in account_caps.keys():
                    if 'mail' in cap and 'mail' not in displayed_features:
                        # Get mail-specific limits
                        mail_info = account_caps.get(cap, {})
                        max_size = mail_info.get('maxSizeMessageAttachments')
                        if max_size:
                            size_mb = max_size / (1024 * 1024)
                            print(f"       - Mail (max attachment: {size_mb:.1f} MB)")
                        else:
                            print(f"       - Mail")
                        displayed_features.add('mail')
                    elif 'submission' in cap and 'submission' not in displayed_features:
                        print(f"       - Email sending")
                        displayed_features.add('submission')
                    elif 'contacts' in cap and 'contacts' not in displayed_features:
                        print(f"       - Contacts")
                        displayed_features.add('contacts')
                    elif 'calendars' in cap and 'calendars' not in displayed_features:
                        print(f"       - Calendars")
                        displayed_features.add('calendars')
        
        # Primary accounts
        print(f"\n🌟 Primary Accounts:")
        displayed_primary = {}  # Track account_id -> types to avoid duplicates
        
        for cap, account_id in perms['primary_accounts'].items():
            account = perms['accounts'].get(account_id, {})
            name = account.get('name', 'Unknown')
            
            if account_id not in displayed_primary:
                displayed_primary[account_id] = {'name': name, 'types': []}
            
            if 'mail' in cap.lower() and 'mail' not in displayed_primary[account_id]['types']:
                displayed_primary[account_id]['types'].append('mail')
            elif 'contact' in cap.lower() and 'contacts' not in displayed_primary[account_id]['types']:
                displayed_primary[account_id]['types'].append('contacts')
            elif 'calendar' in cap.lower() and 'calendars' not in displayed_primary[account_id]['types']:
                displayed_primary[account_id]['types'].append('calendars')
        
        # Display consolidated
        for account_id, info in displayed_primary.items():
            types_str = ', '.join(t.capitalize() for t in info['types'])
            print(f"   • {types_str}: {info['name']}")
        
        # Check for specific permissions
        print(f"\n🔑 What This API Key Can Do:")
        
        can_read_mail = 'urn:ietf:params:jmap:mail' in perms['capabilities']
        can_send_mail = 'urn:ietf:params:jmap:submission' in perms['capabilities']
        can_manage_contacts = 'urn:ietf:params:jmap:contacts' in perms['capabilities']
        can_manage_calendars = 'urn:ietf:params:jmap:calendars' in perms['capabilities']
        
        permissions = [
            ('Read emails', can_read_mail, '📧'),
            ('Send emails', can_send_mail, '📤'),
            ('Manage contacts', can_manage_contacts, '👥'),
            ('Manage calendars', can_manage_calendars, '📅'),
        ]
        
        for perm_name, allowed, icon in permissions:
            status = '✅ CAN' if allowed else '❌ CANNOT'
            print(f"   {status} {icon} {perm_name}")
        
        # Check for account-level restrictions
        print(f"\n⚠️  Account-Level Restrictions:")
        has_warnings = False
        
        for account_id, account_info in perms['accounts'].items():
            is_readonly = account_info.get('isReadOnly', False)
            
            if is_readonly:
                has_warnings = True
                account_name = account_info.get('name', account_id)
                print(f"   🔒 Account '{account_name}' is READ-ONLY")
                print(f"      → API key has write permissions, but account is restricted")
                print(f"      → You CAN read emails, but CANNOT send/modify/delete")
                print(f"      → Contact Fastmail support to enable write access")
                
                if can_send_mail:
                    print(f"      ⚠️  Sending emails will FAIL despite API key having permission!")
        
        if not has_warnings:
            print(f"   ✅ No account restrictions detected")
        
        print("\n" + "=" * 70)
    
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
        
        Raises:
            JMAPMethodError: If account is read-only or API key lacks permission
        """
        if account_id is None:
            account_id = self.session.get_account_id()
        
        # Check if account is read-only
        account_info = self.session.accounts.get(account_id, {})
        if account_info.get('isReadOnly', False):
            from .exceptions import JMAPMethodError
            raise JMAPMethodError(
                f"Cannot send email: Account is READ-ONLY.\n"
                f"Your API key has send permission, but the account '{account_info.get('name', account_id)}' "
                f"is restricted by Fastmail.\n"
                f"💡 Solution: Contact Fastmail support to remove read-only restriction from your account.\n"
                f"   Or check if this is a shared/delegated account with limited access.",
                error_type='accountReadOnly'
            )
        
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
