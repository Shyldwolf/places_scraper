
import time
import requests
from config import (
    TEXTSEARCH_URL,
    DETAILS_URL,
    DEFAULT_TIMEOUT,
    TEXTSEARCH_RETRIES,
    DETAILS_RETRIES,
    BACKOFF_BASE,
)

SESSION = requests.Session()

def safe_get(logger, url, params, timeout=DEFAULT_TIMEOUT, retries=6, backoff=BACKOFF_BASE):
    """
    GET robusto con retries para:
    - OVER_QUERY_LIMIT (rate limit)
    - INVALID_REQUEST (next_page_token aún no activo)
    - errores de red / timeouts
    """
    last_data = None

    for attempt in range(1, retries + 1):
        try:
            r = SESSION.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            last_data = data

            status = data.get("status", "")
            if status in ("OK", "ZERO_RESULTS"):
                return data

            if status in ("OVER_QUERY_LIMIT", "INVALID_REQUEST"):
                wait_s = backoff * attempt
                logger.warning(
                    "Retry %s/%s | status=%s | wait=%ss | error=%s",
                    attempt, retries, status, wait_s, data.get("error_message", "")
                )
                time.sleep(wait_s)
                continue

           
            logger.error("Google API error (no-retry): status=%s error=%s", status, data.get("error_message", ""))
            raise RuntimeError(f"Google API error: status={status}, error={data.get('error_message')}")

        except requests.exceptions.RequestException as e:
            wait_s = backoff * attempt
            logger.warning("HTTP error attempt %s/%s: %s | wait=%ss", attempt, retries, e, wait_s)
            time.sleep(wait_s)

    logger.error("safe_get agotó retries. Última respuesta: %s", last_data)
    return last_data or {}

def text_search(logger, api_key: str, query: str, page_token: str | None = None) -> dict:
    params = {"query": query, "key": api_key}
    if page_token:
        params["pagetoken"] = page_token
    return safe_get(logger, TEXTSEARCH_URL, params=params, retries=TEXTSEARCH_RETRIES, backoff=1.5)

def place_details(logger, api_key: str, place_id: str) -> dict:
    fields = ",".join([
        "name",
        "formatted_phone_number",
        "website",
        "formatted_address",
        "rating",
        "user_ratings_total",
        "business_status",
    ])
    params = {"place_id": place_id, "fields": fields, "key": api_key}
    return safe_get(logger, DETAILS_URL, params=params, retries=DETAILS_RETRIES, backoff=BACKOFF_BASE)

def wait_for_next_page(logger, api_key: str, token: str, query: str, max_wait: int) -> dict:
    """
    Reintenta hasta que el next_page_token esté activo o se acabe max_wait.
    """
    start = time.time()
    while True:
        data = text_search(logger, api_key, query, page_token=token)
        status = data.get("status", "")
        if status in ("OK", "ZERO_RESULTS"):
            return data

        if time.time() - start > max_wait:
            logger.warning("next_page_token no se activó a tiempo. status=%s", status)
            return data

        logger.info("Esperando activación del next_page_token... status=%s", status)
        time.sleep(2)