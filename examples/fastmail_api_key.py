"""
JMAP Engine - Fastmail API Key Example

Using Fastmail API keys (Bearer token authentication)
"""

from jmap_engine import JMAPClient, Email, EmailAddress, EmailBodyPart


def main():
    # Fastmail API Key configuration
    BASE_URL = 'https://api.fastmail.com'
    
    # API key (starts with 'fmu') - generate at:
    # https://app.fastmail.com/settings/security/tokens
    API_KEY = 'fmu1-your-api-key-here'
    
    # Note: With API keys, username is ignored but we pass email for reference
    USERNAME = 'your-email@fastmail.com'
    
    print("Connecting to Fastmail with API key...")
    print("Note: API keys use Bearer token authentication\n")
    
    try:
        # The library auto-detects Bearer token if password starts with 'fmu'
        with JMAPClient(BASE_URL, USERNAME, API_KEY) as client:
            print("✓ Connected successfully with API key!")
            
            # Display account info
            account_id = client.session.get_account_id()
            print(f"👤 Account ID: {account_id}")
            
            # List mailboxes
            print("\n📁 Mailboxes:")
            mailboxes = client.get_mailboxes()
            
            for mailbox in mailboxes:
                role = mailbox.get('role', 'custom')
                name = mailbox.get('name', 'Unknown')
                total = mailbox.get('totalEmails', 0)
                unread = mailbox.get('unreadEmails', 0)
                
                icon = {
                    'inbox': '📥',
                    'sent': '📤',
                    'drafts': '📝',
                    'trash': '🗑️',
                    'spam': '🚫',
                    'archive': '📦'
                }.get(role, '📂')
                
                print(f"   {icon} {name:20} - {total} total, {unread} unread")
            
            # Find inbox
            inbox = next((mb for mb in mailboxes if mb.get('role') == 'inbox'), None)
            
            if inbox:
                # Query recent emails
                print(f"\n📧 Recent emails from Inbox:")
                email_ids = client.query_emails(
                    filter={'inMailbox': inbox['id']},
                    sort=[{'property': 'receivedAt', 'isAscending': False}],
                    limit=5
                )
                
                if email_ids:
                    emails = client.get_emails(
                        ids=email_ids,
                        properties=['id', 'subject', 'from', 'receivedAt', 'preview', 'keywords']
                    )
                    
                    for i, email_data in enumerate(emails, 1):
                        email = Email.from_dict(email_data)
                        
                        from_name = email.from_[0].name if email.from_ and email.from_[0].name else "Unknown"
                        from_email = email.from_[0].email if email.from_ else ""
                        
                        status = "📩" if email.is_unread() else "✓"
                        flag = " 🚩" if email.is_flagged() else ""
                        
                        print(f"\n   {i}. {status}{flag} {email.subject}")
                        print(f"      From: {from_name} <{from_email}>")
                        print(f"      Date: {email.received_at}")
                        print(f"      Preview: {email_data.get('preview', '')[:80]}...")
                else:
                    print("   No emails found")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n💡 Tips for API Keys:")
        print("   1. Generate an API token at: https://app.fastmail.com/settings/security/tokens")
        print("   2. Click 'New API token'")
        print("   3. Name: 'JMAP Engine'")
        print("   4. Permissions: Select 'Read mail', 'Write mail', etc.")
        print("   5. Copy the token (starts with 'fmu1-')")
        print("   6. The token is auto-detected as Bearer auth by the library")


if __name__ == '__main__':
    print("=" * 60)
    print("     JMAP Engine - Fastmail API Key Example")
    print("=" * 60)
    print("\n🔑 Using Fastmail API Keys (Bearer Token Auth)")
    print("   Generate at: https://app.fastmail.com/settings/security/tokens\n")
    
    main()
