import logging

import oracledb

from app.settings import JDASettings

jda_settings = JDASettings()

logger = logging.getLogger(__name__)


def create_oracle_connection() -> oracledb.Connection:
    """Create oracle connection."""
    logger.info("Connect to JDA database")
    oracledb.init_oracle_client()
    return oracledb.connect(
        user=jda_settings.jda_database_user,
        password=jda_settings.jda_database_password.get_secret_value(),
        dsn=jda_settings.jda_database_connection_string_dns.get_secret_value(),
    )
