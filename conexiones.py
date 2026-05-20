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
        # 1. Intentar leer desde los Secrets de la nube de Streamlit
        if "gcp_service_account" in st.secrets:
            info_creds = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info_creds, SCOPE)
            return gspread.authorize(creds)

        # 2. Si no está en la nube, intentar leer el archivo local para desarrollo
        else:
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
        if "429" in str(e) or "quota" in str(e):
            st.error("🚨 Límite de peticiones de Google Sheets alcanzado (Error 429).")
        else:
            st.error(f"❌ No se pudo abrir el libro de Google Sheets: {e}")
        return None


def leer_datos_seguro(id_o_nombre_libro, name=None, header_row=0, cache_version=None):
    """Lee datos de una hoja de Google Sheets de forma segura."""
    libro = conectar_libro(id_o_nombre_libro)
    if not libro:
        return pd.DataFrame()
    try:
        if name:
            hoja = libro.worksheet(name)
        else:
            hoja = libro.get_worksheet(0)

        datos = hoja.get_all_values()
        if not datos:
            return pd.DataFrame()

        df = pd.DataFrame(datos)
        if header_row < len(df):
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1 :].reset_index(drop=True)
        return df
    except Exception as exc:
        st.error(f"No se pudo leer la hoja '{name}': {exc}")
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
