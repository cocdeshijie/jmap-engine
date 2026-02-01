"""
Tests for permission checking
"""

import pytest
from unittest.mock import MagicMock
from jmap_engine import JMAPClient


def test_get_permissions():
    """Test getting permissions from session"""
    client = JMAPClient('https://example.com', 'user', 'pass')
    
    # Mock session data
    client.session.capabilities = {
        'urn:ietf:params:jmap:core': {},
        'urn:ietf:params:jmap:mail': {},
        'urn:ietf:params:jmap:submission': {}
    }
    
    client.session.accounts = {
        'u1': {
            'name': 'test@example.com',
            'isPersonal': True,
            'accountCapabilities': {
                'urn:ietf:params:jmap:mail': {
                    'maxSizeMessageAttachments': 52428800
                }
            }
        }
    }
    
    client.session.primary_accounts = {
        'urn:ietf:params:jmap:mail': 'u1'
    }
    
    # Get permissions
    perms = client.get_permissions()
    
    # Check structure
    assert 'capabilities' in perms
    assert 'accounts' in perms
    assert 'primary_accounts' in perms
    assert 'supported_features' in perms
    
    # Check capabilities
    assert 'urn:ietf:params:jmap:core' in perms['capabilities']
    assert 'urn:ietf:params:jmap:mail' in perms['capabilities']
    
    # Check features
    assert len(perms['supported_features']) > 0
    assert 'Core JMAP protocol' in perms['supported_features']
    
    # Check accounts
    assert 'u1' in perms['accounts']
    assert perms['accounts']['u1']['name'] == 'test@example.com'


def test_print_permissions(capsys):
    """Test printing permissions"""
    client = JMAPClient('https://example.com', 'user', 'pass')
    
    # Mock session data
    client.session.capabilities = {
        'urn:ietf:params:jmap:core': {},
        'urn:ietf:params:jmap:mail': {}
    }
    
    client.session.accounts = {
        'u1': {'name': 'test@example.com', 'isPersonal': True}
    }
    
    client.session.primary_accounts = {
        'urn:ietf:params:jmap:mail': 'u1'
    }
    
    # Print permissions
    client.print_permissions()
    
    # Check output
    captured = capsys.readouterr()
    assert 'JMAP API Key Permissions' in captured.out
    assert 'Supported Features' in captured.out
    assert 'Core JMAP protocol' in captured.out
    assert 'test@example.com' in captured.out


def test_permission_features():
    """Test feature detection from capabilities"""
    client = JMAPClient('https://example.com', 'user', 'pass')
    
    # Mock different capability sets
    client.session.capabilities = {
        'urn:ietf:params:jmap:core': {},
        'urn:ietf:params:jmap:mail': {},
        'urn:ietf:params:jmap:submission': {},
        'urn:ietf:params:jmap:contacts': {},
        'https://www.fastmail.com/dev/maskedemail': {}
    }
    
    client.session.accounts = {}
    client.session.primary_accounts = {}
    
    perms = client.get_permissions()
    
    # Check all features are detected
    features = perms['supported_features']
    assert 'Core JMAP protocol' in features
    assert 'Email reading and management' in features
    assert 'Email sending' in features
    assert 'Contact management' in features
    assert 'Fastmail masked email' in features
