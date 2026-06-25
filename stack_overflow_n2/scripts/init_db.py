import sys
from pathlib import Path
from stack_overflow_n2.src.db import get_connection, init_db

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    with get_connection() as conn:
        init_db(conn)
    print("Banco de dados inicializado com sucesso.")