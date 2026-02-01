"""
Tests for Email models
"""

import pytest
from datetime import datetime
from jmap_engine.email import Email, EmailAddress, EmailBodyPart, EmailQuery


def test_email_address():
    """Test EmailAddress creation and serialization"""
    # With name
    addr = EmailAddress(email='user@example.com', name='Test User')
    assert str(addr) == '"Test User" <user@example.com>'
    assert addr.to_dict() == {'email': 'user@example.com', 'name': 'Test User'}
    
    # Without name
    addr2 = EmailAddress(email='user@example.com')
    assert str(addr2) == 'user@example.com'
    assert addr2.to_dict() == {'email': 'user@example.com'}
    
    # From dict
    addr3 = EmailAddress.from_dict({'email': 'test@example.com', 'name': 'Test'})
    assert addr3.email == 'test@example.com'
    assert addr3.name == 'Test'


def test_email_body_part():
    """Test EmailBodyPart"""
    part = EmailBodyPart(type='text/plain', value='Hello world')
    assert part.to_dict() == {
        'type': 'text/plain',
        'value': 'Hello world',
        'charset': 'utf-8'
    }


def test_email_creation():
    """Test Email object creation"""
    email = Email(
        subject='Test Subject',
        from_=[EmailAddress(email='sender@example.com', name='Sender')],
        to=[EmailAddress(email='recipient@example.com')],
        text_body=[EmailBodyPart(type='text/plain', value='Hello')]
    )
    
    assert email.subject == 'Test Subject'
    assert len(email.from_) == 1
    assert email.from_[0].email == 'sender@example.com'
    assert len(email.to) == 1
    assert email.to[0].email == 'recipient@example.com'


def test_email_serialization():
    """Test Email to_dict() serialization"""
    email = Email(
        subject='Test',
        from_=[EmailAddress(email='sender@example.com')],
        to=[EmailAddress(email='recipient@example.com')]
    )
    
    data = email.to_dict()
    assert data['subject'] == 'Test'
    assert len(data['from']) == 1
    assert data['from'][0]['email'] == 'sender@example.com'


def test_email_deserialization():
    """Test Email from_dict() deserialization"""
    data = {
        'id': 'email123',
        'subject': 'Test Email',
        'from': [{'email': 'sender@example.com', 'name': 'Sender'}],
        'to': [{'email': 'recipient@example.com'}],
        'receivedAt': '2026-02-01T12:00:00Z',
        'keywords': {'$seen': True},
        'textBody': [{'type': 'text/plain', 'value': 'Hello'}]
    }
    
    email = Email.from_dict(data)
    assert email.id == 'email123'
    assert email.subject == 'Test Email'
    assert email.from_[0].email == 'sender@example.com'
    assert email.from_[0].name == 'Sender'
    assert not email.is_unread()  # Has $seen keyword


def test_email_keywords():
    """Test email keyword checks"""
    # Unread email (no $seen)
    unread = Email(keywords={})
    assert unread.is_unread()
    assert not unread.is_flagged()
    
    # Read email
    read = Email(keywords={'$seen': True})
    assert not read.is_unread()
    
    # Flagged email
    flagged = Email(keywords={'$flagged': True})
    assert flagged.is_flagged()
    
    # Draft
    draft = Email(keywords={'$draft': True})
    assert draft.is_draft()


def test_email_content_extraction():
    """Test text/HTML content extraction"""
    email = Email(
        text_body=[
            EmailBodyPart(type='text/plain', value='Part 1'),
            EmailBodyPart(type='text/plain', value='Part 2')
        ],
        html_body=[
            EmailBodyPart(type='text/html', value='<p>HTML 1</p>'),
            EmailBodyPart(type='text/html', value='<p>HTML 2</p>')
        ]
    )
    
    assert email.get_text_content() == 'Part 1\n\nPart 2'
    assert email.get_html_content() == '<p>HTML 1</p>\n\n<p>HTML 2</p>'


def test_email_query():
    """Test EmailQuery filter creation"""
    query = EmailQuery(
        in_mailbox='inbox123',
        has_keyword='$seen',
        min_size=1024,
        subject='test'
    )
    
    data = query.to_dict()
    assert data['inMailbox'] == 'inbox123'
    assert data['hasKeyword'] == '$seen'
    assert data['minSize'] == 1024
    assert data['subject'] == 'test'


def test_email_query_with_dates():
    """Test EmailQuery with date filters"""
    now = datetime.now()
    query = EmailQuery(
        after=now,
        before=now
    )
    
    data = query.to_dict()
    assert 'after' in data
    assert 'before' in data
