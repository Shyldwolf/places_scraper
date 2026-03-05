import csv
import time

from config import (
    MAX_CITIES,
    DETAILS_DELAY_SECONDS,
    NEXT_PAGE_INITIAL_WAIT,
    NEXT_PAGE_MAX_WAIT,
)
from utils import slugify, setup_logger
from prompts import prompt_api_key, prompt_state, prompt_keyword, prompt_cities
from google_places import text_search, place_details, wait_for_next_page

def main():
    logger = setup_logger()
    logger.info("=== Iniciando Google Places Scraper ===")

    api_key = prompt_api_key(logger)
    state = prompt_state(logger)
    keyword = prompt_keyword(logger)
    cities = prompt_cities(logger, state, MAX_CITIES)

    rows = []
    seen_place_ids = set()

    for city in cities:
        query = f"{keyword} in {city}"
        logger.info("Searching: %s", query)

        data = text_search(logger, api_key, query)

        while True:
            results = data.get("results", [])
            logger.info("Found %s results on this page", len(results))

            for item in results:
                pid = item.get("place_id")
                if not pid or pid in seen_place_ids:
                    continue
                seen_place_ids.add(pid)

                try:
                    details = place_details(logger, api_key, pid).get("result", {})
                except Exception as e:
                    logger.warning("Details error for place_id=%s: %s", pid, e)
                    continue

                rows.append({
                    "Company": details.get("name", ""),
                    "Phone": details.get("formatted_phone_number", ""),
                    "Website": details.get("website", ""),
                    "Address": details.get("formatted_address", ""),
                    "City": city.replace(f", {state}", ""),
                    "State": state,
                    "Rating": details.get("rating", ""),
                    "Reviews": details.get("user_ratings_total", ""),
                    "BusinessStatus": details.get("business_status", ""),
                    "PlaceID": pid,
                    "Source": "Google Places API (Text Search)",
                    "Keyword": keyword,
                })

                time.sleep(DETAILS_DELAY_SECONDS)

            token = data.get("next_page_token")
            if not token:
                break

            logger.info("next_page_token detectado. Cargando siguiente página...")
            time.sleep(NEXT_PAGE_INITIAL_WAIT)
            data = wait_for_next_page(logger, api_key, token, query, NEXT_PAGE_MAX_WAIT)

    if rows:
        filename = f"{state}_{slugify(keyword)}_places.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        logger.info("Saved %s leads to %s", len(rows), filename)
        print(f"\n Saved {len(rows)} leads to {filename}")
        print("Log guardado en: scraper.log")
    else:
        logger.warning("No rows collected. Revisa Billing/APIs/permisos de la key.")
        print("\n No rows collected. Revisa Billing, Places API enabled y permisos de la key.")
        print("Revisa el log: scraper.log")

if __name__ == "__main__":
    main()