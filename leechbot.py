import sys
import os
import asyncio

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from leechbot.__main__ import startup

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(startup())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
