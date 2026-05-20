import time
import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError

# --- CONFIGURACIÓN GLOBAL ---
JSON_FILE = "creds_nsg.json"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def obtener_cliente_google():
    """Autentica y devuelve el cliente de Google Sheets una sola vez por sesión."""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, SCOPE)
        return gspread.authorize(creds)
    except Exception as exc:
        st.error(f"❌ Error de conexión con Google: {exc}")
        return None


def conectar_libro(id_o_nombre_libro):
    """Conecta a un libro específico por ID o por Nombre."""
    cliente = obtener_cliente_google()
    if not cliente:
        return None
    try:
        # Intenta abrir por llave (ID) primero, si falla intenta por nombre
        try:
            return cliente.open_by_key(id_o_nombre_libro)
        except Exception:
            return cliente.open(id_o_nombre_libro)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.warning(
                "⚠️ Google Sheets alcanzó su límite de lectura. La App usará datos en caché."
            )
        return None


def es_error_cuota(exc):
    mensaje = str(exc).lower()
    return "429" in mensaje or "quota" in mensaje or "requests per minute" in mensaje


def leer_hoja_con_reintentos(hoja, max_intentos=4, pausa_inicial=1.5):
    """Evita que el sistema truene si Google se pone lento (Manejo de cuotas)."""
    ultimo_error = None
    for intento in range(max_intentos):
        try:
            return hoja.get_all_values()
        except APIError as exc:
            ultimo_error = exc
            if not es_error_cuota(exc) or intento == max_intentos - 1:
                raise
            time.sleep(pausa_inicial * (2**intento))
        except Exception as exc:
            ultimo_error = exc
            if not es_error_cuota(exc) or intento == max_intentos - 1:
                raise
            time.sleep(pausa_inicial * (2**intento))

    if ultimo_error:
        raise ultimo_error
    return []


@st.cache_data(ttl=600)  # Se actualiza cada 10 minutos automáticamente
def leer_datos_seguro(id_o_nombre_libro, nombre_hoja, fila_encabezado=0, version=0):
    """Lee los datos de cualquier hoja, extrae encabezados y devuelve un DataFrame limpio."""
    try:
        libro = conectar_libro(id_o_nombre_libro)
        if not libro:
            return pd.DataFrame()

        hoja = libro.worksheet(nombre_hoja)
        datos = leer_hoja_con_reintentos(hoja)
        if len(datos) <= fila_encabezado:
            return pd.DataFrame()

        nombres = datos[fila_encabezado]
        df = pd.DataFrame(datos[fila_encabezado + 1 :])

        # Limpieza estándar de encabezados para toda la plataforma
        df.columns = [
            str(nombre).strip().upper() if nombre else f"COL_{indice}"
            for indice, nombre in enumerate(nombres)
        ]

        # Limpiamos espacios en blanco de todas las celdas
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

        return df
    except Exception as exc:
        st.error(f"No se pudo leer la hoja '{nombre_hoja}': {exc}")
        return pd.DataFrame()


def guardar_fila_seguro(id_o_nombre_libro, nombre_hoja, fila_datos):
    """Escribe una nueva fila en Google Sheets de forma segura."""
    libro = conectar_libro(id_o_nombre_libro)
    if not libro:
        return False
    try:
        libro.worksheet(nombre_hoja).append_row(fila_datos)
        return True
    except Exception as exc:
        st.error(f"Error al guardar el registro: {exc}")
        return False


def sidebar_comun():
    """Renderiza los elementos comunes del sidebar en todas las páginas."""
    import streamlit as st
    import os

    LOGO_FILENAME = "LOGO NSG SFONDO.png"

    with st.sidebar:
        # 1. Logo
        if os.path.exists(LOGO_FILENAME):
            st.image(LOGO_FILENAME, width="stretch")

        # 2. Saludo al usuario
        if "nombre" in st.session_state:
            st.success(f"👤 **{st.session_state['nombre']}**")
            st.caption(f"Rol: {st.session_state.get('rol', 'Usuario')}")

        st.divider()

        # 3. Botón Maestro de Actualizar
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        # 4. Botón de Cerrar Sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()
