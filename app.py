import time
import logging
import pandas as pd
import streamlit as st

from config import (
    MAX_CITIES,
    DETAILS_DELAY_SECONDS,
    NEXT_PAGE_INITIAL_WAIT,
    NEXT_PAGE_MAX_WAIT,
    KEYWORDS,
    METRO_AREAS,
)
from data import US_STATES, fetch_cities
from utils import slugify, score_lead, recommend_pitch, missing_notes
from google_places import text_search, place_details, wait_for_next_page

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YS Lead Scraper",
    page_icon="📍",
    layout="wide",
)

# ── Logger (solo a archivo, no a consola) ─────────────────────────────────────
@st.cache_resource
def get_logger():
    logger = logging.getLogger("places_scraper")
    if not logger.handlers:
        handler = logging.FileHandler("scraper.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger()


@st.cache_data(show_spinner="Loading cities...")
def _get_cities(state_abbr: str) -> list[str]:
    return fetch_cities(state_abbr)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📍 YS Business Services — Lead Scraper")
st.caption("Busca negocios en Google Maps y exporta leads calificados a CSV.")

st.divider()

# ── Sidebar: configuracion ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuracion")

    api_key = st.text_input(
        "Google API Key",
        type="password",
        placeholder="AIza...",
        help="Tu Google Cloud API Key con Places API habilitada.",
    )

    st.divider()

    state = st.selectbox(
        "Estado",
        options=list(US_STATES.keys()),
        index=list(US_STATES.keys()).index("NC"),
    )

    keyword_option = st.selectbox(
        "Keyword (nicho)",
        options=KEYWORDS + ["Otro..."],
    )

    if keyword_option == "Otro...":
        keyword = st.text_input("Escribe el keyword", placeholder="ej: landscaping")
    else:
        keyword = keyword_option

    st.divider()

    available_cities = _get_cities(state)
    selected_cities = st.multiselect(
        f"Ciudades de {state} (max {MAX_CITIES})",
        options=available_cities,
        default=available_cities[:3],
        help=f"Selecciona hasta {MAX_CITIES} ciudades.",
    )

    # Sugerencias de ciudades cercanas
    if selected_cities:
        state_metros = METRO_AREAS.get(state, {})
        nearby = set()
        for city in selected_cities:
            for neighbor in state_metros.get(city, []):
                if neighbor not in selected_cities and neighbor in available_cities:
                    nearby.add(neighbor)
        if nearby:
            st.caption("Ciudades cercanas sugeridas:")
            suggested = st.multiselect(
                "Agregar al area?",
                options=sorted(nearby),
                default=[],
                key="nearby_suggestions",
            )
            selected_cities = list(set(selected_cities + suggested))

    too_many = len(selected_cities) > MAX_CITIES
    if too_many:
        st.error(f"Seleccionaste {len(selected_cities)} ciudades. El maximo es {MAX_CITIES}. Quita {len(selected_cities) - MAX_CITIES} para continuar.")

    st.divider()

    st.subheader("🎯 Filtros de exportacion")
    only_no_website = st.checkbox("Solo sin website", value=False)
    max_reviews = st.slider("Reviews maximas", min_value=0, max_value=200, value=200, step=5)
    min_rating = st.slider("Rating minimo", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
    score_filter = st.multiselect(
        "Score del lead",
        options=["Hot", "Warm", "Cold"],
        default=["Hot", "Warm", "Cold"],
    )

# ── Main: validacion y run ────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    ready = api_key and keyword and selected_cities and not too_many
    run = st.button(
        "🚀 Buscar Leads",
        disabled=not ready,
        use_container_width=True,
        type="primary",
    )

with col2:
    if not api_key:
        st.warning("Falta API Key")
    elif not keyword:
        st.warning("Falta keyword")
    elif not selected_cities:
        st.warning("Selecciona ciudades")
    else:
        st.success(f"{len(selected_cities)} ciudad(es) seleccionada(s)")

# ── Scraper ───────────────────────────────────────────────────────────────────
if run:
    normalized_cities = [
        c if c.endswith(f", {state}") else f"{c}, {state}"
        for c in selected_cities
    ]

    status_box   = st.empty()
    progress_bar = st.progress(0)
    counter_box  = st.empty()

    rows = []
    seen_place_ids = set()
    total_cities = len(normalized_cities)

    for city_idx, city in enumerate(normalized_cities):
        query = f"{keyword} in {city}"
        status_box.info(f"🔍 Buscando: **{query}**")
        logger.info("Searching: %s", query)

        try:
            data = text_search(logger, api_key, query)
        except Exception as e:
            st.error(f"Error buscando {city}: {e}")
            logger.error("text_search error for %s: %s", city, e)
            continue

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
                    logger.warning("Details error place_id=%s: %s", pid, e)
                    continue

                row = {
                    "Company":        details.get("name", ""),
                    "Phone":          details.get("formatted_phone_number", ""),
                    "Website":        details.get("website", ""),
                    "Address":        details.get("formatted_address", ""),
                    "City":           city.replace(f", {state}", ""),
                    "State":          state,
                    "Rating":         details.get("rating", ""),
                    "Reviews":        details.get("user_ratings_total", ""),
                    "BusinessStatus": details.get("business_status", ""),
                    "GoogleMapsURL":  details.get("url", ""),
                    "PlaceID":        pid,
                    "Keyword":        keyword,
                }
                row["Score"]   = score_lead(row)
                row["Pitch"]   = recommend_pitch(row)
                row["Notes"]   = missing_notes(row)
                rows.append(row)

                counter_box.metric("Leads encontrados", len(rows))
                time.sleep(DETAILS_DELAY_SECONDS)

            token = data.get("next_page_token")
            if not token:
                break

            logger.info("next_page_token detectado. Cargando siguiente pagina...")
            time.sleep(NEXT_PAGE_INITIAL_WAIT)
            data = wait_for_next_page(logger, api_key, token, query, NEXT_PAGE_MAX_WAIT)

        progress_bar.progress((city_idx + 1) / total_cities)

    status_box.empty()
    progress_bar.empty()
    counter_box.empty()

    if not rows:
        st.error("No se encontraron resultados. Revisa tu API Key, Billing y permisos.")
    else:
        df = pd.DataFrame(rows)

        # Normalizar tipos para evitar errores Arrow
        df["Rating"]  = pd.to_numeric(df["Rating"],  errors="coerce")
        df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").astype("Int64")

        # Aplicar filtros
        if only_no_website:
            df = df[df["Website"].astype(str).str.strip() == ""]
        if max_reviews < 200:
            df = df[pd.to_numeric(df["Reviews"], errors="coerce").fillna(0) <= max_reviews]
        if min_rating > 0:
            df = df[pd.to_numeric(df["Rating"], errors="coerce").fillna(0) >= min_rating]
        if score_filter:
            df = df[df["Score"].isin(score_filter)]

        # ── Resultados ────────────────────────────────────────────────────────
        st.divider()
        st.subheader(f"📊 Resultados — {len(df)} leads")

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Total", len(df))
        mcol2.metric("🔥 Hot", len(df[df["Score"] == "Hot"]))
        mcol3.metric("Warm", len(df[df["Score"] == "Warm"]))
        mcol4.metric("Cold", len(df[df["Score"] == "Cold"]))

        # Color por score
        def color_score(val):
            colors = {"Hot": "background-color: #ff4b4b; color: white",
                      "Warm": "background-color: #ffa500; color: white",
                      "Cold": "background-color: #d3d3d3; color: black"}
            return colors.get(val, "")

        styled = df.style.map(color_score, subset=["Score"])
        st.dataframe(styled, width="stretch", height=450)

        # ── Descarga ──────────────────────────────────────────────────────────
        filename = f"{state}_{slugify(keyword)}_places.csv"
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            width="stretch",
        )

        logger.info("Saved %s leads — file: %s", len(df), filename)
