import os
from pyairtable import Table

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "ConfiguracionShill")

def obtener_configuracion_shill():
    registros = table.all()
    if not registros:
        raise Exception("No hay configuración cargada en ConfiguracionShill.")

    campos = registros[0]["fields"]

    return {
        "delay_min": int(campos.get("delay_min", 1)),
        "delay_max": int(campos.get("delay_max", 3)),
        "tiempo_max_conversacion": float(campos.get("tiempo_max_conversacion", 2)),  # en horas
        "probabilidad_respuesta": int(campos.get("probabilidad_respuesta", 0)),
        "probabilidad_reaccion": int(campos.get("probabilidad_reaccion", 0)),
        "reacciones": [r.strip() for r in campos.get("reacciones", "").split(",") if r.strip()],
        "usar_bloques": campos.get("usar_bloques", False),
        "min_intervalo_bloque": int(campos.get("min_intervalo_bloque", 15)),
        "mensajes_por_bloque": int(campos.get("mensajes_por_bloque", 5)),
    }
