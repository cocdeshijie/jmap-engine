# JMAP Engine

Python library for email automation via JMAP protocol (RFC 8620, RFC 8621).

Build bots, integrations, and automation tools for email. Works with Fastmail, Cyrus, Stalwart, and other JMAP servers.

## Installation

```bash
pip install jmap-engine
```

## Quick Start

```python
from jmap_engine import JMAPClient, Email, EmailAddress, EmailBodyPart

# Connect (auto-detects Fastmail API keys starting with 'fmu')
client = JMAPClient(
    base_url='https://api.fastmail.com',
    username='you@fastmail.com',
    password='fmu1-your-api-key'
)
client.connect()

# List mailboxes
mailboxes = client.get_mailboxes()
for mb in mailboxes:
    print(f"{mb['name']}: {mb.get('totalEmails', 0)} emails")

# Get inbox emails
inbox = next((mb for mb in mailboxes if mb['role'] == 'inbox'), None)
email_ids = client.query_emails(
    filter={'inMailbox': inbox['id']},
    limit=10
)
emails = client.get_emails(email_ids, properties=['subject', 'from', 'preview'])
for email in emails:
    print(f"{email['subject']} - {email['from'][0]['email']}")

# Send email
email = Email(
    from_=[EmailAddress(email='you@fastmail.com', name='Your Name')],
    to=[EmailAddress(email='recipient@example.com')],
    subject='Test Email',
    text_body=[EmailBodyPart(type='text/plain', value='Hello!')],
    html_body=[EmailBodyPart(type='text/html', value='<p>Hello!</p>')]
)
submission = client.send_email(email.to_dict())
print(f"Sent! ID: {submission['id']}")
```

## Features

**Core Operations:**
- View and query emails with filters
- Send emails (auto-detects sender identity)
- Manage mailboxes and folders
- Navigate mailbox hierarchies

**JMAP Protocol:**
- RFC 8620 (JMAP Core)
- RFC 8621 (JMAP Mail)
- Bearer token auth (Fastmail API keys)
- Session discovery

## Common Operations

### Get Available Identities

```python
identities = client.get_identities()
for identity in identities:
    print(f"{identity['name']} <{identity['email']}>")
```

### Query Emails with Filters

```python
from jmap_engine import EmailQuery
from datetime import datetime, timedelta

query = EmailQuery(
    in_mailbox='inbox-id',
    after=datetime.now() - timedelta(days=7),
    has_keyword='$seen',
    from_='important@example.com'
)
email_ids = client.query_emails(filter=query.to_dict(), limit=50)
```

### Navigate Mailbox Tree

```python
tree = client.get_mailbox_tree()
tree.print_tree()
# Output:
# 📥 Inbox [150 total, 5 unread]
#   └─ 📂 Projects [20 total, 2 unread]

inbox = tree.get_by_role('inbox')
print(f"{inbox.total_emails} emails, {inbox.unread_emails} unread")
```

### Check API Key Permissions

```python
client.print_permissions()
# Shows what your API key can access:
# ✅ CAN 📧 Read emails
# ✅ CAN 📤 Send emails
# ❌ CANNOT 📅 Manage calendars
```

## Fastmail Setup

1. Generate API token: https://app.fastmail.com/settings/security/tokens
2. Select permissions (Read mail, Write mail, etc.)
3. Copy token (starts with `fmu1-`)

```python
client = JMAPClient(
    base_url='https://api.fastmail.com',
    username='you@fastmail.com',
    password='fmu1-your-token'  # Auto-detected as Bearer auth
)
```

## Use Cases

- **Automation:** Auto-respond, filter, organize emails
- **Bots:** Process incoming emails, extract data
- **Integrations:** Connect email to Slack, Discord, databases
- **Analytics:** Analyze patterns, extract metrics
- **Monitoring:** Trigger alerts for specific emails
- **Backup:** Archive emails to JSON/database
- **Testing:** Verify emails in test suites

## API Reference

### JMAPClient

```python
client = JMAPClient(base_url, username, password, timeout=30)
client.connect()  # Discover session

# Mailboxes
mailboxes = client.get_mailboxes(account_id=None)
tree = client.get_mailbox_tree(account_id=None)

# Identities
identities = client.get_identities(account_id=None)

# Query emails
email_ids = client.query_emails(filter=None, sort=None, limit=None, account_id=None)

# Get emails
emails = client.get_emails(ids, properties=None, account_id=None)

# Send email
submission = client.send_email(email_dict, identity_id=None, account_id=None)

# Permissions
perms = client.get_permissions()
client.print_permissions()
```

### Email Models

```python
from jmap_engine import Email, EmailAddress, EmailBodyPart, EmailQuery

# Create email
email = Email(
    from_=[EmailAddress(email='sender@example.com', name='Sender')],
    to=[EmailAddress(email='recipient@example.com')],
    cc=[...],
    bcc=[...],
    subject='Subject',
    text_body=[EmailBodyPart(type='text/plain', value='Text content')],
    html_body=[EmailBodyPart(type='text/html', value='<p>HTML</p>')],
    mailbox_ids={'mailbox-id': True},  # Optional, auto-detects Sent folder
    keywords={'$seen': True, '$flagged': True}
)

# Use email
email_dict = email.to_dict()
email_obj = Email.from_dict(email_dict)
text = email.get_text_content()
is_unread = email.is_unread()
```

## JMAP Servers

- **[Fastmail](https://fastmail.com)** - Commercial (JMAP creators)
- [Cyrus IMAP](https://cyrusimap.org) - Open source
- [Stalwart](https://stalw.art) - Modern open source
- [Apache James](https://james.apache.org) - Enterprise

## Development

```bash
git clone https://github.com/cocdeshijie/jmap-engine.git
cd jmap-engine
pip install -e ".[dev]"
pytest tests/
```

## Resources

- [JMAP Spec](https://jmap.io/)
- [RFC 8620 - JMAP Core](https://tools.ietf.org/html/rfc8620)
- [RFC 8621 - JMAP Mail](https://tools.ietf.org/html/rfc8621)

## License

MIT - see [LICENSE](LICENSE)
