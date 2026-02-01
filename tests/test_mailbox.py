"""
Tests for Mailbox and MailboxTree
"""

import pytest
from jmap_engine.mailbox import Mailbox, MailboxTree


def test_mailbox_from_dict():
    """Test Mailbox creation from dictionary"""
    data = {
        'id': 'mb1',
        'name': 'Inbox',
        'role': 'inbox',
        'parentId': None,
        'totalEmails': 100,
        'unreadEmails': 5,
        'sortOrder': 1
    }
    
    mailbox = Mailbox.from_dict(data)
    assert mailbox.id == 'mb1'
    assert mailbox.name == 'Inbox'
    assert mailbox.role == 'inbox'
    assert mailbox.total_emails == 100
    assert mailbox.unread_emails == 5


def test_mailbox_to_dict():
    """Test Mailbox serialization"""
    mailbox = Mailbox(
        id='mb1',
        name='Test',
        total_emails=10,
        unread_emails=2
    )
    
    data = mailbox.to_dict()
    assert data['id'] == 'mb1'
    assert data['name'] == 'Test'
    assert data['totalEmails'] == 10
    assert data['unreadEmails'] == 2


def test_mailbox_path():
    """Test mailbox path generation"""
    root = Mailbox(id='root', name='Inbox')
    child = Mailbox(id='child', name='Subfolder', parent_id='root')
    child._parent = root
    
    assert root.path == 'Inbox'
    assert child.path == 'Inbox/Subfolder'


def test_mailbox_depth():
    """Test depth calculation"""
    root = Mailbox(id='root', name='Root')
    level1 = Mailbox(id='l1', name='Level1', parent_id='root')
    level1._parent = root
    level2 = Mailbox(id='l2', name='Level2', parent_id='l1')
    level2._parent = level1
    
    assert root.depth == 0
    assert level1.depth == 1
    assert level2.depth == 2


def test_mailbox_children():
    """Test children management"""
    parent = Mailbox(id='p', name='Parent')
    child1 = Mailbox(id='c1', name='Child1')
    child2 = Mailbox(id='c2', name='Child2')
    
    parent._children = [child1, child2]
    
    assert parent.has_children
    assert len(parent.children) == 2
    assert child1 in parent.children


def test_mailbox_recursive_count():
    """Test recursive email counting"""
    root = Mailbox(id='root', name='Root', total_emails=10, unread_emails=2)
    child1 = Mailbox(id='c1', name='Child1', total_emails=5, unread_emails=1)
    child2 = Mailbox(id='c2', name='Child2', total_emails=3, unread_emails=0)
    
    root._children = [child1, child2]
    
    # 10 + 5 + 3 = 18
    assert root.get_total_emails_recursive() == 18
    # 2 + 1 + 0 = 3
    assert root.get_unread_emails_recursive() == 3


def test_mailbox_find_by_name():
    """Test finding child by name"""
    parent = Mailbox(id='p', name='Parent')
    child = Mailbox(id='c', name='Target')
    parent._children = [child]
    
    found = parent.find_by_name('Target')
    assert found is child
    
    not_found = parent.find_by_name('DoesNotExist')
    assert not_found is None


def test_mailbox_find_by_role():
    """Test finding child by role"""
    parent = Mailbox(id='p', name='Parent')
    inbox = Mailbox(id='i', name='Inbox', role='inbox')
    sent = Mailbox(id='s', name='Sent', role='sent')
    parent._children = [inbox, sent]
    
    found = parent.find_by_role('inbox')
    assert found is inbox


def test_mailbox_tree_creation():
    """Test MailboxTree creation"""
    mailboxes = [
        {'id': '1', 'name': 'Inbox', 'role': 'inbox', 'totalEmails': 10, 'unreadEmails': 2},
        {'id': '2', 'name': 'Sent', 'role': 'sent', 'totalEmails': 50, 'unreadEmails': 0},
        {'id': '3', 'name': 'Subfolder', 'parentId': '1', 'totalEmails': 5, 'unreadEmails': 1}
    ]
    
    tree = MailboxTree(mailboxes)
    
    assert len(tree.roots) == 2  # Inbox and Sent are roots
    assert len(tree.get_all_mailboxes()) == 3


def test_mailbox_tree_hierarchy():
    """Test parent-child relationships in tree"""
    mailboxes = [
        {'id': 'root', 'name': 'Root', 'totalEmails': 10},
        {'id': 'child', 'name': 'Child', 'parentId': 'root', 'totalEmails': 5}
    ]
    
    tree = MailboxTree(mailboxes)
    
    root = tree.get_by_id('root')
    child = tree.get_by_id('child')
    
    assert root.has_children
    assert child in root.children
    assert child._parent is root


def test_mailbox_tree_get_by_role():
    """Test finding mailbox by role"""
    mailboxes = [
        {'id': '1', 'name': 'Inbox', 'role': 'inbox', 'totalEmails': 10},
        {'id': '2', 'name': 'Sent', 'role': 'sent', 'totalEmails': 50}
    ]
    
    tree = MailboxTree(mailboxes)
    
    inbox = tree.get_by_role('inbox')
    assert inbox.name == 'Inbox'
    
    sent = tree.get_by_role('sent')
    assert sent.name == 'Sent'


def test_mailbox_tree_find_by_path():
    """Test finding mailbox by path"""
    mailboxes = [
        {'id': 'root', 'name': 'Inbox', 'totalEmails': 10},
        {'id': 'sub1', 'name': 'Projects', 'parentId': 'root', 'totalEmails': 5},
        {'id': 'sub2', 'name': '2025', 'parentId': 'sub1', 'totalEmails': 2}
    ]
    
    tree = MailboxTree(mailboxes)
    
    # Find by simple path
    inbox = tree.find_by_path('Inbox')
    assert inbox.id == 'root'
    
    # Find by nested path
    deep = tree.find_by_path('Inbox/Projects/2025')
    assert deep.id == 'sub2'
    
    # Not found
    not_found = tree.find_by_path('DoesNotExist')
    assert not_found is None


def test_mailbox_tree_statistics():
    """Test statistics generation"""
    mailboxes = [
        {'id': '1', 'name': 'Inbox', 'totalEmails': 100, 'unreadEmails': 10},
        {'id': '2', 'name': 'Sent', 'totalEmails': 200, 'unreadEmails': 0},
        {'id': '3', 'name': 'Sub', 'parentId': '1', 'totalEmails': 50, 'unreadEmails': 5}
    ]
    
    tree = MailboxTree(mailboxes)
    stats = tree.get_statistics()
    
    assert stats['total_mailboxes'] == 3
    assert stats['root_mailboxes'] == 2
    assert stats['total_emails'] == 350  # 100 + 200 + 50
    assert stats['unread_emails'] == 15  # 10 + 0 + 5
    assert stats['deepest_level'] == 1  # Sub is at level 1


def test_mailbox_permissions():
    """Test permission checks"""
    mailbox = Mailbox(
        id='test',
        name='Test',
        my_rights={
            'mayReadItems': True,
            'mayAddItems': True,
            'mayRemoveItems': False
        }
    )
    
    assert mailbox.can_read()
    assert mailbox.can_write()
    assert not mailbox.can_delete()
