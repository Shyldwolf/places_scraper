# YS Lead Scraper — Google Places

Herramienta interna de **YS Business Services** para prospectar negocios locales en Google Maps usando la **Google Places API**, clasificar leads automaticamente y exportar a CSV.

> Este proyecto **NO** incluye API keys ni datos reales.

---

## Que hace

- Busca negocios por **keyword + ciudades + estado** en Google Maps
- Clasifica cada lead con un **Score** (Hot / Warm / Cold)
- Genera una **recomendacion de servicio** (Pitch) por cada lead
- Exporta CSV listo para usar en outreach
- Guarda logs en `scraper.log`

---

## Como ejecutar

```bash
# Instalar dependencias (solo la primera vez)
uv sync

# Abrir el launcher
uv run python run.py
```

El launcher te da tres opciones:

```
1  Web UI   (Streamlit — abre en el browser)
2  Terminal (Textual  — corre en la terminal)
3  CLI      (original — inputs manuales)
```

---

## Estructura del proyecto

```
places_scraper/
  run.py            # Launcher — punto de entrada
  app.py            # UI web (Streamlit)
  tui.py            # UI terminal (Textual)
  main.py           # CLI original
  data.py           # Estados y ciudades desde API
  google_places.py  # Llamadas a Google Places API
  utils.py          # slugify, score_lead, recommend_pitch
  config.py         # Constantes, keywords, ciudades fallback
  prompts.py        # Inputs del CLI original
  pyproject.toml    # Dependencias (UV)
  scraper.log       # Log generado al correr
```

---

## Requisitos

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) instalado
- Google Cloud:
  - **Billing habilitado**
  - **Places API** habilitada
  - API Key valida

---

## Campos del CSV generado

| Campo | Descripcion |
|---|---|
| `Company` | Nombre del negocio |
| `Phone` | Telefono |
| `Website` | Website (vacio si no tiene) |
| `Address` | Direccion completa |
| `City` | Ciudad |
| `State` | Estado (abreviacion) |
| `Rating` | Estrellas en Google |
| `Reviews` | Numero de reviews |
| `BusinessStatus` | OPERATIONAL / CLOSED_TEMPORARILY / etc |
| `PlaceID` | ID unico de Google Places |
| `Keyword` | Keyword usada en la busqueda |
| `Score` | Hot / Warm / Cold |
| `Pitch` | Servicio recomendado para ese cliente |

---

## Logica de scoring

| Score | Criterio |
|---|---|
| Hot | Sin website **Y** menos de 15 reviews |
| Warm | Sin website **O** menos de 25 reviews **O** rating < 4.0 |
| Cold | Negocio establecido |

---

## Logica del Pitch (recomendacion de servicio)

| Condicion | Pitch generado |
|---|---|
| Sin website + pocas reviews | `One-Page Website + GBP Optimization + Review System` |
| Sin website | `One-Page Website + GBP Optimization` |
| Pocas reviews | `GBP Optimization + Review System` |
| Rating bajo | `+ Reputation Repair` |
| Todo en orden | `GBP Maintenance` |

---

## Filtros disponibles (Web UI y TUI)

- Solo negocios sin website
- Maximo de reviews (slider)
- Rating minimo
- Filtrar por Score (Hot / Warm / Cold)
- Maximo 10 ciudades por busqueda

---

## Logging

`scraper.log` registra cada request y ayuda a diagnosticar:

- `REQUEST_DENIED` — billing o API no habilitada
- `OVER_QUERY_LIMIT` — rate limit / cuota
- `INVALID_REQUEST` — next_page_token no activo todavia
- Timeouts / errores de red

---

## Seguridad

- **Nunca** subas tu API key a GitHub
- No publiques CSVs con datos reales de clientes

`.gitignore` recomendado:
```
*.csv
scraper.log
*.log
__pycache__/
*.pyc
.venv/
.env
```

---

## Disclaimer

Este proyecto usa Google Places API. Asegurate de cumplir con los terminos de Google y las leyes aplicables en tu jurisdiccion.
