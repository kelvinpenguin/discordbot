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
    
    optional_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'ELEVENLABS_API_KEY': 'ElevenLabs API Key',
        'ELEVENLABS_VOICE_ID': 'ElevenLabs Voice ID'
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
    
    print("\n🔧 Optional Configuration:")
    optional_configured = 0
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value or 'your_' in value.lower():
            print(f"⚠️  {description} ({var}) - Not configured")
        else:
            print(f"✅ {description} ({var}) - Configured")
            optional_configured += 1
    
    print("\n" + "=" * 45)
    
    if not all_good:
        print("❌ Configuration incomplete!")
        print("\nTo fix:")
        print("1. Edit the .env file in your project directory")
        print("2. Replace placeholder values with your actual API keys")
        print("3. Run this script again to verify")
        return False
    
    if optional_configured == 0:
        print("⚠️  Bot will start but with limited functionality")
        print("Add OpenAI and ElevenLabs API keys for full features")
    elif optional_configured < len(optional_vars):
        print("✅ Bot will start with partial functionality")
        if not os.getenv('OPENAI_API_KEY') or 'your_' in os.getenv('OPENAI_API_KEY', ''):
            print("   - /ai command will be disabled")
        if not os.getenv('ELEVENLABS_API_KEY') or 'your_' in os.getenv('ELEVENLABS_API_KEY', ''):
            print("   - Voice functionality will be disabled")
    else:
        print("🎉 All configuration complete! Bot ready to run.")
    
    print(f"\nTo start the bot, run: python bot.py")
    return True

def show_setup_help():
    """Show help for getting API keys"""
    print("\n📚 How to get API keys:")
    print("\n1. Discord Bot Token:")
    print("   - Go to https://discord.com/developers/applications")
    print("   - Create a new application")
    print("   - Go to 'Bot' section and create a bot")
    print("   - Copy the token")
    
    print("\n2. OpenAI API Key:")
    print("   - Go to https://platform.openai.com/api-keys")
    print("   - Create a new API key")
    print("   - Copy the key")
    
    print("\n3. ElevenLabs API Key:")
    print("   - Go to https://elevenlabs.io/")
    print("   - Sign up/login and go to your profile")
    print("   - Copy your API key")
    
    print("\n4. ElevenLabs Voice ID (optional):")
    print("   - Go to https://elevenlabs.io/voice-library")
    print("   - Find a voice you like and copy its ID")
    print("   - Or leave the default (Bella voice)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_setup_help()
    else:
        success = check_config()
        if not success:
            print("\n❓ Need help getting API keys? Run: python check_config.py --help")
        
        exit(0 if success else 1)