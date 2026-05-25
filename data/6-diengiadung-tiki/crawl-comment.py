from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "result" / "product_id_ncds.csv"
OUTPUT_FILE = BASE_DIR / "result" / "comments_data_ncds.csv"

MAX_WORKERS = 12
MAX_PAGES = 10
REQUEST_TIMEOUT = 15
RETRY_TIMES = 3

cookies = {
    "TIKI_GUEST_TOKEN": "8jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY",
    "TOKENS": "{%22access_token%22:%228jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY%22%2C%22expires_in%22:157680000%2C%22expires_at%22:1763654224277%2C%22guest_token%22:%228jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY%22}",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://tiki.vn/dien-gia-dung/c1882",
    "x-guest-token": "8jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY",
    "Connection": "keep-alive",
}


def create_session():
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS)
    session.mount("https://", adapter)
    session.headers.update(headers)
    session.cookies.update(cookies)
    return session


def comment_parser(comment, product_id):
    return {
        "product_id": product_id,
        "id": comment.get("id"),
        "title": comment.get("title"),
        "content": comment.get("content"),
        "rating": comment.get("rating"),
    }


def fetch_page(session, product_id, page):
    params = {
        "product_id": product_id,
        "sort": "score|desc,id|desc,stars|all",
        "page": page,
        "limit": 20,
        "include": "comments",
    }

    for attempt in range(RETRY_TIMES):
        try:
            response = session.get(
                "https://tiki.vn/api/v2/reviews",
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                return response.json().get("data") or []
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(0.5 * (attempt + 1))
                continue
            return []
        except requests.RequestException:
            time.sleep(0.5 * (attempt + 1))
    return []


def crawl_product(product_id):
    session = create_session()
    comments = []

    for page in range(1, MAX_PAGES + 1):
        page_comments = fetch_page(session, product_id, page)
        if not page_comments:
            break

        for comment in page_comments:
            rating = comment.get("rating")
            if rating is not None and int(rating) <= 3:
                comments.append(comment_parser(comment, product_id))

    session.close()
    return comments


def main():
    df_id = pd.read_csv(INPUT_FILE)
    product_ids = df_id["id"].dropna().astype(int).drop_duplicates().tolist()

    result = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(crawl_product, product_id) for product_id in product_ids]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Crawl comments"):
            result.extend(future.result())

    pd.DataFrame(result).to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(result)} comments to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
