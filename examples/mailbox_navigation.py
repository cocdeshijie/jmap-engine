"""
JMAP Engine - Mailbox Navigation Example

Demonstrates mailbox tree navigation, counting emails, and exploring hierarchy.
"""

from jmap_engine import JMAPClient


def main():
    # Configuration
    BASE_URL = 'https://api.fastmail.com'
    API_KEY = 'your-api-key-here'  # Fastmail API key
    USERNAME = 'your-email@fastmail.com'
    
    print("=" * 70)
    print("         JMAP Engine - Mailbox Navigation Example")
    print("=" * 70)
    
    with JMAPClient(BASE_URL, USERNAME, API_KEY) as client:
        print("\n✓ Connected to JMAP server\n")
        
        # Get mailbox tree
        tree = client.get_mailbox_tree()
        
        # 1. Print full tree structure
        print("📁 Mailbox Tree Structure:")
        print("-" * 70)
        tree.print_tree(show_counts=True)
        
        # 2. Get statistics
        print("\n📊 Mailbox Statistics:")
        print("-" * 70)
        stats = tree.get_statistics()
        print(f"Total mailboxes: {stats['total_mailboxes']}")
        print(f"Root mailboxes: {stats['root_mailboxes']}")
        print(f"Total emails: {stats['total_emails']}")
        print(f"Unread emails: {stats['unread_emails']}")
        print(f"Deepest level: {stats['deepest_level']}")
        
        # 3. Find specific mailboxes by role
        print("\n📥 Standard Mailboxes:")
        print("-" * 70)
        
        standard_roles = ['inbox', 'sent', 'drafts', 'trash', 'spam', 'archive']
        for role in standard_roles:
            mailbox = tree.get_by_role(role)
            if mailbox:
                recursive_total = mailbox.get_total_emails_recursive()
                recursive_unread = mailbox.get_unread_emails_recursive()
                
                print(f"{str(mailbox)}")
                print(f"   Path: {mailbox.path}")
                print(f"   ID: {mailbox.id}")
                if mailbox.has_children:
                    print(f"   Including subfolders: {recursive_total} total, {recursive_unread} unread")
                    print(f"   Direct children: {len(mailbox.children)}")
        
        # 4. Explore Inbox in detail
        inbox = tree.get_by_role('inbox')
        if inbox:
            print(f"\n📥 Inbox Details:")
            print("-" * 70)
            print(f"Name: {inbox.name}")
            print(f"Total emails: {inbox.total_emails}")
            print(f"Unread emails: {inbox.unread_emails}")
            print(f"Total threads: {inbox.total_threads}")
            print(f"Unread threads: {inbox.unread_threads}")
            
            if inbox.has_children:
                print(f"\n   Subfolders under Inbox:")
                for child in inbox.children:
                    print(f"      {child}")
                    # Show nested children
                    if child.has_children:
                        for subchild in child.children:
                            print(f"         └─ {subchild}")
        
        # 5. Find mailboxes by name
        print(f"\n🔍 Find Mailbox by Name:")
        print("-" * 70)
        
        # Try common names
        test_names = ['Archive', 'Sent', 'Important', 'Projects']
        for name in test_names:
            mailbox = tree.get_by_name(name)
            if mailbox:
                print(f"   Found: {mailbox.name} ({mailbox.total_emails} emails)")
            else:
                print(f"   Not found: {name}")
        
        # 6. Find by path
        print(f"\n📂 Find Mailbox by Path:")
        print("-" * 70)
        
        # Example paths (adjust to your mailbox structure)
        test_paths = ['Inbox', 'Inbox/Subfolder', 'Archive/2025']
        for path in test_paths:
            mailbox = tree.find_by_path(path)
            if mailbox:
                print(f"   {path} → {mailbox.total_emails} emails, {mailbox.unread_emails} unread")
            else:
                print(f"   {path} → Not found")
        
        # 7. Show all root mailboxes
        print(f"\n📁 Root Mailboxes:")
        print("-" * 70)
        for root in tree.roots:
            print(f"   {root}")
            
            # Recursive count
            if root.has_children:
                all_children = root.get_all_children()
                total_recursive = root.get_total_emails_recursive()
                unread_recursive = root.get_unread_emails_recursive()
                print(f"      └─ {len(all_children)} total subfolders, {total_recursive} emails")
        
        # 8. Interactive navigation
        print(f"\n🧭 Interactive Mailbox Explorer:")
        print("-" * 70)
        
        while True:
            choice = input("\nEnter mailbox name to explore (or 'quit' to exit): ").strip()
            
            if choice.lower() in ['quit', 'q', 'exit']:
                break
            
            if not choice:
                continue
            
            # Try to find mailbox
            mailbox = tree.get_by_name(choice)
            
            if not mailbox:
                # Try by path
                mailbox = tree.find_by_path(choice)
            
            if mailbox:
                print(f"\n📂 {mailbox.name}")
                print(f"   ID: {mailbox.id}")
                print(f"   Path: {mailbox.path}")
                print(f"   Depth: {mailbox.depth}")
                print(f"   Role: {mailbox.role or 'custom'}")
                print(f"   Total emails: {mailbox.total_emails}")
                print(f"   Unread emails: {mailbox.unread_emails}")
                
                if mailbox.parent_id:
                    parent = tree.get_by_id(mailbox.parent_id)
                    print(f"   Parent: {parent.name if parent else 'N/A'}")
                
                if mailbox.has_children:
                    print(f"   Children ({len(mailbox.children)}):")
                    for child in mailbox.children:
                        print(f"      • {child.name} ({child.total_emails} emails)")
                    
                    recursive_total = mailbox.get_total_emails_recursive()
                    recursive_unread = mailbox.get_unread_emails_recursive()
                    print(f"   Total (recursive): {recursive_total} emails, {recursive_unread} unread")
                
                # Permissions
                perms = []
                if mailbox.can_read():
                    perms.append('read')
                if mailbox.can_write():
                    perms.append('write')
                if mailbox.can_delete():
                    perms.append('delete')
                print(f"   Permissions: {', '.join(perms) if perms else 'none'}")
            else:
                print(f"   ✗ Mailbox '{choice}' not found")
                print(f"   💡 Try: {', '.join([m.name for m in tree.roots[:5]])}")


if __name__ == '__main__':
    main()
