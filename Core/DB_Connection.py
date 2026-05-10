import os
import urllib.parse
from sqlalchemy import create_engine


def read_db_config(file_path="config/db_config.txt"):
    config = {}

    if not os.path.exists(file_path):
        raise FileNotFoundError("Database config file not found")

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            config[key.strip().upper()] = value.strip()

    return config


def get_connection():
    cfg = read_db_config()

    # Build ODBC connection string
    conn_str = (
        f"DRIVER={{{cfg['DRIVER']}}};"
        f"SERVER={cfg['SERVER']};"
        f"DATABASE={cfg['DATABASE']};"
    )

    # Trusted or SQL auth
    if cfg.get("TRUSTED_CONNECTION", "yes").lower() == "yes":
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={cfg['USER']};PWD={cfg['PASSWORD']};"

    # Encode for SQLAlchemy
    params = urllib.parse.quote_plus(conn_str)

    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        pool_pre_ping=True,     # avoids stale connections
        pool_recycle=1800       # good for long-running apps
    )

    return engine
