"""
JMAP Session management
"""

import requests
from typing import Dict, Optional
from .exceptions import JMAPAuthError, JMAPNetworkError


class JMAPSession:
    """
    Manages JMAP session and capabilities.
    
    Implements session discovery and authentication as per RFC 8620.
    """
    
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # Session data
        self.api_url: Optional[str] = None
        self.download_url: Optional[str] = None
        self.upload_url: Optional[str] = None
        self.event_source_url: Optional[str] = None
        self.capabilities: Dict = {}
        self.accounts: Dict = {}
        self.primary_accounts: Dict = {}
        self.state: Optional[str] = None
        
        # HTTP session
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def discover_session(self) -> None:
        """
        Discover JMAP session endpoint and capabilities.
        
        Fetches the session object from /.well-known/jmap
        as specified in RFC 8620 Section 2.2.
        """
        well_known_url = f"{self.base_url}/.well-known/jmap"
        
        try:
            response = self.session.get(well_known_url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise JMAPNetworkError(f"Failed to discover JMAP session: {e}")
        
        try:
            session_data = response.json()
        except ValueError as e:
            raise JMAPAuthError(f"Invalid JSON response: {e}")
        
        # Extract session information
        self.api_url = session_data.get('apiUrl')
        self.download_url = session_data.get('downloadUrl')
        self.upload_url = session_data.get('uploadUrl')
        self.event_source_url = session_data.get('eventSourceUrl')
        self.capabilities = session_data.get('capabilities', {})
        self.accounts = session_data.get('accounts', {})
        self.primary_accounts = session_data.get('primaryAccounts', {})
        self.state = session_data.get('state')
        
        if not self.api_url:
            raise JMAPAuthError("No API URL in session response")
    
    def get_account_id(self, capability: str = 'urn:ietf:params:jmap:mail') -> str:
        """Get the primary account ID for a given capability"""
        account_id = self.primary_accounts.get(capability)
        if not account_id and self.accounts:
            # Fall back to first account
            account_id = list(self.accounts.keys())[0]
        if not account_id:
            raise JMAPAuthError(f"No account found for capability: {capability}")
        return account_id
    
    def has_capability(self, capability: str) -> bool:
        """Check if server supports a capability"""
        return capability in self.capabilities
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
