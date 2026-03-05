# Google Places Lead Exporter (CSV)

Herramienta en Python para buscar negocios en Google Maps usando **Google Places API (Text Search + Details)** y exportar los resultados a un **CSV**.  
Ideal para crear listas de leads por **keyword + ciudades + estado**, con logging para depurar errores y límites de la API.

> Este proyecto **NO** incluye API keys ni datos reales.

---

##  Qué hace
- Pide por terminal:
  - **Google API Key** (obligatoria)
  - **Estado** (2 letras, ej: `NC`)
  - **Keyword** (ej: `roofing`)
  - **Ciudades** (máximo 10)
- Busca: `"<keyword> in <city>, <state>"`
- Obtiene detalles por negocio:
  - Company, Phone, Website, Address, Rating, Reviews, PlaceID, etc.
- Exporta un archivo CSV con nombre:
  - `STATE_keyword_places.csv` (ej: `NC_roofing_places.csv`)
- Guarda logs en:
  - `scraper.log`

---

## Estructura del proyecto
```
places_scraper/
  main.py
  config.py
  prompts.py
  google_places.py
  utils.py
  requirements.txt
```

---

## 🔧 Requisitos
- Python 3.10+ recomendado
- Google Cloud:
  - **Billing habilitado**
  - **Places API** habilitada
  - API Key válida

Instala dependencias:
```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar
Desde la carpeta del proyecto:
```bash
python main.py
```

Ejemplo de entradas:
- Estado: `NC`
- Keyword: `roofing`
- Ciudades: `Charlotte, Raleigh, Durham`

Al finalizar verás:
- `NC_roofing_places.csv`
- `scraper.log`

---

## Campos del CSV
El CSV incluye (puede variar según disponibilidad del negocio):
- `Company`
- `Phone`
- `Website`
- `Address`
- `City`
- `State`
- `Rating`
- `Reviews`
- `BusinessStatus`
- `PlaceID`
- `Source`
- `Keyword`

---

## Logging (scraper.log)
El archivo `scraper.log` ayuda a diagnosticar:
- `REQUEST_DENIED` (billing / API no habilitada / restricciones de key)
- `OVER_QUERY_LIMIT` (rate limit / cuota)
- `INVALID_REQUEST` (token de paginación no activo todavía)
- timeouts / errores de red

---

## Seguridad y buenas prácticas
- **Nunca** subas tu API key a GitHub.
- No publiques CSVs con leads reales (teléfonos/direcciones).
- Agrega estos archivos a `.gitignore`:
  - `*.csv`
  - `scraper.log` / `*.log`

Ejemplo `.gitignore`:
```gitignore
*.csv
scraper.log
*.log
__pycache__/
*.pyc
.venv/
venv/
.env
```

---

## Notas técnicas
- Se usa paginación con `next_page_token` y espera/reintentos.
- Hay throttling (`sleep`) entre requests para reducir rate limiting.
- `requests.Session()` reutiliza conexiones para mejor rendimiento.

---

## Roadmap (ideas)
- Filtro y scoring de leads (pocas reviews / sin website / rating bajo)
- Export a Google Sheets
- Integración directa con GHL (import + tags + pipeline)

---

## Disclaimer
Este proyecto usa Google Places API. Asegúrate de cumplir con los términos de Google y las leyes aplicables en tu jurisdicción.
