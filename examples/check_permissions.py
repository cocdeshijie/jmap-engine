"""
Check API Key Permissions

Shows what operations are allowed with your API key.
"""

from jmap_engine import JMAPClient


def main():
    # Configuration
    BASE_URL = 'https://api.fastmail.com'
    API_KEY = 'your-api-key-here'
    USERNAME = 'your-email@fastmail.com'
    
    print("\n🔐 Checking API Key Permissions...\n")
    
    with JMAPClient(BASE_URL, USERNAME, API_KEY) as client:
        # Method 1: Print formatted permissions
        client.print_permissions()
        
        # Method 2: Get permissions as dictionary for programmatic use
        print("\n" + "=" * 70)
        print("           Programmatic Access Example")
        print("=" * 70 + "\n")
        
        perms = client.get_permissions()
        
        # Check specific capabilities
        if 'urn:ietf:params:jmap:mail' in perms['capabilities']:
            print("✅ This API key can READ emails")
            
            # Get mail account details
            mail_account_id = perms['primary_accounts'].get('urn:ietf:params:jmap:mail')
            if mail_account_id:
                account = perms['accounts'][mail_account_id]
                print(f"   Mail account: {account.get('name')}")
                
                # Check for size limits
                mail_cap = account.get('accountCapabilities', {}).get('urn:ietf:params:jmap:mail', {})
                max_size = mail_cap.get('maxSizeMessageAttachments')
                if max_size:
                    print(f"   Max attachment size: {max_size / (1024*1024):.1f} MB")
        
        if 'urn:ietf:params:jmap:submission' in perms['capabilities']:
            print("✅ This API key can SEND emails")
        else:
            print("❌ This API key CANNOT send emails")
            print("   💡 Generate a new API key with 'Write mail' permission")
        
        if 'urn:ietf:params:jmap:contacts' in perms['capabilities']:
            print("✅ This API key can manage CONTACTS")
        
        if 'urn:ietf:params:jmap:calendars' in perms['capabilities']:
            print("✅ This API key can manage CALENDARS")
        
        # Show all raw capabilities
        print(f"\n📋 All Capabilities ({len(perms['capabilities'])}):")
        for cap in perms['capabilities'].keys():
            print(f"   • {cap}")
        
        # Show Fastmail-specific features
        fastmail_caps = [cap for cap in perms['capabilities'].keys() if 'fastmail' in cap]
        if fastmail_caps:
            print(f"\n🚀 Fastmail-specific Features:")
            for cap in fastmail_caps:
                print(f"   • {cap}")


if __name__ == '__main__':
    main()
