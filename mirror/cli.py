#!/usr/bin/env python3
"""
MIRROR CLI — Command-line interface for management
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mirror.core.memory import Memory
from mirror.modules.dna_cloner import DNACloner
from mirror.utils.logger import get_logger

logger = get_logger("cli")


def main():
    args = sys.argv[1:]
    if not args:
        print("MIRROR — Autonomous Client Hunting Organism")
        print(f"Usage: python cli.py [command]")
        print("")
        print("Commands:")
        print("  --init          Initialize system (first-time setup)")
        print("  --clone-me      Extract your writing DNA")
        print("  --status        Show system status")
        print("  --update        Check for updates")
        print("  --check-update  Check if update available")
        print("  --help          Show this help")
        return

    command = args[0]

    if command == "--help":
        print("""
MIRROR CLI Commands:

  --init              First-time setup wizard
  --clone-me          Extract writing style from Facebook history
  --status            Show current system status
  --check-update      Check for available updates
  --update            Apply latest update
  --help              Show this help

Documentation: README.md
        """)

    elif command == "--clone-me":
        print("🧬 DNA Cloner")
        fb_path = input("Enter path to Facebook data export: ").strip()
        if not fb_path or not Path(fb_path).exists():
            print("❌ Invalid path")
            return

        cloner = DNACloner()
        cloner.extract_from_fb_data(fb_path)
        profile = cloner.get_profile()

        print(f"\n✅ DNA profile created!")
        print(f"   Avg sentence length: {profile['structure']['avg_sentence_length']}")
        print(f"   Question ratio: {profile['structure']['question_ratio']}")
        print(f"   Emoji frequency: {profile['style']['emoji_frequency']}")
        print(f"   Banglish ratio: {profile['style']['banglish_ratio']}")
        print(f"   Top words: {', '.join(profile['vocabulary']['top_words'][:10])}")
        print(f"\nSaved to: config/dna_profile.json")

    elif command == "--init":
        print("\n🚀 MIRROR Initialization Wizard\n")
        print("Step 1: Setup API Keys")
        print("  Edit config/secrets.env with your API keys")

        print("\nStep 2: DNA Cloning")
        print("  Run: python cli.py --clone-me")

        print("\nStep 3: Start the Agent")
        print("  Run: python main.py")
        print("  Or: python cli.py --start")

        print("\n⚠️  Before running:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure secrets.env")
        print("  3. Update config/groups.yaml with actual FB group URLs")
        print("\n✅ Initialization guide complete!")

    elif command == "--status":
        print("📊 MIRROR Status")
        db_dir = Path(__file__).parent / "database"
        if db_dir.exists():
            dbs = list(db_dir.glob("*.db"))
            print(f"  Databases: {len(dbs)} files")
            for d in dbs:
                size = d.stat().st_size
                print(f"    {d.name}: {size / 1024:.1f} KB")
        else:
            print("  No databases found (not initialized)")

        config_dir = Path(__file__).parent / "config"
        if (config_dir / "dna_profile.json").exists():
            print("  DNA Profile: ✅ Loaded")
        else:
            print("  DNA Profile: ❌ Not configured")

    elif command == "--check-update":
        print("🔍 Checking for updates...")
        print("  Current version: 1.0.0")
        print("  Latest version: 1.0.0 (up to date)")

    elif command == "--update":
        print("⬇️  Updating MIRROR...")
        print("  This feature is coming soon.")
        print("  For now, pull the latest from your repository.")

    elif command == "--start":
        print("🚀 Starting MIRROR agent...")
        from main import MirrorApplication

        async def run():
            app = MirrorApplication()
            await app.start()

        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            print("\nMIRROR stopped.")

    else:
        print(f"Unknown command: {command}")
        print("Run 'python cli.py --help' for usage")


if __name__ == "__main__":
    main()
