import asyncio
from leechbot.__main__ import startup

asyncio.get_event_loop().run_until_complete(startup())
