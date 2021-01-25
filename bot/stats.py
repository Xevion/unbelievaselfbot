"""
stats.py

Holds classes and functions related to working with the database, i.e. storing statistics collected by the client.
"""

import asyncio
import logging
import sqlite3

import aiosqlite

from bot import constants

logger = logging.getLogger(__file__)
logger.setLevel(constants.LOGGING_LEVEL)


class StatsHandler(object):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db

    @classmethod
    async def create(cls) -> 'StatsHandler':
        """Factory method for creating StatsHandler objects."""
        db = await aiosqlite.connect(constants.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        stats = StatsHandler(db)
        # await stats.construct()
        await db.commit()
        return stats

    async def construct(self) -> None:
        """Construct the database."""
        await self.db.execute('''CREATE TABLE IF NOT EXISTS change
                                (id INTEGER PRIMARY KEY,    
                                self BOO
                                ''')

    async def record_change(self) -> None:
        pass

aiosqlite.register_adapter(bool, int)
aiosqlite.register_converter("BOOLEAN", lambda v: bool(int(v)))
asyncio.run(StatsHandler.create())
