# JMAP Engine

Python library for viewing and sending emails through the JMAP protocol (RFC 8620, RFC 8621).

## Features

- ✅ Full JMAP Core Protocol (RFC 8620) support
- ✅ JMAP Mail Protocol (RFC 8621) support
- ✅ Email viewing and querying
- ✅ Email sending
- ✅ **Mailbox tree navigation** - Hierarchical mailbox browsing with recursive counts
- ✅ Mailbox management
- ✅ Session discovery and authentication
- ✅ Type-safe email models with dataclasses
- ✅ Bearer token support (Fastmail API keys)
- ✅ Easy-to-use Python API

## Installation

```bash
pip install jmap-engine
```

### From source

```bash
git clone https://github.com/cocdeshijie/jmap-engine.git
cd jmap-engine
pip install -e .
```

## Quick Start

### Connect to JMAP server

```python
from jmap_engine import JMAPClient

# Create client
client = JMAPClient(
    base_url='https://jmap.example.com',
    username='user@example.com',
    password='your-password'
)

# Connect and discover capabilities
client.connect()
```

### Or use as context manager

```python
with JMAPClient('https://jmap.example.com', 'user@example.com', 'password') as client:
    # Use client
    mailboxes = client.get_mailboxes()
    print(f"Found {len(mailboxes)} mailboxes")
```

### Check API key permissions

```python
with JMAPClient('https://api.fastmail.com', 'you@fastmail.com', 'api-key') as client:
    # Print formatted permissions report
    client.print_permissions()
    
    # Or get as dictionary for programmatic use
    perms = client.get_permissions()
    
    if 'urn:ietf:params:jmap:mail' in perms['capabilities']:
        print("✅ Can read emails")
    
    if 'urn:ietf:params:jmap:submission' in perms['capabilities']:
        print("✅ Can send emails")
    else:
        print("❌ Cannot send emails - need 'Write mail' permission")
```

**Example output:**
```
======================================================================
                 JMAP API Key Permissions
======================================================================

✅ Supported Features:
   • Core JMAP protocol
   • Email reading and management
   • Email sending
   • Contact management

👤 Accounts (1):
   • you@fastmail.com (Personal)
     ID: u12345
     Features:
       - Mail (max attachment: 50.0 MB)
       - Email sending

🔒 Permissions:
   ✅ 📧 Read emails
   ✅ 📤 Send emails
   ✅ 👥 Manage contacts
   ❌ 📅 Manage calendars
```

### View emails

```python
# Get all mailboxes
mailboxes = client.get_mailboxes()

# Find inbox
inbox = next((mb for mb in mailboxes if mb['role'] == 'inbox'), None)
if inbox:
    # Query emails in inbox
    email_ids = client.query_emails(
        filter={'inMailbox': inbox['id']},
        sort=[{'property': 'receivedAt', 'isAscending': False}],
        limit=20
    )
    
    # Fetch email details
    emails = client.get_emails(
        ids=email_ids,
        properties=['id', 'subject', 'from', 'receivedAt', 'preview']
    )
    
    # Print emails
    for email in emails:
        from_addr = email['from'][0] if email['from'] else {}
        print(f"From: {from_addr.get('name', from_addr.get('email'))}")
        print(f"Subject: {email['subject']}")
        print(f"Preview: {email.get('preview', '')[:100]}")
        print("---")
```

### Send an email

```python
from jmap_engine import Email, EmailAddress, EmailBodyPart

# Create email
email = Email(
    from_=[EmailAddress(email='sender@example.com', name='Sender Name')],
    to=[EmailAddress(email='recipient@example.com', name='Recipient')],
    subject='Hello from JMAP Engine!',
    text_body=[EmailBodyPart(
        type='text/plain',
        value='This is a test email sent via JMAP protocol.'
    )],
    html_body=[EmailBodyPart(
        type='text/html',
        value='<p>This is a <strong>test email</strong> sent via JMAP protocol.</p>'
    )]
)

# Send email
submission = client.send_email(email.to_dict())
print(f"Email sent! Submission ID: {submission.get('id')}")
```

### Navigate mailbox tree

```python
from jmap_engine import JMAPClient

with JMAPClient('https://api.fastmail.com', 'you@fastmail.com', 'api-key') as client:
    # Get mailbox tree
    tree = client.get_mailbox_tree()
    
    # Print tree structure
    tree.print_tree()
    # Output:
    # 📥 Inbox [150 total, 5 unread]
    #   └─ 📂 Projects [20 total, 2 unread]
    #      └─ 📂 2025 [10 total, 0 unread]
    # 📤 Sent [500 total, 0 unread]
    # 📝 Drafts [2 total, 0 unread]
    
    # Get inbox
    inbox = tree.get_by_role('inbox')
    print(f"Inbox: {inbox.total_emails} emails, {inbox.unread_emails} unread")
    
    # Get emails in inbox and all subfolders
    total_with_subs = inbox.get_total_emails_recursive()
    unread_with_subs = inbox.get_unread_emails_recursive()
    print(f"Including subfolders: {total_with_subs} total, {unread_with_subs} unread")
    
    # Navigate to subfolder
    projects = inbox.find_by_name('Projects')
    if projects:
        print(f"Projects path: {projects.path}")  # "Inbox/Projects"
        print(f"Has {len(projects.children)} subfolders")
    
    # Find by path
    mailbox = tree.find_by_path('Inbox/Projects/2025')
    
    # Get statistics
    stats = tree.get_statistics()
    print(f"{stats['total_mailboxes']} mailboxes, {stats['total_emails']} emails")
```

### Advanced querying

```python
from jmap_engine import EmailQuery
from datetime import datetime, timedelta

# Create query filter
query = EmailQuery(
    in_mailbox='inbox-id',
    after=datetime.now() - timedelta(days=7),  # Last 7 days
    has_keyword='$seen',  # Only read emails
    from_='important@example.com',
    min_size=1024  # Minimum 1KB
)

# Query emails
email_ids = client.query_emails(filter=query.to_dict(), limit=50)
emails = client.get_emails(ids=email_ids)

# Process emails
for email_data in emails:
    email = Email.from_dict(email_data)
    print(f"Subject: {email.subject}")
    print(f"Text: {email.get_text_content()[:200]}")
    print(f"Unread: {email.is_unread()}")
    print(f"Flagged: {email.is_flagged()}")
    print("---")
```

## Architecture

### Core Components

- **JMAPClient**: Main client class for JMAP operations
- **JMAPSession**: Session management and authentication
- **Email**: Email model with convenient methods
- **EmailQuery**: Email query filters
- **EmailSubmission**: Email submission status tracking

### Protocol Support

- ✅ RFC 8620 - JMAP Core Protocol
- ✅ RFC 8621 - JMAP for Mail
- 🔄 RFC 8887 - JMAP over WebSocket (planned)
- 🔄 RFC 9404 - JMAP Blob Management (planned)

## Development

### Setup development environment

```bash
git clone https://github.com/cocdeshijie/jmap-engine.git
cd jmap-engine
pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/
```

### Code formatting

```bash
black jmap_engine/
flake8 jmap_engine/
mypy jmap_engine/
```

## Examples

See the [examples/](examples/) directory for more usage examples:

- `basic_usage.py` - Basic email viewing and sending
- `advanced_query.py` - Advanced email querying
- `mailbox_management.py` - Managing mailboxes
- `attachment_handling.py` - Working with attachments

## JMAP Servers

Compatible JMAP servers include:

- **[Fastmail](https://www.fastmail.com/)** - Commercial email service (JMAP creators) - [See setup guide](FASTMAIL.md)
- [Cyrus IMAP](https://www.cyrusimap.org/) - Open source IMAP/JMAP server
- [Stalwart Mail Server](https://stalw.art/) - Modern mail server with JMAP support
- [Apache James](https://james.apache.org/) - Enterprise mail server

### Quick Fastmail Setup

```python
from jmap_engine import JMAPClient

# Get app password from: https://www.fastmail.com/settings/security/devicekeys/new
with JMAPClient('https://api.fastmail.com', 'you@fastmail.com', 'app-password') as client:
    mailboxes = client.get_mailboxes()
    print(f"Connected! Found {len(mailboxes)} mailboxes")
```

See [FASTMAIL.md](FASTMAIL.md) for complete Fastmail setup guide.

## Resources

- [JMAP Specification](https://jmap.io/)
- [RFC 8620 - JMAP Core](https://tools.ietf.org/html/rfc8620)
- [RFC 8621 - JMAP Mail](https://tools.ietf.org/html/rfc8621)
- [JMAP Community](https://jmap.io/#community)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built according to JMAP specifications from [jmap.io](https://jmap.io/)
- Inspired by the need for a modern, Pythonic JMAP library
- Thanks to the JMAP working group for creating an excellent protocol

## Support

- 🐛 [Report bugs](https://github.com/cocdeshijie/jmap-engine/issues)
- 💬 [Discussions](https://github.com/cocdeshijie/jmap-engine/discussions)
- 📧 Contact: [Open an issue](https://github.com/cocdeshijie/jmap-engine/issues/new)
