"""
YS Lead Scraper — Textual TUI
Corre con: uv run python tui.py
"""
from __future__ import annotations

import csv
import time
import logging

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    SelectionList,
    Static,
)
from textual.widgets.selection_list import Selection

from config import (
    KEYWORDS,
    MAX_CITIES,
    DETAILS_DELAY_SECONDS,
    NEXT_PAGE_INITIAL_WAIT,
    NEXT_PAGE_MAX_WAIT,
)
from data import US_STATES, fetch_cities
from utils import slugify, score_lead, recommend_pitch
from google_places import text_search, place_details, wait_for_next_page


class YSLeadScraper(App):

    CSS = """
    Screen { layout: vertical; }

    #body {
        layout: horizontal;
        height: 1fr;
    }

    #sidebar {
        width: 40;
        background: $panel;
        border-right: tall $primary;
        padding: 1 2;
        overflow-y: auto;
    }

    #main {
        padding: 1 2;
        width: 1fr;
    }

    .lbl {
        color: $text-muted;
        margin-top: 1;
        text-style: bold;
    }

    #city-list {
        height: 14;
        border: tall $surface-lighten-2;
        margin-bottom: 1;
    }

    #run-btn { margin-top: 1; width: 100%; }
    #save-btn { margin-top: 1; width: 100%; }

    #status  { height: 1; color: $warning;  margin-bottom: 1; }
    #metrics { height: 1; color: $success;  margin-bottom: 1; }
    #progress { margin-bottom: 1; }

    DataTable { height: 1fr; }
    """

    TITLE = "YS Business Services — Lead Scraper"
    BINDINGS = [("q", "quit", "Quit"), ("s", "action_save_csv", "Save CSV")]

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict] = []
        self._logger = self._make_logger()

    def _make_logger(self) -> logging.Logger:
        logger = logging.getLogger("places_scraper_tui")
        if not logger.handlers:
            h = logging.FileHandler("scraper.log", encoding="utf-8")
            h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            logger.addHandler(h)
            logger.setLevel(logging.INFO)
        return logger

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Label("API Key", classes="lbl")
                yield Input(placeholder="AIza...", password=True, id="api-key")

                yield Label("State", classes="lbl")
                yield Select(
                    [(abbr, abbr) for abbr in US_STATES],
                    id="state-select",
                    value="NC",
                )

                yield Label("Keyword", classes="lbl")
                yield Select(
                    [(kw, kw) for kw in KEYWORDS] + [("Other...", "__custom__")],
                    id="keyword-select",
                    value=KEYWORDS[0],
                )

                yield Label("Custom keyword", classes="lbl")
                yield Input(placeholder="ej: landscaping", id="custom-kw")

                yield Label(f"Cities (scroll · max {MAX_CITIES})", classes="lbl")
                yield SelectionList[str](id="city-list")

                yield Label("Max reviews  (0 = all)", classes="lbl")
                yield Input(value="0", id="max-reviews")

                yield Button("▶  Run Scraper", id="run-btn", variant="primary")
                yield Button("⬇  Save CSV",   id="save-btn", variant="success", disabled=True)

            with Vertical(id="main"):
                yield Static("Ready — configure and press Run.", id="status")
                yield ProgressBar(total=100, show_eta=False, id="progress")
                yield Static("", id="metrics")
                yield DataTable(id="results-table", zebra_stripes=True)

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Company", "Phone", "Website", "City", "Rating", "Reviews", "Score", "Pitch")
        self._load_cities("NC")

    # ── State change → reload cities ─────────────────────────────────────────

    @on(Select.Changed, "#state-select")
    def on_state_changed(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            self._load_cities(str(event.value))

    @work(thread=True)
    def _load_cities(self, state: str) -> None:
        self.call_from_thread(self._set_status, f"Loading cities for {state}...")
        cities = fetch_cities(state)
        self.call_from_thread(self._populate_cities, cities)

    def _populate_cities(self, cities: list[str]) -> None:
        city_list = self.query_one("#city-list", SelectionList)
        city_list.clear_options()
        for city in cities:
            city_list.add_option(Selection(city, city, initial_state=False))
        self._set_status(f"Ready — {len(cities)} cities loaded.")

    # ── Run button ────────────────────────────────────────────────────────────

    @on(Button.Pressed, "#run-btn")
    def on_run(self) -> None:
        api_key = self.query_one("#api-key", Input).value.strip()
        if not api_key:
            self._set_status("⚠  API Key required.")
            return

        state_val = self.query_one("#state-select", Select).value
        state = str(state_val) if state_val is not Select.BLANK else ""
        if not state:
            self._set_status("⚠  Select a state.")
            return

        kw_val = self.query_one("#keyword-select", Select).value
        custom_kw = self.query_one("#custom-kw", Input).value.strip()
        keyword = custom_kw if kw_val == "__custom__" else str(kw_val)
        if not keyword:
            self._set_status("⚠  Enter a keyword.")
            return

        city_list = self.query_one("#city-list", SelectionList)
        selected_cities = [str(v) for v in city_list.selected]
        if not selected_cities:
            self._set_status("⚠  Select at least one city.")
            return
        if len(selected_cities) > MAX_CITIES:
            self._set_status(f"⚠  Max {MAX_CITIES} cities. You selected {len(selected_cities)} — remove {len(selected_cities) - MAX_CITIES}.")
            return

        try:
            max_reviews = int(self.query_one("#max-reviews", Input).value or "0")
        except ValueError:
            max_reviews = 0

        # Reset UI
        self.query_one("#results-table", DataTable).clear()
        self.query_one("#metrics", Static).update("")
        self.query_one("#save-btn", Button).disabled = True
        self.query_one("#run-btn", Button).disabled = True
        self.query_one(ProgressBar).update(progress=0)
        self._rows = []

        self._scrape(api_key, keyword, selected_cities, state, max_reviews)

    # ── Scraper (background thread) ───────────────────────────────────────────

    @work(thread=True)
    def _scrape(
        self,
        api_key: str,
        keyword: str,
        cities: list[str],
        state: str,
        max_reviews: int,
    ) -> None:
        seen: set[str] = set()
        total = len(cities)

        for idx, city in enumerate(cities):
            query = f"{keyword} in {city}, {state}"
            self.call_from_thread(self._set_status, f"Searching {city}…")
            self._logger.info("Searching: %s", query)

            try:
                data = text_search(self._logger, api_key, query)
            except Exception as exc:
                self._logger.error("text_search error %s: %s", city, exc)
                continue

            while True:
                for item in data.get("results", []):
                    pid = item.get("place_id")
                    if not pid or pid in seen:
                        continue
                    seen.add(pid)

                    try:
                        details = place_details(self._logger, api_key, pid).get("result", {})
                    except Exception as exc:
                        self._logger.warning("details error %s: %s", pid, exc)
                        continue

                    reviews_raw = details.get("user_ratings_total", 0) or 0
                    if max_reviews > 0 and int(reviews_raw) > max_reviews:
                        time.sleep(DETAILS_DELAY_SECONDS)
                        continue

                    row = {
                        "Company":        details.get("name", ""),
                        "Phone":          details.get("formatted_phone_number", ""),
                        "Website":        details.get("website", ""),
                        "Address":        details.get("formatted_address", ""),
                        "City":           city,
                        "State":          state,
                        "Rating":         details.get("rating", ""),
                        "Reviews":        reviews_raw,
                        "BusinessStatus": details.get("business_status", ""),
                        "PlaceID":        pid,
                        "Keyword":        keyword,
                        "Score":          "",
                    }
                    row["Score"] = score_lead(row)
                    row["Pitch"] = recommend_pitch(row)
                    self._rows.append(row)
                    self.call_from_thread(self._add_row, row)
                    time.sleep(DETAILS_DELAY_SECONDS)

                token = data.get("next_page_token")
                if not token:
                    break
                time.sleep(NEXT_PAGE_INITIAL_WAIT)
                data = wait_for_next_page(self._logger, api_key, token, query, NEXT_PAGE_MAX_WAIT)

            self.call_from_thread(
                self.query_one(ProgressBar).update,
                progress=int((idx + 1) / total * 100),
            )

        self.call_from_thread(self._scrape_done)

    # ── UI update helpers (called from thread) ────────────────────────────────

    def _add_row(self, row: dict) -> None:
        score_label = "🔥 Hot" if row["Score"] == "Hot" else row["Score"]
        self.query_one("#results-table", DataTable).add_row(
            row["Company"],
            row["Phone"],
            "Yes" if row["Website"] else "No",
            row["City"],
            str(row["Rating"]),
            str(row["Reviews"]),
            score_label,
            row["Pitch"],
        )
        hot  = sum(1 for r in self._rows if r["Score"] == "Hot")
        warm = sum(1 for r in self._rows if r["Score"] == "Warm")
        cold = sum(1 for r in self._rows if r["Score"] == "Cold")
        self.query_one("#metrics", Static).update(
            f"Total: {len(self._rows)}   🔥 Hot: {hot}   Warm: {warm}   Cold: {cold}"
        )

    def _set_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)

    def _scrape_done(self) -> None:
        self._set_status(f"Done!  {len(self._rows)} leads found.")
        self.query_one("#run-btn", Button).disabled = False
        if self._rows:
            self.query_one("#save-btn", Button).disabled = False

    # ── Save CSV ──────────────────────────────────────────────────────────────

    @on(Button.Pressed, "#save-btn")
    def on_save(self) -> None:
        self.action_save_csv()

    def action_save_csv(self) -> None:
        if not self._rows:
            self._set_status("No results to save.")
            return

        state_val = self.query_one("#state-select", Select).value
        kw_val    = self.query_one("#keyword-select", Select).value
        custom_kw = self.query_one("#custom-kw", Input).value.strip()
        state   = str(state_val) if state_val is not Select.BLANK else "XX"
        keyword = custom_kw if kw_val == "__custom__" else str(kw_val)

        filename = f"{state}_{slugify(keyword)}_places.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self._rows[0].keys()))
            writer.writeheader()
            writer.writerows(self._rows)

        self._set_status(f"Saved {len(self._rows)} leads → {filename}")
        self._logger.info("Saved %s leads to %s", len(self._rows), filename)


if __name__ == "__main__":
    YSLeadScraper().run()
