# Using JMAP Engine with Fastmail

Fastmail is one of the creators of JMAP and has full JMAP support!

> 🔑 **This guide is for API/programmatic access via Fastmail API keys.**  
> For regular email reading in a GUI, use [Fastmail's web interface](https://www.fastmail.com/),  
> [Thunderbird](https://www.thunderbird.net/), or [Apple Mail](https://support.apple.com/mail).  
>  
> **Use JMAP Engine to build:** email automation, bots, integrations, monitoring tools, and custom scripts.

## Setup

You have two authentication options:

### Option 1: API Key (Recommended)

**Best for programmatic access with fine-grained permissions**

1. Go to Fastmail API Tokens: https://app.fastmail.com/settings/security/tokens
2. Click **"New API token"**
3. Name: "JMAP Engine"
4. Permissions: Select what you need:
   - ✅ **Read mail** - View emails
   - ✅ **Write mail** - Send emails, modify flags
   - ✅ **Manage mail** - Delete, move emails
5. Click **"Generate"**
6. **Copy the API key** (starts with `fmu1-`) - you won't see it again!

### Option 2: App Password

**Simpler but full access to your account**

1. Go to Fastmail Settings: https://www.fastmail.com/settings/security/devicekeys/new
2. Name: "JMAP Engine"
3. Scope: Select **"IMAP/SMTP"** or **"Custom"**
4. Click **"Generate password"**
5. **Copy the password** - you won't see it again!

### 2. Install JMAP Engine

```bash
git clone https://github.com/cocdeshijie/jmap-engine.git
cd jmap-engine
pip install -e .
```

### 3. Run the Example

**With API Key:**
```bash
cd examples
python fastmail_api_key.py
```

**With App Password:**
```bash
cd examples
python fastmail_example.py
```

Or use it in your code:

**Using API Key (auto-detected):**
```python
from jmap_engine import JMAPClient

BASE_URL = 'https://api.fastmail.com'
API_KEY = 'fmu1-your-api-key-here'  # From Fastmail API tokens
USERNAME = 'your-email@fastmail.com'  # Not used with API keys, but helpful for reference

# API keys starting with 'fmu' are auto-detected as Bearer tokens
with JMAPClient(BASE_URL, USERNAME, API_KEY) as client:
    mailboxes = client.get_mailboxes()
    print(f"Found {len(mailboxes)} mailboxes")
```

**Using App Password (Basic auth):**
```python
from jmap_engine import JMAPClient

BASE_URL = 'https://api.fastmail.com'
USERNAME = 'your-email@fastmail.com'
PASSWORD = 'your-app-password'  # From app passwords

with JMAPClient(BASE_URL, USERNAME, PASSWORD) as client:
    # Get mailboxes
    mailboxes = client.get_mailboxes()
    print(f"Found {len(mailboxes)} mailboxes")
    
    # Query inbox
    inbox = next(mb for mb in mailboxes if mb['role'] == 'inbox')
    email_ids = client.query_emails(
        filter={'inMailbox': inbox['id']},
        limit=10
    )
    
    # Get emails
    emails = client.get_emails(ids=email_ids)
    for email_data in emails:
        print(f"Subject: {email_data['subject']}")
```

## Configuration Details

### Base URL
```python
BASE_URL = 'https://api.fastmail.com'
```

### Authentication

The library automatically detects the authentication method:

**API Key (Bearer Token):**
- API keys start with `fmu1-` or `fmu-`
- Automatically uses Bearer token authentication
- Username is ignored (but can be passed for reference)
- More secure with fine-grained permissions

**App Password (Basic Auth):**
- Regular app password (any other format)
- Uses HTTP Basic authentication
- Requires your full Fastmail email as username
- Full account access

**Auto-detection:**
```python
# This uses Bearer token (auto-detected)
client = JMAPClient(
    'https://api.fastmail.com',
    'you@fastmail.com',
    'fmu1-abc123...'  # Starts with 'fmu' → Bearer auth
)

# This uses Basic auth
client = JMAPClient(
    'https://api.fastmail.com',
    'you@fastmail.com',
    'regular-app-password'  # Not 'fmu' → Basic auth
)

# Explicit Bearer token (if needed)
client = JMAPClient(
    'https://api.fastmail.com',
    'you@fastmail.com',
    'your-token',
    use_bearer_token=True
)
```

### Session Discovery
The library automatically discovers JMAP endpoints via:
```
https://api.fastmail.com/.well-known/jmap
```

## Capabilities

Fastmail supports these JMAP capabilities:

- ✅ `urn:ietf:params:jmap:core` - Core protocol
- ✅ `urn:ietf:params:jmap:mail` - Email
- ✅ `urn:ietf:params:jmap:submission` - Email sending
- ✅ `urn:ietf:params:jmap:contacts` - Contacts (CardDAV)
- ✅ `urn:ietf:params:jmap:calendars` - Calendars (CalDAV)
- ✅ `https://www.fastmail.com/dev/maskedemail` - Masked email (Fastmail-specific)

## Common Tasks

### View Recent Emails
```python
with JMAPClient('https://api.fastmail.com', username, password) as client:
    mailboxes = client.get_mailboxes()
    inbox = next(mb for mb in mailboxes if mb['role'] == 'inbox')
    
    email_ids = client.query_emails(
        filter={'inMailbox': inbox['id']},
        sort=[{'property': 'receivedAt', 'isAscending': False}],
        limit=20
    )
    
    emails = client.get_emails(
        ids=email_ids,
        properties=['id', 'subject', 'from', 'receivedAt', 'preview']
    )
    
    for email in emails:
        print(f"{email['subject']} - {email['from'][0]['name']}")
```

### Send Email
```python
from jmap_engine import Email, EmailAddress, EmailBodyPart

email = Email(
    from_=[EmailAddress(email='you@fastmail.com', name='Your Name')],
    to=[EmailAddress(email='recipient@example.com')],
    subject='Hello from JMAP!',
    text_body=[EmailBodyPart(
        type='text/plain',
        value='Email body text here'
    )]
)

with JMAPClient('https://api.fastmail.com', username, password) as client:
    submission = client.send_email(email.to_dict())
    print(f"Sent! ID: {submission['id']}")
```

### Search Emails
```python
from jmap_engine import EmailQuery
from datetime import datetime, timedelta

# Search last 7 days
query = EmailQuery(
    in_mailbox=inbox_id,
    after=datetime.now() - timedelta(days=7),
    subject='important'  # Search in subject
)

email_ids = client.query_emails(filter=query.to_dict())
```

## Troubleshooting

### "HTTP 401: Bad credentials"
- Make sure you're using an **App Password**, not your main Fastmail password
- Regenerate the app password if needed

### "No such capability"
- Fastmail supports all standard JMAP features
- Check `client.session.capabilities` to see available capabilities

### Rate Limiting
Fastmail has generous rate limits for JMAP:
- Personal: ~1000 requests/hour
- Business: Higher limits

### Connection Issues
```python
# Increase timeout if needed
client = JMAPClient(
    'https://api.fastmail.com',
    username,
    password,
    timeout=60  # Increase from default 30s
)
```

## Resources

- [Fastmail JMAP API Docs](https://www.fastmail.com/developer/)
- [Fastmail App Passwords](https://www.fastmail.com/settings/security/devicekeys)
- [JMAP Specification](https://jmap.io/)

## Example Output

```
Connecting to Fastmail JMAP server...
✓ Connected successfully!

📋 Server Capabilities:
   - urn:ietf:params:jmap:core
   - urn:ietf:params:jmap:mail
   - urn:ietf:params:jmap:submission
   ...

👤 Account ID: u12345678

📁 Mailboxes:
   📥 Inbox                - 150 total, 5 unread
   📤 Sent                 - 500 total, 0 unread
   📝 Drafts               - 2 total, 0 unread
   🗑️  Trash                - 10 total, 0 unread

📧 Recent emails from Inbox:
   1. 📩 Important Update from Team
      From: Alice <alice@example.com>
      Date: 2026-02-01 12:30:00+00:00
      Preview: Hi there! Just wanted to update you on...
```

## Support

- GitHub Issues: https://github.com/cocdeshijie/jmap-engine/issues
- Fastmail Help: https://www.fastmail.com/help/
