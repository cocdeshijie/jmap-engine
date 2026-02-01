# JMAP Engine Use Cases

**Real-world examples of using JMAP Engine for API-driven email automation**

JMAP Engine is designed for **programmatic email access**, not end-user email reading. Here are practical examples of what you can build:

---

## 🤖 Email Automation

### Auto-Reply Bot
```python
"""
Automatically reply to emails with specific subjects.
"""
from jmap_engine import JMAPClient, Email, EmailAddress, EmailBodyPart

with JMAPClient('https://api.fastmail.com', 'bot@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    # Query unread emails
    email_ids = client.query_emails(
        filter={
            'inMailbox': inbox.id,
            'hasKeyword': '$seen',
            'not': True  # Unread only
        }
    )
    
    emails = client.get_emails(ids=email_ids)
    
    for email_data in emails:
        email = Email.from_dict(email_data)
        
        # Auto-reply to support emails
        if 'support' in email.subject.lower():
            reply = Email(
                from_=[EmailAddress(email='bot@example.com', name='Support Bot')],
                to=email.from_,
                subject=f"Re: {email.subject}",
                in_reply_to=email.message_id,
                text_body=[EmailBodyPart(
                    type='text/plain',
                    value='Thank you for contacting support. A human will respond within 24 hours.'
                )]
            )
            client.send_email(reply.to_dict())
```

---

## 🔔 Email Monitoring & Alerts

### Slack Notification Bridge
```python
"""
Send Slack notification when important emails arrive.
"""
import requests

with JMAPClient('https://api.fastmail.com', 'monitor@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    # Query recent unread emails
    email_ids = client.query_emails(
        filter={
            'inMailbox': inbox.id,
            'notKeyword': '$seen',
            'from': 'important@example.com'  # Monitor specific sender
        },
        limit=10
    )
    
    emails = client.get_emails(ids=email_ids)
    
    for email_data in emails:
        email = Email.from_dict(email_data)
        
        # Send Slack notification
        requests.post('https://hooks.slack.com/services/YOUR/WEBHOOK/URL', json={
            'text': f"📧 New email from {email.from_[0].name}",
            'attachments': [{
                'title': email.subject,
                'text': email.get_text_content()[:200],
                'color': 'good'
            }]
        })
```

---

## 📊 Email Analytics

### Daily Email Report
```python
"""
Generate daily email statistics report.
"""
from datetime import datetime, timedelta
from collections import Counter

with JMAPClient('https://api.fastmail.com', 'analytics@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    # Query last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    email_ids = client.query_emails(
        filter={
            'inMailbox': inbox.id,
            'after': yesterday.isoformat()
        }
    )
    
    emails = client.get_emails(ids=email_ids, properties=['from', 'subject', 'receivedAt'])
    
    # Analyze
    total = len(emails)
    senders = Counter([e['from'][0]['email'] for e in emails if e.get('from')])
    
    print(f"📊 Daily Email Report - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Total emails: {total}")
    print(f"\nTop Senders:")
    for sender, count in senders.most_common(5):
        print(f"  {sender}: {count} emails")
```

---

## 🔗 Integration Examples

### CRM Integration
```python
"""
Sync emails to CRM system.
"""
import requests

with JMAPClient('https://api.fastmail.com', 'crm@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    email_ids = client.query_emails(
        filter={'inMailbox': inbox.id},
        limit=50
    )
    
    emails = client.get_emails(ids=email_ids)
    
    for email_data in emails:
        email = Email.from_dict(email_data)
        
        # Send to CRM API
        requests.post('https://crm.example.com/api/emails', json={
            'from': email.from_[0].email,
            'subject': email.subject,
            'body': email.get_text_content(),
            'date': email.received_at.isoformat()
        })
```

---

## 📝 Content Processing

### Extract Invoice Data
```python
"""
Extract invoice information from emails and save to database.
"""
import re
import sqlite3

with JMAPClient('https://api.fastmail.com', 'invoices@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    # Find invoice emails
    email_ids = client.query_emails(
        filter={
            'inMailbox': inbox.id,
            'subject': 'invoice'  # Contains "invoice"
        }
    )
    
    emails = client.get_emails(ids=email_ids)
    
    db = sqlite3.connect('invoices.db')
    
    for email_data in emails:
        email = Email.from_dict(email_data)
        text = email.get_text_content()
        
        # Extract invoice number and amount (example regex)
        invoice_match = re.search(r'Invoice #(\d+)', text)
        amount_match = re.search(r'\$([0-9,]+\.\d{2})', text)
        
        if invoice_match and amount_match:
            invoice_num = invoice_match.group(1)
            amount = amount_match.group(1)
            
            db.execute(
                'INSERT INTO invoices (number, amount, sender, date) VALUES (?, ?, ?, ?)',
                (invoice_num, amount, email.from_[0].email, email.received_at)
            )
    
    db.commit()
```

---

## 🔄 Email Backup

### Archive to JSON
```python
"""
Backup emails to JSON files.
"""
import json
from pathlib import Path

with JMAPClient('https://api.fastmail.com', 'backup@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    
    # Backup all mailboxes
    for mailbox in tree.get_all_mailboxes():
        email_ids = client.query_emails(
            filter={'inMailbox': mailbox.id}
        )
        
        if not email_ids:
            continue
        
        emails = client.get_emails(ids=email_ids)
        
        # Save to file
        backup_dir = Path('email_backup') / mailbox.name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for email_data in emails:
            email_id = email_data['id']
            with open(backup_dir / f'{email_id}.json', 'w') as f:
                json.dump(email_data, f, indent=2)
        
        print(f"✓ Backed up {len(emails)} emails from {mailbox.name}")
```

---

## 🧪 Testing & QA

### Email Verification in Tests
```python
"""
Verify emails were sent during automated tests.
"""
import pytest
from jmap_engine import JMAPClient

@pytest.fixture
def email_client():
    with JMAPClient('https://api.fastmail.com', 'test@example.com', API_KEY) as client:
        yield client

def test_welcome_email_sent(email_client):
    """Test that welcome email was sent to new user."""
    tree = email_client.get_mailbox_tree()
    sent = tree.get_by_role('sent')
    
    # Query recent sent emails
    email_ids = email_client.query_emails(
        filter={
            'inMailbox': sent.id,
            'to': 'newuser@example.com',
            'subject': 'Welcome'
        },
        limit=1
    )
    
    assert len(email_ids) > 0, "Welcome email was not sent"
    
    emails = email_client.get_emails(ids=email_ids)
    assert 'welcome' in emails[0]['textBody'][0]['value'].lower()
```

---

## 📤 Bulk Operations

### Mass Email Categorization
```python
"""
Automatically categorize and move emails to folders.
"""
from jmap_engine import JMAPClient

with JMAPClient('https://api.fastmail.com', 'organize@example.com', API_KEY) as client:
    tree = client.get_mailbox_tree()
    inbox = tree.get_by_role('inbox')
    
    # Create/find category mailboxes
    newsletters = tree.find_by_path('Newsletters') or tree.get_by_name('Newsletters')
    receipts = tree.find_by_path('Receipts') or tree.get_by_name('Receipts')
    
    email_ids = client.query_emails(
        filter={'inMailbox': inbox.id},
        limit=100
    )
    
    emails = client.get_emails(ids=email_ids, properties=['id', 'from', 'subject'])
    
    for email in emails:
        # Categorize by sender/subject
        sender = email['from'][0]['email'].lower()
        subject = email['subject'].lower()
        
        target_mailbox = None
        
        if 'unsubscribe' in subject or 'newsletter' in subject:
            target_mailbox = newsletters.id
        elif 'receipt' in subject or 'invoice' in subject:
            target_mailbox = receipts.id
        
        if target_mailbox:
            # Move email (update mailboxIds)
            client.make_request([
                ['Email/set', {
                    'accountId': client.session.get_account_id(),
                    'update': {
                        email['id']: {
                            'mailboxIds': {target_mailbox: True}
                        }
                    }
                }, 'c1']
            ])
```

---

## 🎯 Key Takeaway

JMAP Engine is for **building tools that interact with email**, not for reading email yourself.

If you're:
- 🧑‍💻 Writing code that processes emails → ✅ Use JMAP Engine
- 👤 Just reading your personal email → ❌ Use a proper email client

For more examples, see the [`examples/`](examples/) directory in the repository.
