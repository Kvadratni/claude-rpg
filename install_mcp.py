#!/usr/bin/env python3
"""
Auto-install RPG MCP Server globally
This script ensures the MCP server is available as 'rpg-mcp' command
"""

import subprocess
import sys
from pathlib import Path

def install_rpg_mcp():
    """Install the RPG MCP server globally"""
    print("🔧 Installing RPG MCP Server globally...")
    
    # Get the current directory (should be the game directory)
    game_dir = Path(__file__).parent
    mcp_package_dir = game_dir / "rpg_mcp_package"
    
    if not mcp_package_dir.exists():
        print("❌ MCP package directory not found!")
        return False
    
    try:
        # Install the package globally using uv tool
        result = subprocess.run([
            "uv", "tool", "install", "--editable", str(mcp_package_dir)
        ], capture_output=True, text=True, check=True)
        
        print("✅ RPG MCP Server installed successfully!")
        print(f"   Command available: rpg-mcp")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install RPG MCP Server: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ uv command not found. Please install uv first.")
        return False

def check_installation():
    """Check if rpg-mcp is already installed"""
    try:
        result = subprocess.run(["which", "rpg-mcp"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ RPG MCP Server already installed at: {result.stdout.strip()}")
            return True
        else:
            print("ℹ️  RPG MCP Server not found, installing...")
            return False
    except Exception as e:
        print(f"ℹ️  Could not check installation: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 RPG MCP Server Auto-Installer")
    print("=" * 40)
    
    # Check if already installed
    if check_installation():
        print("✅ No installation needed!")
        return True
    
    # Install the package
    success = install_rpg_mcp()
    
    if success:
        print("\n🎉 Installation complete!")
        print("   You can now use: uvx rpg-mcp")
        print("   Recipes will use this command automatically")
    else:
        print("\n❌ Installation failed!")
        print("   Please check the error messages above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)