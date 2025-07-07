#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"You have Python {sys.version}")
        return False
    print("✅ Python version is compatible")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    if shutil.which('ffmpeg') is None:
        print("❌ FFmpeg not found!")
        print("Please install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    print("✅ FFmpeg is installed")
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup environment file"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
            print("📝 Please edit .env with your actual API keys and tokens")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def main():
    """Main setup function"""
    print("🤖 Discord AI Bot Setup")
    print("=" * 30)
    
    checks_passed = 0
    total_checks = 4
    
    # Check Python version
    if check_python_version():
        checks_passed += 1
    
    # Check FFmpeg
    if check_ffmpeg():
        checks_passed += 1
    
    # Install dependencies
    if install_dependencies():
        checks_passed += 1
    
    # Setup environment file
    if setup_env_file():
        checks_passed += 1
    
    print("\n" + "=" * 30)
    print(f"Setup complete: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All setup steps completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env with your API keys and Discord bot token")
        print("2. Run: python bot.py")
    else:
        print("⚠️ Some setup steps failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())