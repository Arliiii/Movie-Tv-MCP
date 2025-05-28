#!/usr/bin/env python3
"""
Setup script for Movie & TV MCP Server
Helps users get started quickly
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print welcome banner"""
    print("🎬" + "=" * 48 + "🎬")
    print("    Movie & TV MCP Server Setup")
    print("🎬" + "=" * 48 + "🎬")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "fastmcp>=2.0.0", "httpx>=0.25.0", "python-dotenv>=1.0.0"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install fastmcp httpx python-dotenv")
        return False

def check_api_key():
    """Check if TMDb API key is configured"""
    # Check for .env file first
    env_file_exists = os.path.exists(".env")
    print(f"\n🔧 Configuration check:")
    print(f"   .env file found: {env_file_exists}")

    # Load .env if it exists
    if env_file_exists:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("   .env file loaded successfully")
        except ImportError:
            print("   Warning: python-dotenv not installed")

    api_key = os.getenv("TMDB_API_KEY")

    if api_key:
        print(f"✅ TMDb API key configured: {api_key[:8]}...")
        return True
    else:
        print("⚠️  TMDb API key not configured")

        if env_file_exists:
            print("   Check your .env file configuration")
        else:
            print("   No .env file found")
            print()
            print("To get your API key:")
            print("1. Visit: https://www.themoviedb.org/settings/api")
            print("2. Create a free account if needed")
            print("3. Request an API key (choose 'Developer' option)")
            print("4. Create a .env file or set environment variable:")
            print()

            if platform.system() == "Windows":
                print("   Windows (Command Prompt):")
                print("   set TMDB_API_KEY=your_actual_api_key_here")
                print()
                print("   Windows (PowerShell):")
                print("   $env:TMDB_API_KEY=\"your_actual_api_key_here\"")
            else:
                print("   Mac/Linux:")
                print("   export TMDB_API_KEY=\"your_actual_api_key_here\"")

        print()
        return False

def run_test():
    """Run the test suite"""
    print("\n🧪 Running tests...")

    try:
        result = subprocess.run([
            sys.executable, "test_server.py"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def main():
    """Main setup function"""
    print_banner()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Check API key
    api_key_configured = check_api_key()

    # Run tests if API key is configured
    if api_key_configured:
        if run_test():
            print("\n🎉 Setup completed successfully!")
            print("\nYour Movie & TV MCP Server is ready to use!")
            print("\nNext steps:")
            print("1. Run: python movie_server.py")
            print("2. Or deploy to Smithery for production use")
        else:
            print("\n⚠️  Setup completed with test failures")
            print("   Check your API key and network connection")
    else:
        print("\n⚠️  Setup completed but API key needed")
        print("   Configure your TMDb API key and run tests")

    print("\n📚 Documentation: README.md")
    print("🔧 Test suite: python test_server.py")
    print("🚀 Start server: python movie_server.py")

if __name__ == "__main__":
    main()
