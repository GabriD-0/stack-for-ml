import time
import requests
from .config import QUESTIONS_URL, TAGS, PAGE_SIZE, SORT, ORDER, STACK_API_KEY, get_date_range
from .db import get_connection, init_db, upsert_questions

# Busca uma página de perguntas para uma tag. Retorna (items, has_more, backoff ou None).
def fetch_questions_page(tag, fromdate, todate, page=1):
    params = {
        "tagged": tag,
        "fromdate": fromdate,
        "todate": todate,
        "sort": SORT,
        "order": ORDER,
        "pagesize": PAGE_SIZE,
        "page": page,
        "site": "stackoverflow",
    }

    if STACK_API_KEY:
        params["key"] = STACK_API_KEY

    response = requests.get(QUESTIONS_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    backoff = data.get("backoff")
    return data.get("items", []), data.get("has_more", False), backoff


# Coleta todas as páginas para uma tag e persiste no banco de dados.
def collect_tag(tag, fromdate, todate, conn, progress_callback=None):
    page = 1
    total = 0

    while True:
        items, has_more, backoff = fetch_questions_page(tag, fromdate, todate, page)
        if not items:
            break

        questions = []
        for item in items:
            questions.append({
                "question_id": item["question_id"],
                "title": item.get("title", ""),
                "creation_date": item.get("creation_date"),
                "last_activity_date": item.get("last_activity_date"),
                "score": item.get("score", 0),
                "view_count": item.get("view_count", 0),
                "answer_count": item.get("answer_count", 0),
                "is_answered": item.get("is_answered", False),
                "accepted_answer_id": item.get("accepted_answer_id"),
                "tags": item.get("tags", []),
            })

        upsert_questions(conn, questions)
        total += len(questions)

        if progress_callback:
            progress_callback(tag, page, len(questions), total)
        if backoff:
            time.sleep(backoff)
        if not has_more:
            break

        page += 1
        time.sleep(0.05)  # Evita throttling
    return total


# Executa a coleta para todas as tags na janela configurada.
def run_collector(progress_callback=None):
    fromdate, todate = get_date_range()
    with get_connection() as conn:
        init_db(conn)
        grand_total = 0

        for tag in TAGS:
            n = collect_tag(tag, fromdate, todate, conn, progress_callback)
            grand_total += n
        return grand_total


if __name__ == "__main__":
    def log_progress(tag, page, count, total):
        print(f"  {tag}: página {page}, +{count} (total da tag: {total})")

    print("Iniciando coleta Stack Overflow...")
    total = run_collector(progress_callback=log_progress)
    print(f"Coleta concluída. Total de registros processados: {total}")