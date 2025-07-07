#!/usr/bin/env python3

import os

# Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv not installed. Install requirements first: pip install -r requirements.txt")
    print("   Checking .env file manually...\n")

def check_config():
    """Check if the .env file is properly configured"""
    print("🔍 Discord AI Bot - Configuration Checker")
    print("=" * 45)
    
    # Load environment variables
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and add your API keys.")
        return False
    
    if DOTENV_AVAILABLE:
        load_dotenv()
    else:
        # Manually read .env file
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check required variables
    required_vars = {
        'DISCORD_TOKEN': 'Discord Bot Token',
    }
    
    all_good = True
    
    print("\n📋 Required Configuration:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or 'your_' in value.lower():
            print(f"❌ {description} ({var}) - Not set or using placeholder")
            all_good = False
        else:
            print(f"✅ {description} ({var}) - Configured")
    
    print("\n" + "=" * 45)
    
    if not all_good:
        print("❌ Configuration incomplete!")
        print("\nTo fix:")
        print("1. Edit the .env file in your project directory")
        print("2. Replace 'your_discord_bot_token_here' with your actual Discord bot token")
        print("3. Run this script again to verify")
        return False
    
    print("🎉 Configuration complete! Your free AI bot is ready to run!")
    print("✨ Features available:")
    print("   • Free AI chat with /ai command")
    print("   • Smart conversational responses")
    print("   • No API costs or limits")
    print("   • Works immediately!")
    
    print(f"\nTo start the bot, run: python bot.py")
    return True

def show_setup_help():
    """Show help for getting Discord bot token"""
    print("\n📚 How to get your Discord Bot Token:")
    print("\n🤖 Step-by-step setup:")
    print("   1. Go to https://discord.com/developers/applications")
    print("   2. Click 'New Application' and give it a name")
    print("   3. Go to the 'Bot' section in the left sidebar")
    print("   4. Click 'Add Bot' if needed")
    print("   5. Under 'Token', click 'Reset Token' then 'Copy'")
    print("   6. Paste this token in your .env file")
    
    print("\n🔐 Bot Permissions Setup:")
    print("   1. In the same bot page, scroll to 'Privileged Gateway Intents'")
    print("   2. Enable 'Message Content Intent'")
    print("   3. Go to 'OAuth2' → 'URL Generator'")
    print("   4. Select scopes: 'bot' and 'applications.commands'")
    print("   5. Select permissions: 'Send Messages', 'Use Slash Commands'")
    print("   6. Use the generated URL to invite your bot to a server")
    
    print("\n✨ That's it! No other API keys needed - this bot is completely free!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_setup_help()
    else:
        success = check_config()
        if not success:
            print("\n❓ Need help setting up Discord bot? Run: python check_config.py --help")
        
        exit(0 if success else 1)