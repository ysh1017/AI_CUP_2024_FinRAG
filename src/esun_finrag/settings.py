"""Configuration & Logger helpers."""
from __future__ import annotations
import configparser
import logging
from pathlib import Path

CONFIG_PATH = Path(__file__).with_suffix('').parent.parent.parent / "cfg.ini"
LOG_PATH = Path(__file__).with_suffix('').parent.parent.parent / "logs/esun_finrag.log"
LOG_PATH.parent.mkdir(exist_ok=True)

cfg = configparser.ConfigParser()
if CONFIG_PATH.exists():
    cfg.read(CONFIG_PATH)
else:
    cfg.read_dict({"weaviate": {"url": "http://127.0.0.1:8882"}})

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s:%(lineno)d :: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("esun_finrag")
