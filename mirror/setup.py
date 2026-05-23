#!/usr/bin/env python3
"""MIRROR setup script — one-command installer"""

import subprocess
import sys
from pathlib import Path


def main():
    print("🚀 MIRROR — Autonomous Client Hunting Organism")
    print("=" * 50)
    print("\n📦 Installing dependencies...")

    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r",
                str(req_file)
            ])
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️  Some packages failed to install")
    else:
        print("⚠️  requirements.txt not found")

    print("\n📁 Creating database...")
    from mirror.core.memory import Memory
    Memory()
    print("✅ Database initialized")

    print("\n🔧 Setup complete!")
    print("\nNext steps:")
    print("  1. Edit config/secrets.env with your API keys")
    print("  2. Run: python cli.py --clone-me")
    print("  3. Start: python cli.py --start")
    print("\nHappy hunting! 🎯")


if __name__ == "__main__":
    main()
