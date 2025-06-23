1 / 0  # fuerza un error fatal de división por cero

# --- shill_routes.py ---
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os

from services.telegram_simulado import enviar_mensajes_simulados
from services.airtable_projects import obtener_proyectos
from services.telegram_manager import verificar_sesiones
from pyairtable import Table
from pyairtable import Table
from services.configuracion_shill import obtener_configuracion_shill


# 📦 Importar funciones desde el servicio Airtable
from services.airtable_projects import (
    obtener_proyectos,
    agregar_proyecto as airtable_agregar_proyecto,
    eliminar_proyecto as eliminar_proyecto_airtable
)

shill_bp = Blueprint('shill', __name__, url_prefix='/shill')


@shill_bp.route('/')
def shill_home():
    if 'username' not in session:
        flash('Debes iniciar sesión para acceder.', 'warning')
        return redirect(url_for('auth.login'))

    proyectos = obtener_proyectos()
    return render_template("Shill/index.html", proyectos=proyectos)


@shill_bp.route('/<proyecto_alias>', methods=['GET', 'POST'])
def shill_proyecto(proyecto_alias):
    estado = None
    preview = []

    # Buscar el proyecto en Airtable según el alias
    proyectos = obtener_proyectos()
    proyecto_en_uso = next((p for p in proyectos if p["alias"] == proyecto_alias), None)

    if not proyecto_en_uso:
        flash(f"❌ Proyecto '{proyecto_alias}' no encontrado.", "danger")
        return redirect(url_for("shill.shill_home"))

    if request.method == 'POST':
        texto = request.form.get('texto', '').strip()
        accion = request.form.get('accion')

        if texto:
            # Mostrar vista previa
            lineas = texto.split('\n')
            for linea in lineas:
                if ":" in linea:
                    parte = linea.split(":", 1)
                    session_tag = parte[0].strip()
                    mensaje = parte[1].strip()
                    preview.append((session_tag, mensaje))

            if accion == "confirmar":
                grupo = proyecto_en_uso.get("telegram")
                if grupo:
                     from services.telegram_simulado import enviar_mensajes_en_hilo
                     enviar_mensajes_en_hilo(texto, grupo)
                     estado = "🕒 Envío iniciado en segundo plano."
                else:
                     estado = "❌ El proyecto no tiene grupo de Telegram configurado."

    config = obtener_configuracion_shill()

    return render_template(
        "Shill/proyecto.html",
        nombre=proyecto_en_uso["nombre"],
        estado=estado,
        preview=preview,
        config=config
    )




@shill_bp.route('/agregar', methods=['POST'])
def agregar_proyecto():
    nombre = request.form.get('nuevo_proyecto', '').strip()
    alias = request.form.get('nuevo_alias', '').strip()
    telegram = request.form.get('nuevo_telegram', '').strip()

    print("FORM INPUTS:", nombre, alias, telegram)

    if nombre and alias and telegram:
        try:
            airtable_agregar_proyecto(nombre, alias, telegram)
            flash(f"✅ Proyecto '{nombre}' agregado con éxito.", "success")
        except Exception as e:
            print("ERROR:", e)
            flash(f"❌ Error al agregar el proyecto: {e}", "danger")
    else:
        flash("⚠️ Todos los campos son obligatorios (nombre, alias, telegram).", "warning")

    return redirect(url_for('shill.shill_home'))



@shill_bp.route('/eliminar/<proyecto_id>', methods=['POST'])
def eliminar_proyecto(proyecto_id):
    try:
        eliminar_proyecto_airtable(proyecto_id)
        flash(f"✅ Proyecto eliminado.", "success")
    except Exception as e:
        flash(f"❌ Error al eliminar: {e}", "danger")

    return redirect(url_for('shill.shill_home'))

@shill_bp.route('/admin/sesiones', methods=['GET', 'POST'])
def administrar_sesiones():
    print("⚙️  Ingresó a la ruta de sesiones")

    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Cuentas Telegram")

    if request.method == 'POST':
        alias = request.form.get("alias", "").strip()
        session = request.form.get("session", "").strip()
        activa = request.form.get("activa") == "on"

        print("📤 Datos recibidos:", alias, session[:10], "Activa:", activa)

        if alias and session:
            try:
                table.create({
                    "Alias": alias,
                    "Session": session,
                    "Activa": activa
                })
                flash(f"✅ Sesión '{alias}' agregada con éxito", "success")
            except Exception as e:
                print("❌ ERROR AL GUARDAR:", e)
                flash(f"❌ Error al agregar sesión: {e}", "danger")
        else:
            flash("⚠️ Todos los campos son obligatorios", "warning")

    sesiones = table.all()

    # ✅ Ordenar por número extraído del alias
    import re
    def extraer_numero(alias):
        match = re.search(r'\d+', alias)
        return int(match.group()) if match else 0

    sesiones.sort(key=lambda r: extraer_numero(r["fields"].get("Alias", "")))

    aliases = [r["fields"].get("Alias", "") for r in sesiones]

    return render_template("admin/Sesiones.html", sesiones=sesiones, aliases=aliases)


@shill_bp.route('/admin/eliminar_sesion/<session_id>', methods=['POST'])
def eliminar_sesion(session_id):
    from pyairtable import Table

    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Cuentas Telegram")

    try:
        table.delete(session_id)
        flash("✅ Sesión eliminada correctamente.", "success")
    except Exception as e:
        flash(f"❌ Error al eliminar sesión: {e}", "danger")

    return redirect(url_for("shill.administrar_sesiones"))

@shill_bp.route('/admin/verificar_sesiones', methods=['POST'])
def verificar_sesiones_route():
    from services.telegram_manager import verificar_sesiones
    from pyairtable import Table

    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Cuentas Telegram")

    sesiones = table.all()

    cuentas = {
        r["fields"]["Alias"]: r["fields"]["Session"]
        for r in sesiones
        if r["fields"].get("Activa") and "Alias" in r["fields"] and "Session" in r["fields"]
    }

    resultados = verificar_sesiones(cuentas)  # {alias: True/False}

    mensaje = ""
    for alias, ok in resultados.items():
        if ok:
            mensaje += f"✅ {alias} funciona correctamente\n"
        else:
            mensaje += f"❌ {alias} no se pudo conectar\n"

    flash(mensaje.replace("\n", "<br>"), "info")
    return redirect(url_for('shill.administrar_sesiones'))

@shill_bp.route('/configuracion', methods=['GET', 'POST'])
def configurar_shill():
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "ConfiguracionShill")

    # Tomamos la primera fila (única)
    registros = table.all()
    if not registros:
        return "⚠️ No hay configuración cargada aún."
    
    record_id = registros[0]['id']
    campos = registros[0]['fields']

    if request.method == 'POST':
        data = {
            "delay_min": int(request.form.get("delay_min", 1)),
            "delay_max": int(request.form.get("delay_max", 5)),
            "tiempo_max_conversacion": float(request.form.get("tiempo_max_conversacion", 1)),
            "probabilidad_respuesta": int(request.form.get("probabilidad_respuesta", 0)),
            "probabilidad_reaccion": int(request.form.get("probabilidad_reaccion", 0)),
            "reacciones": request.form.get("reacciones", ""),
            "usar_bloques": bool(request.form.get("usar_bloques")),
            "min_intervalo_bloque": int(request.form.get("min_intervalo_bloque", 10)),
            "mensajes_por_bloque": int(request.form.get("mensajes_por_bloque", 5)),
        }

        table.update(record_id, data)
        flash("✅ Configuración actualizada correctamente", "success")
        campos = data  # actualizar vista

    return render_template("Shill/configuracion.html", config=campos)

@shill_bp.route('/reordenar', methods=['POST'])
def reordenar_proyectos():
    from pyairtable import Table
    import os
    data = request.get_json()

    if not isinstance(data, list):
        return {"error": "Formato inválido"}, 400

    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Proyectos")

    for orden, id_proyecto in enumerate(data):
        try:
            table.update(id_proyecto, {"orden": orden + 1})
        except Exception as e:
            print(f"❌ Error actualizando {id_proyecto}: {e}")

    return {"success": True}, 200