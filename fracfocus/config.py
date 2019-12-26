from __future__ import annotations
import logging
import os
import socket
import shutil

from dotenv import load_dotenv
import pandas as pd
import tomlkit
import yaml
from attrdict import AttrDict
from sqlalchemy.engine.url import URL

""" Optional Pandas display settings"""
pd.options.display.max_rows = None
pd.set_option("display.float_format", lambda x: "%.2f" % x)
pd.set_option("large_repr", "truncate")
pd.set_option("precision", 2)

_pg_aliases = ["postgres", "postgresql", "psycopg2", "psycopg2-binary"]
_mssql_aliases = ["mssql", "sql server"]

APP_SETTINGS = os.getenv("APP_SETTINGS", "fracfocus.config.DevelopmentConfig")
FLASK_APP = os.getenv("FLASK_APP", "fracfocus.manage.py")


def make_config_path(path: str, filename: str) -> str:
    return os.path.abspath(os.path.join(path, filename))


def load_config(path: str) -> AttrDict:
    with open(path) as f:
        return AttrDict(yaml.safe_load(f))


def get_active_config() -> AttrDict:
    return globals()[APP_SETTINGS.replace("fracfocus.config.", "")]()


def get_default_port(driver: str):
    port = None
    if driver in _pg_aliases:
        port = 5432
    elif driver in _mssql_aliases:
        port = 1433

    return port


def get_default_driver(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "postgres"  # "psycopg2"
    elif dialect in _mssql_aliases:
        driver = "pymssql"

    return driver


def get_default_schema(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "public"
    elif dialect in _mssql_aliases:
        driver = "dbo"

    return driver


def make_url(url_params: dict) -> URL:
    return URL(**url_params)


def _get_project_meta() -> dict:
    pyproj_path = "./pyproject.toml"
    if os.path.exists(pyproj_path):
        with open(pyproj_path, "r") as pyproject:
            file_contents = pyproject.read()
        return tomlkit.parse(file_contents)["tool"]["poetry"]
    else:
        return {}


pkg_meta = _get_project_meta()
project = pkg_meta.get("name")
version = pkg_meta.get("version")


class BaseConfig:
    """Base configuration"""

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    ENV_NAME = os.getenv("ENV_NAME", socket.gethostname())

    """ Datadog """
    DATADOG_ENABLED = os.getenv("DATADOG_ENABLED", False)
    DATADOG_API_KEY = os.getenv("DATADOG_API_KEY", None)
    DATADOG_APP_KEY = os.getenv("DATADOG_APP_KEY", None)

    """ Config """
    CONFIG_BASEPATH = "./config"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)
    COLLECTOR_BASE_URL = os.getenv("FRACFOCUS_BASE_URL", None)

    """ Logging """
    LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)
    LOG_FORMAT = os.getenv("LOG_FORMAT", "funcname")

    """ --------------- Sqlalchemy --------------- """

    DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgres")
    DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", get_default_driver(DATABASE_DIALECT))
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", get_default_port(DATABASE_DRIVER))
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", get_default_schema(DATABASE_DRIVER))
    DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres")
    DATABASE_URL_PARAMS = {
        "drivername": DATABASE_DRIVER,
        "username": DATABASE_USERNAME,
        "password": DATABASE_PASSWORD,
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "database": DATABASE_NAME,
    }
    SQLALCHEMY_DATABASE_URI = str(make_url(DATABASE_URL_PARAMS))
    DEFAULT_EXCLUSIONS = ["updated_at", "inserted_at"]

    @property
    def show(self):
        return [x for x in dir(self) if not x.startswith("_")]

    @property
    def api_params(self):
        return {
            key.lower().replace("api_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("API_")
        }

    @property
    def datadog_params(self):
        return {
            key.lower().replace("datadog_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("DATADOG_")
        }

    @property
    def endpoints(self):
        return self.COLLECTOR_CONFIG.endpoints

    def __repr__(self):
        """ Print noteworthy configuration items """
        hr = "-" * shutil.get_terminal_size().columns + "\n"
        tpl = "{name:>25} {value:<50}\n"
        string = ""
        string += tpl.format(name="app config:", value=APP_SETTINGS)
        string += tpl.format(name="flask app:", value=FLASK_APP)
        string += tpl.format(name="flask env:", value=self.FLASK_ENV)
        string += tpl.format(
            name="backend:", value=make_url(self.DATABASE_URL_PARAMS).__repr__()
        )
        string += tpl.format(name="collector:", value=self.COLLECTOR_BASE_URL)
        return hr + string + hr


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG_TB_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    """Testing configuration"""

    CONFIG_BASEPATH = "./tests/data"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)
    TESTING = True
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_BASE_URL = "https://api.example.com/v3"
    API_CLIENT_ID = "test_client_id"
    API_CLIENT_SECRET = "test_client_secret"
    API_USERNAME = "username"
    API_PASSWORD = "password"
    API_TOKEN_PATH = "/auth"
    API_DEFAULT_PAGESIZE = 100


class CIConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    """Production configuration"""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERYD_PREFETCH_MULTIPLIER = 8
    CELERYD_CONCURRENCY = 12
    LOG_FORMAT = "json"


if __name__ == "__main__":
    t = TestingConfig()
    t.api_params
