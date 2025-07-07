#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil
import venv

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

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = "venv"
    if os.path.exists(venv_path):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("🔧 Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies in virtual environment"""
    try:
        print("📦 Installing Python dependencies in virtual environment...")
        
        # Determine the correct pip path based on OS
        if os.name == 'nt':  # Windows
            pip_path = os.path.join("venv", "Scripts", "pip")
            python_path = os.path.join("venv", "Scripts", "python")
        else:  # Unix/Linux/macOS
            pip_path = os.path.join("venv", "bin", "pip")
            python_path = os.path.join("venv", "bin", "python")
        
        # Install requirements
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        
        # Create a run script for convenience
        create_run_script(python_path)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_run_script(python_path):
    """Create a convenient run script"""
    if os.name == 'nt':  # Windows
        script_content = f"""@echo off
{python_path} bot.py
pause
"""
        with open("run_bot.bat", "w") as f:
            f.write(script_content)
        print("✅ Created run_bot.bat script")
    else:  # Unix/Linux/macOS
        script_content = f"""#!/bin/bash
{python_path} bot.py
"""
        with open("run_bot.sh", "w") as f:
            f.write(script_content)
        os.chmod("run_bot.sh", 0o755)
        print("✅ Created run_bot.sh script")

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
    print("🤖 Discord AI Bot Setup (Virtual Environment)")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 5
    
    # Check Python version
    if check_python_version():
        checks_passed += 1
    
    # Check FFmpeg (optional for now)
    ffmpeg_available = check_ffmpeg()
    if ffmpeg_available:
        checks_passed += 1
    else:
        print("⚠️ FFmpeg will be needed for voice functionality")
    
    # Create virtual environment
    if create_virtual_environment():
        checks_passed += 1
    
    # Install dependencies
    if install_dependencies():
        checks_passed += 1
    
    # Setup environment file
    if setup_env_file():
        checks_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Setup complete: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed >= 4:  # Allow FFmpeg to be missing initially
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env with your API keys and Discord bot token")
        if os.name == 'nt':
            print("2. Run: run_bot.bat")
        else:
            print("2. Run: ./run_bot.sh")
            print("   Or: source venv/bin/activate && python bot.py")
        
        if not ffmpeg_available:
            print("\n⚠️ Note: Install FFmpeg later for voice functionality")
    else:
        print("⚠️ Some critical setup steps failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())