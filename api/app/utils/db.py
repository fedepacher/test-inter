""" Setting Connections """

import asyncio
import logging
from peewee_async import PooledMySQLDatabase as PooledMySQLDatabaseAsync
from api.app.utils.settings import Settings


DB_NAME = Settings.db_name()
DB_USER = Settings.db_user()
DB_PASS = Settings.db_pass
DB_HOST = Settings.db_host
DB_PORT = Settings.db_port
DEPLOYMENT_SERVICE = Settings.deployment_service

if DB_NAME is None:
    raise ValueError("DB_NAME env var not set")
if DB_USER is None:
    raise ValueError("DB_USER env var not set")
if DB_PASS is None:
    raise ValueError("DB_PASS env var not set")
if DB_PORT is None:
    raise ValueError("DB_PORT env var not set")
if DEPLOYMENT_SERVICE is None:
    raise ValueError("DEPLOYMENT_SERVICE env var not set")

if 'local' in DEPLOYMENT_SERVICE:
    logging.info(f"Connecting pool to local database at {DB_HOST}")
    db = PooledMySQLDatabaseAsync(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=int(DB_PORT)
    )
else:
    logging.error(f"No connection pool for host {DB_HOST}")


async def renew_connection_if_needed():
    """
    Renew connection if inactive or close.
    """
    if db.is_closed():
        try:
            db.connect(reuse_if_open=True)
            logging.info("Reconnected to the database.")
        except Exception as e:
            logging.error(f"Error reconnecting to the database: {e}")


async def renew_connections_periodically():
    """
    Check connection pool status.
    """
    while True:
        try:
            await renew_connection_if_needed()
        except Exception as e:
            logging.error(f"Error during connection renewal: {e}")
        await asyncio.sleep(60)
