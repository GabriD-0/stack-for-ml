import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TAGS = ["python", "reactjs", "docker", "vue.js"]
MONTHS = int(os.getenv("MONTHS", "6")) # Janela temporal em meses (6 a 12)
API = "https://api.stackexchange.com/2.3"
QUESTIONS_URL = f"{API}/questions"

# Parâmetros padrão da API
PAGE_SIZE = 100
SORT = "creation"
ORDER = "desc"
STACK_API_KEY = os.getenv("STACK_API_KEY")

# Caminho do banco SQLite
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "stackoverflow.db"
SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(DEFAULT_DB_PATH)))


def get_date_range():
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=MONTHS * 30)
    return int(from_date.timestamp()), int(to_date.timestamp())