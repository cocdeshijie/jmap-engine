"""
JMAP Engine - Fastmail Example

Fastmail is one of the creators of JMAP and has full support.
"""

from jmap_engine import JMAPClient, Email, EmailAddress, EmailBodyPart


def main():
    # Fastmail JMAP configuration
    BASE_URL = 'https://api.fastmail.com'
    USERNAME = 'your-email@fastmail.com'  # Your Fastmail email
    PASSWORD = 'your-app-password'  # Generate at Settings > Password & Security > App Passwords
    
    print("Connecting to Fastmail JMAP server...")
    
    try:
        with JMAPClient(BASE_URL, USERNAME, PASSWORD) as client:
            print("✓ Connected successfully!")
            
            # Display capabilities
            print("\n📋 Server Capabilities:")
            for capability in client.session.capabilities.keys():
                print(f"   - {capability}")
            
            # Get account info
            account_id = client.session.get_account_id()
            print(f"\n👤 Account ID: {account_id}")
            
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
            
            # Optional: Send a test email
            send = input("\n\n📨 Send a test email? (y/N): ")
            if send.lower() == 'y':
                recipient = input("Recipient email: ")
                
                email = Email(
                    from_=[EmailAddress(email=USERNAME, name='JMAP Test')],
                    to=[EmailAddress(email=recipient)],
                    subject='Test from JMAP Engine',
                    text_body=[EmailBodyPart(
                        type='text/plain',
                        value='This is a test email sent via Fastmail JMAP using jmap-engine!'
                    )],
                    html_body=[EmailBodyPart(
                        type='text/html',
                        value='<p>This is a <strong>test email</strong> sent via Fastmail JMAP using <code>jmap-engine</code>!</p>'
                    )]
                )
                
                print("\nSending email...")
                submission = client.send_email(email.to_dict())
                print(f"✓ Email sent! Submission ID: {submission.get('id', 'N/A')}")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n💡 Tips:")
        print("   1. Make sure you're using an App Password (not your main password)")
        print("   2. Generate one at: https://www.fastmail.com/settings/security/devicekeys/new")
        print("   3. Select 'IMAP/SMTP' or 'Custom' scope")
        print("   4. Use your full Fastmail email as username")


if __name__ == '__main__':
    print("=" * 60)
    print("        JMAP Engine - Fastmail Example")
    print("=" * 60)
    print("\n⚠️  You need a Fastmail App Password!")
    print("   Generate at: https://www.fastmail.com/settings/security/devicekeys/new\n")
    
    main()
