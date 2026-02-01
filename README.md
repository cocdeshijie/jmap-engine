# JMAP Engine

**Python library for programmatic email access via JMAP API**

[![For Developers](https://img.shields.io/badge/For-Developers-blue?style=for-the-badge)](https://github.com/cocdeshijie/jmap-engine)
[![API Access](https://img.shields.io/badge/API-Access-green?style=for-the-badge)](https://github.com/cocdeshijie/jmap-engine)
[![Not a Client](https://img.shields.io/badge/Not%20a-Email%20Client-red?style=for-the-badge)](https://github.com/cocdeshijie/jmap-engine)

Build email automation, integrations, and tools using the modern JMAP protocol (RFC 8620, RFC 8621).

> 🔧 **For Developers:** API/programmatic email access  
> 🤖 **Use For:** Bots, automation, integrations, monitoring, analytics  
> ❌ **Not For:** Reading personal email (use Thunderbird, Apple Mail, etc.)
> 
> **Think of it as:** Python SDK for JMAP email servers (like `requests` is for HTTP APIs)

## What is JMAP Engine?

JMAP Engine is a **Python library for developers** to programmatically access email via the JMAP API protocol. Think of it as a Python SDK for JMAP servers.

### ✅ Use JMAP Engine to build:
- 📧 **Email automation** - Auto-respond, filter, organize emails
- 🤖 **Email bots** - Process incoming emails, extract data
- 🔗 **Integrations** - Connect email to Slack, Discord, databases, etc.
- 📊 **Analytics tools** - Analyze email patterns, extract metrics
- 🔔 **Notification systems** - Monitor specific emails, trigger alerts
- 📝 **Backup scripts** - Download and archive emails
- 🧪 **Testing tools** - Send/verify emails in test suites
- 📤 **Bulk operations** - Mass email management

### ❌ NOT for:
- 📮 End-user email reading (use Thunderbird, Apple Mail, etc.)
- 🖥️ Building a desktop email client (use existing IMAP/JMAP clients)

### 🔑 Designed for API Keys
JMAP Engine is optimized for **Fastmail API keys** and similar token-based authentication:
- Automatic Bearer token detection
- Permission checking (`client.print_permissions()`)
- Scoped access (read-only, write-only, etc.)

---

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
- ✅ Permission checking
- ✅ Easy-to-use Python API

## Who is this for?

| You are... | Use JMAP Engine? |
|------------|------------------|
| 🧑‍💻 **Developer** building email automation | ✅ YES - This is for you! |
| 🤖 Building bots, scripts, or integrations | ✅ YES - Perfect use case |
| 🔧 Need programmatic email access via API | ✅ YES - That's what it does |
| 📊 Building analytics or monitoring tools | ✅ YES - Read/process emails via API |
| 👤 **End user** who wants to read emails | ❌ NO - Use Thunderbird/Apple Mail |
| 🖥️ Building a desktop email client | ❌ NO - Use existing clients |

---

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

### 1. Get a Fastmail API Key

Generate an API token at: https://app.fastmail.com/settings/security/tokens

- Name: "My Email Bot"
- Permissions: Select what you need (Read mail, Write mail, etc.)
- Copy the token (starts with `fmu1-`)

### 2. Connect and use the API

```python
from jmap_engine import JMAPClient

# Create client with API key (recommended)
client = JMAPClient(
    base_url='https://api.fastmail.com',
    username='you@fastmail.com',  # Your email (for reference)
    password='fmu1-your-api-key'  # API key - auto-detected as Bearer token
)

# Connect and discover capabilities
client.connect()

# Check what your API key can do
client.print_permissions()
```

> 💡 **API keys starting with `fmu` are automatically detected** as Bearer tokens.  
> You can also use app passwords (Basic auth), but API keys are recommended for better security.

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

💡 This shows what YOUR API KEY can do (not account properties).
   The permissions below reflect your API token's scope.

✅ API Key Has Access To:
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

🌟 Primary Accounts:
   • Mail, Contacts: you@fastmail.com

🔑 What This API Key Can Do:
   ✅ CAN 📧 Read emails
   ✅ CAN 📤 Send emails
   ✅ CAN 👥 Manage contacts
   ❌ CANNOT 📅 Manage calendars
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

## Real-World Use Cases

Want to see what you can build with JMAP Engine? Check out **[USECASES.md](USECASES.md)** for practical examples:

- 🤖 **Auto-reply bots** - Respond to support emails automatically
- 🔔 **Email monitoring** - Send Slack notifications for important emails
- 📊 **Analytics** - Generate daily email reports and statistics
- 🔗 **CRM integration** - Sync emails to your CRM system
- 📝 **Invoice extraction** - Parse and save invoice data to database
- 🔄 **Email backup** - Archive emails to JSON/database
- 🧪 **Testing** - Verify emails in automated tests
- 📤 **Bulk operations** - Auto-categorize and organize emails

→ **[See all examples in USECASES.md](USECASES.md)**

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
