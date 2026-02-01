"""
Basic JMAP Engine usage example
"""

from jmap_engine import JMAPClient, Email, EmailAddress, EmailBodyPart


def main():
    # Configuration
    BASE_URL = 'https://jmap.example.com'
    USERNAME = 'user@example.com'
    PASSWORD = 'your-password'
    
    # Create and connect client
    with JMAPClient(BASE_URL, USERNAME, PASSWORD) as client:
        print("✓ Connected to JMAP server")
        
        # Get mailboxes
        print("\nFetching mailboxes...")
        mailboxes = client.get_mailboxes()
        
        for mailbox in mailboxes:
            role = mailbox.get('role', 'custom')
            name = mailbox.get('name', 'Unknown')
            total = mailbox.get('totalEmails', 0)
            unread = mailbox.get('unreadEmails', 0)
            print(f"  [{role:10}] {name:20} - {total} total, {unread} unread")
        
        # Find inbox
        inbox = next((mb for mb in mailboxes if mb.get('role') == 'inbox'), None)
        
        if inbox:
            print(f"\n✓ Found inbox: {inbox['name']} (ID: {inbox['id']})")
            
            # Query recent emails
            print("\nQuerying recent emails...")
            email_ids = client.query_emails(
                filter={'inMailbox': inbox['id']},
                sort=[{'property': 'receivedAt', 'isAscending': False}],
                limit=5
            )
            
            print(f"✓ Found {len(email_ids)} emails")
            
            # Fetch email details
            if email_ids:
                print("\nFetching email details...")
                emails = client.get_emails(
                    ids=email_ids,
                    properties=['id', 'subject', 'from', 'receivedAt', 'preview', 'keywords']
                )
                
                for i, email_data in enumerate(emails, 1):
                    email = Email.from_dict(email_data)
                    
                    from_name = email.from_[0].name if email.from_ and email.from_[0].name else "Unknown"
                    from_email = email.from_[0].email if email.from_ else "unknown@example.com"
                    
                    status = "📩 UNREAD" if email.is_unread() else "✓ Read"
                    flag = " 🚩" if email.is_flagged() else ""
                    
                    print(f"\n{i}. {status}{flag}")
                    print(f"   From: {from_name} <{from_email}>")
                    print(f"   Subject: {email.subject}")
                    print(f"   Date: {email.received_at}")
                    print(f"   Preview: {email_data.get('preview', '')[:100]}...")
        
        # Example: Send an email
        send_example = input("\n\nWould you like to send a test email? (y/N): ")
        
        if send_example.lower() == 'y':
            recipient = input("Recipient email: ")
            
            # Create email
            email = Email(
                from_=[EmailAddress(email=USERNAME, name='JMAP Test')],
                to=[EmailAddress(email=recipient)],
                subject='Test email from JMAP Engine',
                text_body=[EmailBodyPart(
                    type='text/plain',
                    value='This is a test email sent using the JMAP Engine Python library!'
                )],
                html_body=[EmailBodyPart(
                    type='text/html',
                    value='<p>This is a <strong>test email</strong> sent using the JMAP Engine Python library!</p>'
                )]
            )
            
            # Send email
            print("\nSending email...")
            try:
                submission = client.send_email(email.to_dict())
                print(f"✓ Email sent successfully!")
                print(f"  Submission ID: {submission.get('id', 'N/A')}")
            except Exception as e:
                print(f"✗ Failed to send email: {e}")


if __name__ == '__main__':
    main()
