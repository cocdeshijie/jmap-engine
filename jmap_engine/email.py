"""
JMAP Email models and utilities
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmailAddress:
    """Email address with optional name"""
    email: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = {'email': self.email}
        if self.name:
            result['name'] = self.name
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmailAddress':
        return cls(
            email=data['email'],
            name=data.get('name')
        )
    
    def __str__(self) -> str:
        if self.name:
            return f'"{self.name}" <{self.email}>'
        return self.email


@dataclass
class EmailBodyPart:
    """Email body part (text or HTML)"""
    type: str  # 'text/plain' or 'text/html'
    value: str
    charset: str = 'utf-8'
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'value': self.value,
            'charset': self.charset
        }


@dataclass
class Email:
    """
    JMAP Email object.
    
    Represents an email message as defined in RFC 8621.
    """
    
    # Message metadata
    id: Optional[str] = None
    blob_id: Optional[str] = None
    thread_id: Optional[str] = None
    mailbox_ids: Dict[str, bool] = field(default_factory=dict)
    keywords: Dict[str, bool] = field(default_factory=dict)
    size: Optional[int] = None
    received_at: Optional[datetime] = None
    
    # Headers
    from_: List[EmailAddress] = field(default_factory=list)
    to: List[EmailAddress] = field(default_factory=list)
    cc: List[EmailAddress] = field(default_factory=list)
    bcc: List[EmailAddress] = field(default_factory=list)
    reply_to: List[EmailAddress] = field(default_factory=list)
    subject: str = ""
    sent_at: Optional[datetime] = None
    
    # Body
    text_body: List[EmailBodyPart] = field(default_factory=list)
    html_body: List[EmailBodyPart] = field(default_factory=list)
    attachments: List[Dict] = field(default_factory=list)
    
    # Additional metadata
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert email to JMAP dictionary format"""
        result = {}
        
        if self.mailbox_ids:
            result['mailboxIds'] = self.mailbox_ids
        if self.keywords:
            result['keywords'] = self.keywords
        
        # Headers
        if self.from_:
            result['from'] = [addr.to_dict() for addr in self.from_]
        if self.to:
            result['to'] = [addr.to_dict() for addr in self.to]
        if self.cc:
            result['cc'] = [addr.to_dict() for addr in self.cc]
        if self.bcc:
            result['bcc'] = [addr.to_dict() for addr in self.bcc]
        if self.reply_to:
            result['replyTo'] = [addr.to_dict() for addr in self.reply_to]
        if self.subject:
            result['subject'] = self.subject
        if self.sent_at:
            result['sentAt'] = self.sent_at.isoformat()
        
        # Body
        if self.text_body:
            result['textBody'] = [part.to_dict() for part in self.text_body]
        if self.html_body:
            result['htmlBody'] = [part.to_dict() for part in self.html_body]
        if self.attachments:
            result['attachments'] = self.attachments
        
        # Additional fields
        if self.message_id:
            result['messageId'] = self.message_id
        if self.in_reply_to:
            result['inReplyTo'] = self.in_reply_to
        if self.references:
            result['references'] = self.references
        if self.headers:
            result['headers'] = self.headers
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Email':
        """Create Email from JMAP dictionary"""
        # Parse email addresses
        from_ = [EmailAddress.from_dict(addr) for addr in data.get('from', [])]
        to = [EmailAddress.from_dict(addr) for addr in data.get('to', [])]
        cc = [EmailAddress.from_dict(addr) for addr in data.get('cc', [])]
        bcc = [EmailAddress.from_dict(addr) for addr in data.get('bcc', [])]
        reply_to = [EmailAddress.from_dict(addr) for addr in data.get('replyTo', [])]
        
        # Parse dates
        received_at = None
        if 'receivedAt' in data:
            received_at = datetime.fromisoformat(data['receivedAt'].replace('Z', '+00:00'))
        
        sent_at = None
        if 'sentAt' in data:
            sent_at = datetime.fromisoformat(data['sentAt'].replace('Z', '+00:00'))
        
        # Parse body parts
        text_body = []
        for part in data.get('textBody', []):
            text_body.append(EmailBodyPart(
                type=part.get('type', 'text/plain'),
                value=part.get('value', ''),
                charset=part.get('charset', 'utf-8')
            ))
        
        html_body = []
        for part in data.get('htmlBody', []):
            html_body.append(EmailBodyPart(
                type=part.get('type', 'text/html'),
                value=part.get('value', ''),
                charset=part.get('charset', 'utf-8')
            ))
        
        return cls(
            id=data.get('id'),
            blob_id=data.get('blobId'),
            thread_id=data.get('threadId'),
            mailbox_ids=data.get('mailboxIds', {}),
            keywords=data.get('keywords', {}),
            size=data.get('size'),
            received_at=received_at,
            from_=from_,
            to=to,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            subject=data.get('subject', ''),
            sent_at=sent_at,
            text_body=text_body,
            html_body=html_body,
            attachments=data.get('attachments', []),
            message_id=data.get('messageId'),
            in_reply_to=data.get('inReplyTo'),
            references=data.get('references', []),
            headers=data.get('headers', {})
        )
    
    def get_text_content(self) -> str:
        """Get plain text content of email"""
        if self.text_body:
            return '\n\n'.join(part.value for part in self.text_body)
        return ""
    
    def get_html_content(self) -> str:
        """Get HTML content of email"""
        if self.html_body:
            return '\n\n'.join(part.value for part in self.html_body)
        return ""
    
    def is_unread(self) -> bool:
        """Check if email is unread"""
        return '$seen' not in self.keywords
    
    def is_flagged(self) -> bool:
        """Check if email is flagged"""
        return '$flagged' in self.keywords
    
    def is_draft(self) -> bool:
        """Check if email is a draft"""
        return '$draft' in self.keywords


@dataclass
class EmailQuery:
    """Email query filter"""
    in_mailbox: Optional[str] = None
    after: Optional[datetime] = None
    before: Optional[datetime] = None
    has_keyword: Optional[str] = None
    not_keyword: Optional[str] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    text: Optional[str] = None
    from_: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to JMAP filter format"""
        result = {}
        
        if self.in_mailbox:
            result['inMailbox'] = self.in_mailbox
        if self.after:
            result['after'] = self.after.isoformat()
        if self.before:
            result['before'] = self.before.isoformat()
        if self.has_keyword:
            result['hasKeyword'] = self.has_keyword
        if self.not_keyword:
            result['notKeyword'] = self.not_keyword
        if self.min_size is not None:
            result['minSize'] = self.min_size
        if self.max_size is not None:
            result['maxSize'] = self.max_size
        if self.text:
            result['text'] = self.text
        if self.from_:
            result['from'] = self.from_
        if self.to:
            result['to'] = self.to
        if self.subject:
            result['subject'] = self.subject
        
        return result


@dataclass
class EmailSubmission:
    """Email submission status"""
    id: Optional[str] = None
    identity_id: Optional[str] = None
    email_id: Optional[str] = None
    thread_id: Optional[str] = None
    envelope: Optional[Dict] = None
    send_at: Optional[datetime] = None
    undo_status: str = 'final'
    delivery_status: Optional[Dict] = None
    dsn_blob_ids: List[str] = field(default_factory=list)
    mdn_blob_ids: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmailSubmission':
        """Create EmailSubmission from JMAP dictionary"""
        send_at = None
        if 'sendAt' in data:
            send_at = datetime.fromisoformat(data['sendAt'].replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            identity_id=data.get('identityId'),
            email_id=data.get('emailId'),
            thread_id=data.get('threadId'),
            envelope=data.get('envelope'),
            send_at=send_at,
            undo_status=data.get('undoStatus', 'final'),
            delivery_status=data.get('deliveryStatus'),
            dsn_blob_ids=data.get('dsnBlobIds', []),
            mdn_blob_ids=data.get('mdnBlobIds', [])
        )
