# Alina Khan - 25 April 2026
# Team Member - 25 April 2026
# A3 review update: improved documentation after PR review

import os


class Config:
    """Base configuration class for the Sakila Flask application."""

    MYSQL_HOST = os.environ.get("MYSQL_HOST", "sakila-db-server")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "admin")
    MYSQL_DB = os.environ.get("MYSQL_DB", "sakila")

    CONNECTION_TIMEOUT = int(os.environ.get("CONNECTION_TIMEOUT", "30"))
    HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", "10"))

    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
