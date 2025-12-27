# Hyperion
# Copyright (C) 2025 Arian Ott <arian.ott@ieee.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .database import init_db, async_session_factory
from ..models.accounts import Role, UsedRefreshToken
from ..models.fixtures import Manufacturer
import logging
from datetime import datetime, timezone
from sqlalchemy import delete, text
from .security.access import UserRole
from . import settings

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
              
            CREATE EVENT IF NOT EXISTS delete_expired_otp
            ON SCHEDULE EVERY 1 HOUR
            COMMENT 'Removes expired OTP from the otp_challenge table.'
            DO
                DELETE FROM otp_challenges
                WHERE  expires_at < NOW();
                
            CREATE EVENT IF NOT EXISTS delete_expired_device_tokens
            ON SCHEDULE EVERY 1 HOUR
            COMMENT 'Removes expired device tokens from the client_tokens table.'
            DO
                DELETE FROM client_tokens
                WHERE  expires_at < NOW();
            
            """
            if settings.DEBUG:
                event_query = (
                    """DROP EVENT IF EXISTS discard_expired_refresh_tokens;
            DROP EVENT IF EXISTS delete_expired_otp;
            DROP EVENT IF EXISTS delete_expired_device_tokens;
            """
                    + event_query
                )
            await db.execute(text(event_query))
            await db.commit()
            logger.info("MariaDB cleanup event configured successfully.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to setup MariaDB events: {e}")
            logger.fatal("Ensure the DB user has 'EVENT' privileges.")

async def seed_manufacturers():
    manufacturer_list = [
        Manufacturer(name="ACME", website="https://www.acme.com.cn/"),
        Manufacturer(name="ADB Stagelight",
                     website="https://www.adb-stagelight.com/"),
        Manufacturer(name="ADJ (American DJ)", website="https://www.adj.com/"),
        Manufacturer(name="Altman Lighting",
                     website="https://www.altmanlighting.com/"),
        Manufacturer(name="Amerec", website="https://www.amerec.com/"),
        Manufacturer(name="Antari", website="https://antari.com/"),
        Manufacturer(name="Aputure", website="https://www.aputure.com/"),
        Manufacturer(name="ArcLight", website="https://www.arclight.com/"),
        Manufacturer(name="Arri", website="https://www.arri.com/"),
        Manufacturer(name="Astera", website="https://astera-led.com/"),
        Manufacturer(name="Avolites", website="https://www.avolites.com/"),
        Manufacturer(name="Ayrton", website="https://www.ayrton.eu/"),
        Manufacturer(name="B-Lighting", website="https://www.b-lighting.be/"),
        Manufacturer(name="Blizzard Lighting",
                     website="https://www.blizzardpro.com/"),
        Manufacturer(name="Briteq", website="https://briteq-lighting.com/"),
        Manufacturer(name="Cameo", website="https://www.cameolight.com/"),
        Manufacturer(name="Cast Software (WYSIWYG)",
                     website="https://cast-soft.com/"),
        Manufacturer(name="Chamsys", website="https://chamsyslighting.com/"),
        Manufacturer(name="Chauvet Professional",
                     website="https://www.chauvetprofessional.com/"),
        Manufacturer(name="Chroma-Q", website="https://chroma-q.com/"),
        Manufacturer(name="City Theatrical",
                     website="https://www.citytheatrical.com/"),
        Manufacturer(name="Clay Paky", website="https://www.claypaky.it/"),
        Manufacturer(name="Coemar", website="https://www.coemar.com/"),
        Manufacturer(name="Color Kinetics",
                     website="https://www.colorkinetics.com/"),
        Manufacturer(name="Coolux (Pandoras Box)",
                     website="https://www.christiedigital.com/"),
        Manufacturer(name="Daslight", website="https://www.daslight.com/"),
        Manufacturer(name="DedoLight", website="https://www.dedolight.com/"),
        Manufacturer(name="DTS Lighting", website="https://dts-lighting.it/"),
        Manufacturer(name="Eclalux", website="https://www.eclalux.com/"),
        Manufacturer(name="Elation Professional",
                     website="https://www.elationlighting.com/"),
        Manufacturer(name="Electronic Theatre Controls (ETC)",
                     website="https://www.etcconnect.com/"),
        Manufacturer(name="Eliminator Lighting",
                     website="https://www.adj.com/eliminator-lighting/"),
        Manufacturer(name="Enttec", website="https://www.enttec.com/"),
        Manufacturer(name="Ereimul", website="https://www.ereimul.com/"),
        Manufacturer(name="Espen Technology",
                     website="https://www.espentech.com/"),
        Manufacturer(name="Eurolite",
                     website="https://www.steinigke.de/eurolite/"),
        Manufacturer(name="Explo", website="https://www.explo.at/"),
        Manufacturer(name="Fine Art",
                     website="https://www.fineart-light.com/"),
        Manufacturer(name="Flash Professional",
                     website="https://flash-butrym.pl/"),
        Manufacturer(name="Futurelight",
                     website="https://www.futurelight.de/"),
        Manufacturer(name="Gantom", website="https://www.gantom.com/"),
        Manufacturer(name="Generic Line",
                     website="https://www.generic-line.de/"),
        Manufacturer(name="GLP (German Light Products)",
                     website="https://www.glp.de/"),
        Manufacturer(name="Griven", website="https://www.griven.com/"),
        Manufacturer(name="HazeBase", website="https://hazebase.com/"),
        Manufacturer(name="High End Systems",
                     website="https://www.etcconnect.com/"),
        Manufacturer(name="Hungaroflash",
                     website="https://www.hungaroflash.hu/"),
        Manufacturer(name="Ianiro", website="https://www.ianiro.com/"),
        Manufacturer(name="Inner Circles",
                     website="https://www.innercircles.com/"),
        Manufacturer(name="JB-Lighting",
                     website="https://www.jb-lighting.de/"),
        Manufacturer(name="Jem (Martin)", website="https://www.martin.com/"),
        Manufacturer(name="Kino Flo", website="https://www.kinoflo.com/"),
        Manufacturer(name="Kvant Lasers",
                     website="https://www.kvantlasers.sk/"),
        Manufacturer(name="LDR (Luci della Ribalta)",
                     website="https://www.ldr.it/"),
        Manufacturer(name="Lee Filters",
                     website="https://www.leefilters.com/"),
        Manufacturer(name="Light Sky", website="https://www.lightsky.com.cn/"),
        Manufacturer(name="Light-Processor",
                     website="https://www.lightprocessor.co.uk/"),
        Manufacturer(name="Lightpower", website="https://www.lightpower.de/"),
        Manufacturer(name="Litecraft",
                     website="https://www.litecraft-lighting.com/"),
        Manufacturer(name="Lite-Puter",
                     website="https://www.liteputer.com.tw/"),
        Manufacturer(name="Littlite", website="https://www.littlite.com/"),
        Manufacturer(name="Look Solutions",
                     website="https://looksolutions.com/"),
        Manufacturer(name="LSC Control Systems",
                     website="https://www.lsccontrol.com.au/"),
        Manufacturer(name="Lumenpulse", website="https://www.lumenpulse.com/"),
        Manufacturer(name="Luminex", website="https://www.luminex.be/"),
        Manufacturer(name="Luxibel", website="https://www.luxibel.com/"),
        Manufacturer(name="MA Lighting",
                     website="https://www.malighting.com/"),
        Manufacturer(name="Madrix", website="https://www.madrix.com/"),
        Manufacturer(name="Martin Professional",
                     website="https://www.martin.com/"),
        Manufacturer(name="MDG Fog Generators",
                     website="https://www.mdgfog.com/"),
        Manufacturer(name="Minuit Une", website="https://minuitune.com/"),
        Manufacturer(name="Mole-Richardson", website="https://www.mole.com/"),
        Manufacturer(name="Music & Lights (Prolights)",
                     website="https://www.musiclights.it/"),
        Manufacturer(name="Nicolaudie", website="https://www.nicolaudie.com/"),
        Manufacturer(name="Obsidian Control Systems",
                     website="https://obsidiancontrol.com/"),
        Manufacturer(name="Osram", website="https://www.osram.com/"),
        Manufacturer(name="Pangolin Laser Systems",
                     website="https://pangolin.com/"),
        Manufacturer(name="Pathway Connectivity",
                     website="https://www.pathwayconnect.com/"),
        Manufacturer(name="Philips Entertainment",
                     website="https://www.lighting.philips.com/"),
        Manufacturer(name="Portman Lights",
                     website="https://portmanlights.com/"),
        Manufacturer(name="Prolights", website="https://www.prolights.it/"),
        Manufacturer(name="Pulsar", website="https://www.pulsarlight.com/"),
        Manufacturer(name="Quasar Science",
                     website="https://www.quasarscience.com/"),
        Manufacturer(name="Robe", website="https://www.robe.cz/"),
        Manufacturer(name="Robert Juliat",
                     website="https://www.robertjuliat.com/"),
        Manufacturer(name="Rosco", website="https://www.rosco.com/"),
        Manufacturer(name="ROXX", website="https://roxxlight.com/"),
        Manufacturer(name="Sellecon (Strand)",
                     website="https://www.strandlighting.com/"),
        Manufacturer(name="SGM Light", website="https://sgmlight.com/"),
        Manufacturer(name="Showtec", website="https://www.highlite.com/"),
        Manufacturer(name="Smoke Factory",
                     website="https://smoke-factory.de/"),
        Manufacturer(name="Spotlight", website="https://www.spotlight.it/"),
        Manufacturer(name="Stairville", website="https://www.thomann.de/"),
        Manufacturer(name="StarWay", website="https://en.starway.eu/"),
        Manufacturer(name="Strand Lighting",
                     website="https://www.strandlighting.com/"),
        Manufacturer(name="Studio Due", website="https://www.studiodue.com/"),
        Manufacturer(name="Swisson", website="https://www.swisson.com/"),
        Manufacturer(name="TMB (Solaris)", website="https://tmb.com/"),
        Manufacturer(name="Vari-Lite", website="https://www.vari-lite.com/"),
        Manufacturer(name="Zero 88", website="https://www.zero88.com/"),
    ]
    async with async_session_factory() as db:
        for manufact in manufacturer_list:
            try:
                db.add(manufact)
                await db.flush()
                logger.info(f"Added {manufact.name} to DB")              
            except Exception:
                await db.rollback()
                logger.warning(f"Duplicate entry '{manufact.name}', skipping...")
                continue
        await db.commit()
        

async def startup():
    await init_db()
    await role_creation()
    await delete_old_tokens()
    await setup_database_events()
    await seed_manufacturers()
