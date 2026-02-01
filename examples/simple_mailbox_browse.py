"""
Simple Mailbox Browser Example

Quick demo of mailbox navigation features.
"""

from jmap_engine import JMAPClient


# Configuration
BASE_URL = 'https://api.fastmail.com'
API_KEY = 'your-api-key-here'
USERNAME = 'your-email@fastmail.com'

with JMAPClient(BASE_URL, USERNAME, API_KEY) as client:
    # Get mailbox tree
    tree = client.get_mailbox_tree()
    
    # 1. Print tree structure
    print("📁 Your Mailboxes:\n")
    tree.print_tree()
    
    # 2. Get inbox
    inbox = tree.get_by_role('inbox')
    print(f"\n📥 Inbox:")
    print(f"   Total emails: {inbox.total_emails}")
    print(f"   Unread: {inbox.unread_emails}")
    
    # 3. Check if inbox has subfolders
    if inbox.has_children:
        print(f"   Subfolders:")
        for subfolder in inbox.children:
            print(f"      • {subfolder.name} ({subfolder.total_emails} emails)")
        
        # Recursive count (including all subfolders)
        total_with_subs = inbox.get_total_emails_recursive()
        unread_with_subs = inbox.get_unread_emails_recursive()
        print(f"   Total with subfolders: {total_with_subs} emails, {unread_with_subs} unread")
    
    # 4. Get sent mailbox
    sent = tree.get_by_role('sent')
    if sent:
        print(f"\n📤 Sent:")
        print(f"   Total emails: {sent.total_emails}")
    
    # 5. Statistics
    stats = tree.get_statistics()
    print(f"\n📊 Account Summary:")
    print(f"   {stats['total_mailboxes']} mailboxes")
    print(f"   {stats['total_emails']} total emails")
    print(f"   {stats['unread_emails']} unread")
