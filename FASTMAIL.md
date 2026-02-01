# Using JMAP Engine with Fastmail

Fastmail is one of the creators of JMAP and has full JMAP support!

## Setup

### 1. Generate App Password

1. Go to Fastmail Settings: https://www.fastmail.com/settings/security/devicekeys/new
2. Name: "JMAP Engine" (or whatever you like)
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

```bash
cd examples
python fastmail_example.py
```

Or use it in your code:

```python
from jmap_engine import JMAPClient

BASE_URL = 'https://api.fastmail.com'
USERNAME = 'your-email@fastmail.com'
PASSWORD = 'your-app-password'  # From step 1

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
- **Username**: Your full Fastmail email (e.g., `user@fastmail.com`)
- **Password**: App password (NOT your main password!)

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
