"""
JMAP Mailbox models and utilities
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Mailbox:
    """
    JMAP Mailbox object with navigation utilities.
    
    Represents a mailbox/folder as defined in RFC 8621.
    """
    
    # Core properties
    id: str
    name: str
    parent_id: Optional[str] = None
    role: Optional[str] = None
    sort_order: int = 0
    
    # Email counts
    total_emails: int = 0
    unread_emails: int = 0
    total_threads: int = 0
    unread_threads: int = 0
    
    # Mailbox capabilities
    my_rights: Dict[str, bool] = field(default_factory=dict)
    is_subscribed: bool = True
    
    # Internal navigation
    _children: List['Mailbox'] = field(default_factory=list, repr=False)
    _parent: Optional['Mailbox'] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Mailbox':
        """Create Mailbox from JMAP dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            parent_id=data.get('parentId'),
            role=data.get('role'),
            sort_order=data.get('sortOrder', 0),
            total_emails=data.get('totalEmails', 0),
            unread_emails=data.get('unreadEmails', 0),
            total_threads=data.get('totalThreads', 0),
            unread_threads=data.get('unreadThreads', 0),
            my_rights=data.get('myRights', {}),
            is_subscribed=data.get('isSubscribed', True)
        )
    
    def to_dict(self) -> Dict:
        """Convert to JMAP dictionary format"""
        result = {
            'id': self.id,
            'name': self.name,
            'sortOrder': self.sort_order,
            'totalEmails': self.total_emails,
            'unreadEmails': self.unread_emails,
            'totalThreads': self.total_threads,
            'unreadThreads': self.unread_threads,
            'isSubscribed': self.is_subscribed
        }
        
        if self.parent_id:
            result['parentId'] = self.parent_id
        if self.role:
            result['role'] = self.role
        if self.my_rights:
            result['myRights'] = self.my_rights
        
        return result
    
    @property
    def path(self) -> str:
        """Get full path of mailbox (e.g., 'Inbox/Subfolder/Deep')"""
        if self._parent:
            return f"{self._parent.path}/{self.name}"
        return self.name
    
    @property
    def depth(self) -> int:
        """Get depth level (0 for root mailboxes)"""
        if self._parent:
            return self._parent.depth + 1
        return 0
    
    @property
    def children(self) -> List['Mailbox']:
        """Get direct children mailboxes"""
        return self._children
    
    @property
    def has_children(self) -> bool:
        """Check if mailbox has children"""
        return len(self._children) > 0
    
    def get_all_children(self, include_self: bool = False) -> List['Mailbox']:
        """Get all descendant mailboxes (recursive)"""
        result = [self] if include_self else []
        for child in self._children:
            result.extend(child.get_all_children(include_self=True))
        return result
    
    def get_total_emails_recursive(self) -> int:
        """Get total email count including all children"""
        total = self.total_emails
        for child in self._children:
            total += child.get_total_emails_recursive()
        return total
    
    def get_unread_emails_recursive(self) -> int:
        """Get unread email count including all children"""
        total = self.unread_emails
        for child in self._children:
            total += child.get_unread_emails_recursive()
        return total
    
    def find_by_name(self, name: str, recursive: bool = False) -> Optional['Mailbox']:
        """Find child mailbox by name"""
        for child in self._children:
            if child.name == name:
                return child
            if recursive:
                result = child.find_by_name(name, recursive=True)
                if result:
                    return result
        return None
    
    def find_by_role(self, role: str, recursive: bool = False) -> Optional['Mailbox']:
        """Find child mailbox by role (inbox, sent, trash, etc.)"""
        for child in self._children:
            if child.role == role:
                return child
            if recursive:
                result = child.find_by_role(role, recursive=True)
                if result:
                    return result
        return None
    
    def can_read(self) -> bool:
        """Check if user can read this mailbox"""
        return self.my_rights.get('mayReadItems', True)
    
    def can_write(self) -> bool:
        """Check if user can add emails to this mailbox"""
        return self.my_rights.get('mayAddItems', True)
    
    def can_delete(self) -> bool:
        """Check if user can delete this mailbox"""
        return self.my_rights.get('mayRemoveItems', True)
    
    def __str__(self) -> str:
        """String representation"""
        icon = {
            'inbox': '📥',
            'sent': '📤',
            'drafts': '📝',
            'trash': '🗑️',
            'spam': '🚫',
            'archive': '📦',
            'junk': '🚫'
        }.get(self.role, '📂')
        
        unread_str = f" ({self.unread_emails} unread)" if self.unread_emails > 0 else ""
        return f"{icon} {self.name} [{self.total_emails} emails{unread_str}]"


class MailboxTree:
    """
    Mailbox tree structure for easy navigation.
    
    Organizes mailboxes into a tree hierarchy.
    """
    
    def __init__(self, mailboxes: List[Dict]):
        """
        Initialize mailbox tree from JMAP mailbox list.
        
        Args:
            mailboxes: List of mailbox dictionaries from JMAP
        """
        # Create Mailbox objects
        self._mailboxes_by_id: Dict[str, Mailbox] = {}
        self._root_mailboxes: List[Mailbox] = []
        
        # First pass: create all mailbox objects
        for mb_data in mailboxes:
            mailbox = Mailbox.from_dict(mb_data)
            self._mailboxes_by_id[mailbox.id] = mailbox
        
        # Second pass: build tree structure
        for mailbox in self._mailboxes_by_id.values():
            if mailbox.parent_id:
                parent = self._mailboxes_by_id.get(mailbox.parent_id)
                if parent:
                    parent._children.append(mailbox)
                    mailbox._parent = parent
                else:
                    # Parent not found, treat as root
                    self._root_mailboxes.append(mailbox)
            else:
                self._root_mailboxes.append(mailbox)
        
        # Sort children by sort_order
        for mailbox in self._mailboxes_by_id.values():
            mailbox._children.sort(key=lambda m: (m.sort_order, m.name))
        
        # Sort roots
        self._root_mailboxes.sort(key=lambda m: (m.sort_order, m.name))
    
    @property
    def roots(self) -> List[Mailbox]:
        """Get root-level mailboxes"""
        return self._root_mailboxes
    
    def get_by_id(self, mailbox_id: str) -> Optional[Mailbox]:
        """Get mailbox by ID"""
        return self._mailboxes_by_id.get(mailbox_id)
    
    def get_by_name(self, name: str) -> Optional[Mailbox]:
        """Get mailbox by name (searches all mailboxes)"""
        for mailbox in self._mailboxes_by_id.values():
            if mailbox.name == name:
                return mailbox
        return None
    
    def get_by_role(self, role: str) -> Optional[Mailbox]:
        """Get mailbox by role (inbox, sent, trash, etc.)"""
        for mailbox in self._mailboxes_by_id.values():
            if mailbox.role == role:
                return mailbox
        return None
    
    def find_by_path(self, path: str, separator: str = '/') -> Optional[Mailbox]:
        """
        Find mailbox by path.
        
        Args:
            path: Path like 'Inbox/Subfolder/Deep'
            separator: Path separator (default: '/')
        
        Returns:
            Mailbox if found, None otherwise
        """
        parts = path.split(separator)
        current = None
        
        # Find root
        for root in self._root_mailboxes:
            if root.name == parts[0]:
                current = root
                break
        
        if not current:
            return None
        
        # Navigate down
        for part in parts[1:]:
            current = current.find_by_name(part, recursive=False)
            if not current:
                return None
        
        return current
    
    def get_all_mailboxes(self) -> List[Mailbox]:
        """Get all mailboxes as flat list"""
        return list(self._mailboxes_by_id.values())
    
    def print_tree(self, max_depth: Optional[int] = None, show_counts: bool = True):
        """
        Print mailbox tree in a nice format.
        
        Args:
            max_depth: Maximum depth to display (None = unlimited)
            show_counts: Show email counts
        """
        def print_mailbox(mailbox: Mailbox, indent: int = 0):
            if max_depth is not None and indent > max_depth:
                return
            
            # Icon
            icon = {
                'inbox': '📥',
                'sent': '📤',
                'drafts': '📝',
                'trash': '🗑️',
                'spam': '🚫',
                'archive': '📦',
                'junk': '🚫'
            }.get(mailbox.role, '📂')
            
            # Indent
            prefix = '  ' * indent + ('└─ ' if indent > 0 else '')
            
            # Name
            name = mailbox.name
            
            # Counts
            counts = ''
            if show_counts:
                if mailbox.has_children:
                    total_recursive = mailbox.get_total_emails_recursive()
                    unread_recursive = mailbox.get_unread_emails_recursive()
                    counts = f" [{mailbox.total_emails}/{total_recursive} total, {mailbox.unread_emails}/{unread_recursive} unread]"
                else:
                    counts = f" [{mailbox.total_emails} total, {mailbox.unread_emails} unread]"
            
            print(f"{prefix}{icon} {name}{counts}")
            
            # Print children
            for child in mailbox.children:
                print_mailbox(child, indent + 1)
        
        for root in self._root_mailboxes:
            print_mailbox(root)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get overall statistics"""
        stats = {
            'total_mailboxes': len(self._mailboxes_by_id),
            'root_mailboxes': len(self._root_mailboxes),
            'total_emails': 0,
            'unread_emails': 0,
            'deepest_level': 0
        }
        
        for mailbox in self._mailboxes_by_id.values():
            stats['total_emails'] += mailbox.total_emails
            stats['unread_emails'] += mailbox.unread_emails
            stats['deepest_level'] = max(stats['deepest_level'], mailbox.depth)
        
        return stats
