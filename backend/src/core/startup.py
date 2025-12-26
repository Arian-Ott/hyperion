from .database import init_db, async_session_factory
from ..models.accounts import Role, UsedRefreshToken
import logging
from datetime import datetime, timezone
from sqlalchemy import delete, text
from .security.access import UserRole
logger = logging.getLogger("hyperion.startup")


async def role_creation():
    logger.info("Creating system roles")

    async with async_session_factory() as db:
        for role in UserRole:
            try:
                new_role = Role(name=role.value, system_role=True)
                db.add(new_role)
                await db.commit()
            except:
                await db.rollback()
                logger.warning(f"Role {role} already exists... Skipping...")


async def delete_old_tokens():
    logger.info("Deleting old Refresh Tokens...")
    now = datetime.now(tz=timezone.utc)
    async with async_session_factory() as db:
        qry = delete(UsedRefreshToken).where(UsedRefreshToken.expires_at < now)
        await db.execute(qry)
        await db.commit()


async def setup_database_events():
    """
    Initialise MariaDB event scheduler and recurring cleanup tasks.

    This function enables the global event scheduler and creates the
    cleanup event if it does not already exist.

    :raises Exception: If the database user lacks sufficient privileges
                       to set global variables or create events.
    """
    logger.info("Initialising MariaDB event scheduler...")
    async with async_session_factory() as db:
        try:
            # Create the recurring event
            event_query = """
            CREATE EVENT IF NOT EXISTS discard_expired_refresh_tokens
            ON SCHEDULE EVERY 1 HOUR
            COMMENT 'Removes expired JTIs from the used_refresh_tokens table.'
            DO
              DELETE FROM used_refresh_tokens 
              WHERE expires_at < NOW();
            """
            await db.execute(text(event_query))
            await db.commit()
            logger.info("MariaDB cleanup event configured successfully.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to setup MariaDB events: {e}")
            logger.fatal("Ensure the DB user has 'EVENT' privileges.")


async def startup():
    await init_db()
    await role_creation()
    await delete_old_tokens()
    await setup_database_events()
