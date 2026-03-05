# funciones para pedir imputs al usiario
import re

def prompt_api_key(logger) -> str:
    key = input("Google API Key (obligatoria): ").strip()
    if not key:
        logger.critical("No ingresaste API Key. Cancelando script.")
        raise SystemExit("No ingresaste API Key. Script cancelado.")
    return key

def prompt_state(logger) -> str:
    state = input("Estado (2 letras, ej: NC): ").strip().upper()
    if not state or len(state) != 2:
        logger.critical("Estado inválido: %s", state)
        raise SystemExit("Estado inválido. Usa 2 letras (ej: NC).")
    return state

def prompt_keyword(logger) -> str:
    kw = input("Keyword (ej: roofing): ").strip()
    if not kw:
        logger.critical("Keyword vacía.")
        raise SystemExit("Keyword vacía. Script cancelado.")
    return kw

def prompt_cities(logger, state: str, max_cities: int) -> list[str]:
    print(f"\n Ciudades (máximo {max_cities}).")
    print("Opción A) Separadas por coma: Charlotte, Raleigh, Durham")
    print("Opción B) ENTER y luego una por línea. ENTER vacío para terminar.\n")

    first = input("Ciudades: ").strip()
    cities = []

    if first:
        cities = [c.strip() for c in first.split(",") if c.strip()]
    else:
        while True:
            c = input("Ciudad (ENTER para terminar): ").strip()
            if not c:
                break
            cities.append(c)

    if not cities:
        logger.critical("No se ingresaron ciudades.")
        raise SystemExit("No ingresaste ciudades. Script cancelado.")

    if len(cities) > max_cities:
        logger.warning("Se ingresaron %s ciudades; truncando a %s.", len(cities), max_cities)
        cities = cities[:max_cities]

    normalized = []
    for c in cities:
        
        if re.search(r",\s*[A-Za-z]{2}\s*$", c):
            normalized.append(c)
        else:
            normalized.append(f"{c}, {state}")

    logger.info("Ciudades finales: %s", normalized)
    return normalized