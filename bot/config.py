from decouple import config
from pathlib import Path

TOKEN=config("TOKEN")
ADMIN_ID=config("ADMIN_ID", cast=lambda v: [s.strip() for s in v.split(',')])
CHANEL_ID=config("CHANEL_ID")
MYSQL_URI=config("MYSQL_URI")

REDIS_PORT=config("REDIS_PORT")

I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'