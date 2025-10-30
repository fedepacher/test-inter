"""
Settings module for managing application environment variables.

This module retrieves and provides access to environment variables
used for database configuration, email settings, and application secrets.
"""

import logging
import json
import os


class Settings:
    """
    Handles configuration using environment variables.
    """

    run_env = os.getenv('RUN_ENV')

    _db_name: str = os.getenv('DB_NAME')
    _db_user: str = os.getenv('DB_USER')
    db_pass: str = os.getenv('DB_PASS')
    db_host: str = os.getenv('DB_HOST')
    db_port: int = os.getenv('DB_PORT')

    log_file: str | None = os.getenv('LOG_FILE', None)

    secret_key: str = os.getenv('SECRET_KEY')
    token_expire: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    deployment_service: str = os.getenv('DEPLOYMENT_SERVICE')

    @classmethod
    def db_name(cls):
        """
        Retrieves the database name, appending a test prefix if in test environment.

        Returns:
            str: The database name, with 'test_' prefix if RUN_ENV is 'test'.
        """
        return cls._db_name + '_' + cls.run_env

    @classmethod
    def db_user(cls):
        """
        Retrieves the database user, overriding with 'root' in test environment.

        Returns:
            str: The database user, or 'root' if RUN_ENV is 'test'.
        """
        return cls._db_user
