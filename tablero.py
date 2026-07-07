import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import pytz
import unicodedata
import re
from conexiones import leer_datos_seguro

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(layout="wide", page_title="NSG - CONTROL DE PISO", page_icon="🏭")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0E1117; }
    .block-container {
        max-width: 100% !important;
        padding: 0.25rem 0.8rem 0.2rem 0.8rem !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.45rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
    [data-testid="column"] {
        min-width: 0 !important;
        padding-left: 0.22rem !important;
        padding-right: 0.22rem !important;
    }
    [data-testid="stElementContainer"] { margin-bottom: 0 !important; }
    @keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    .area-card {
        padding: clamp(8px, 1vmin, 12px); border-radius: 18px; border: 4px solid #333;
        background-color: #1A1A1A; height: calc((100dvh - 12vh) / 2); margin: 0 0.1rem 0.5rem 0.1rem;
        display: flex; flex-direction: column; justify-content: space-between;
        position: relative; box-sizing: border-box; overflow: hidden;
    }
    .label-area { font-size: clamp(20px, 2.2vmin, 34px); font-weight: 800; color: white; text-align: center; text-transform: uppercase; }
    .val-pct { font-size: clamp(52px, 10vmin, 120px); font-weight: 900; text-align: center; margin: -4px 0; line-height: 0.9; }
    .bar-container { width: 100%; background-color: #262626; border-radius: 8px; height: clamp(18px, 3.5vmin, 44px); margin-bottom: clamp(4px, 0.8vmin, 10px); position: relative; border: 1px solid #555; overflow: hidden; }
    .bar-fill-ideal { position: absolute; top: 0; left: 0; bottom: 0; background-color: #2d4a57; }
    .bar-fill-real { position: absolute; top: 0; left: 0; bottom: 0; transition: width 0.8s; }
    .bar-marker-ideal { position: absolute; top: 0; bottom: 0; width: 3px; background: rgba(255,255,255,0.4); z-index: 3; pointer-events: none; }
    .label-meta { font-size: clamp(11px, 1.25vmin, 16px); color: #9da8ad; font-weight: 900; display: flex; justify-content: space-between; margin-bottom: 3px; }

    /* Vista de Productividad por Áreas con Líderes */
    .prod-card {
        background-color: #161A22; border: 3px solid #28303F; border-radius: 20px; padding: 20px; height: auto; display: flex; flex-direction: column;
    }
    .prod-card-title {
        font-size: clamp(18px, 2vmin, 28px); font-weight: 900; text-align: center; margin-bottom: 8px; text-transform: uppercase; padding-bottom: 6px; border-bottom: 2px solid #232934;
    }
    .leader-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 4px solid #3B82F6; border-radius: 22px; padding: 14px;
        margin-bottom: 1vh; text-align: center; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    .leader-title { font-size: clamp(18px, 2vmin, 28px); color: #94A3B8; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
    .leader-name { font-size: clamp(28px, 3.6vmin, 50px); color: #FFFFFF; font-weight: 950; margin: 3px 0 10px 0; }
    .leader-metrics { display: flex; justify-content: space-around; margin-top: 6px; }
    .leader-met-box { text-align: center; padding: 8px 20px; background: #1E293B; border-radius: 14px; border: 1px solid #334155; }
    .leader-met-val { font-size: clamp(42px, 6vmin, 82px); font-weight: 900; }
    .table-piso-gigante { width: 100%; border-collapse: collapse; color: #F1F5F9; font-size: clamp(26px, 3.2vmin, 48px); table-layout: fixed; }
    .table-piso-gigante th { background-color: #1E293B; padding: 0 20px; height: 48px; font-weight: 950; color: #3B82F6; text-align: left; border-bottom: 4px solid #334155; text-transform: uppercase; vertical-align: middle; box-sizing: border-box; }
    .table-piso-gigante td { padding: 0 20px; height: 110px; border-bottom: 2px solid #1E293B; font-weight: 900; vertical-align: middle; box-sizing: border-box; overflow: hidden; }
    .table-piso-gigante tr:nth-child(even) { background-color: #111827; }
    /* Paginación automática tablas de productividad */
    .prod-piso-wrap { overflow: hidden; position: relative; }
    @keyframes prodPisoTrack {
        from { transform: translateY(0); }
        to   { transform: translateY(var(--prod-shift)); }
    }

    /* Mini Tabla Interna (Avance por proceso) */
    .mini-tabla-wrap {
        height: 8vh; overflow: hidden; margin-top: clamp(2px, 0.6vmin, 6px); padding-right: 4px;
        position: relative;
    }
    .mini-tabla-wrap::-webkit-scrollbar { width: 6px; }
    .mini-tabla-wrap::-webkit-scrollbar-thumb { background: #444; border-radius: 6px; }
    .mini-track { animation: miniTrack 8s steps(1) infinite; }
    .mini-track-unica { animation: none; }
    .mini-page { height: 8vh; }
    @keyframes miniTrack {
        from { transform: translateY(0); }
        to { transform: translateY(var(--shift)); }
    }
    .mini-tabla { font-size: clamp(17px, 2.2vmin, 32px); color: #BBB; width: 100%; border-collapse: collapse; table-layout: fixed; }
    .mini-tabla td { padding: clamp(2px, 0.4vmin, 5px) 0 clamp(2px, 0.4vmin, 5px) 0; border-bottom: 1px solid #252525; vertical-align: top; }
    .mini-main { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: center; }
    .mini-piece { color: #F2F2F2; font-weight: 900; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .mini-sub { color: #d6e4ef; font-size: clamp(13px, 1.6vmin, 22px); font-weight: 850; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 2px; }
    .mini-real { color: #b4c9d8; font-size: clamp(13px, 1.6vmin, 22px); font-weight: 900; text-align: right; }
    .mini-pagina { font-size: clamp(8px, 0.8vmin, 12px); color: #555; text-align: right; font-weight: bold; margin-top: 2px; }
    .paro-alert {
        padding: clamp(8px, 1.2vmin, 16px); border-radius: 10px; font-size: clamp(13px, 1.6vmin, 22px); font-weight: bold;
        text-align: center; margin-top: clamp(4px, 0.8vmin, 10px); animation: parpadeo 2s infinite;
    }
    .paro-rojo { background-color: #441111; color: #ff4444; border: 1px solid #ff4444; }
    .paro-amarillo { background-color: #3f3508; color: #f1c40f; border: 1px solid #f1c40f; }
    .paro-verde { background-color: #0f3b22; color: #2ecc71; border: 1px solid #2ecc71; }
    .paro-espera { background-color: #102b3a; color: #7fb3d5; border: 1px solid #7fb3d5; }
    .estado-badge {
        position: absolute; top: 10px; right: 12px; padding: 5px 10px;
        border-radius: 999px; font-size: clamp(8px, 0.8vmin, 12px); font-weight: 900;
        letter-spacing: 0.02em; text-transform: uppercase;
    }
    .nota-moldeo-diferido {
        position: absolute; top: 12px; left: 14px; max-width: 15vw;
        color: #7fb3d5; font-size: clamp(8px, 0.68vmin, 11px); font-weight: 900;
        line-height: 1.2; text-align: left; text-transform: uppercase;
        opacity: 0.82;
    }
    .estado-verde { background-color: #0f3b22; color: #2ecc71; border: 1px solid #2ecc71; }
    .estado-amarillo { background-color: #3f3508; color: #f1c40f; border: 1px solid #f1c40f; }
    .estado-rojo { background-color: #441111; color: #ff4444; border: 1px solid #ff4444; }
    .estado-espera { background-color: #102b3a; color: #7fb3d5; border: 1px solid #7fb3d5; }
    .area-sin-programa {
        border-color: #555 !important; background-color: #151515; color: #777;
        justify-content: center; align-items: center; text-align: center;
    }
    .sin-programa-texto { font-size: 1.4vw; font-weight: 800; color: #888; margin-top: 18px; }
    .sin-programa-sub { font-size: 0.9vw; color: #555; font-weight: bold; margin-top: 8px; }
    .screensaver {
        height: 90vh; display: flex; align-items: center; justify-content: center;
        text-align: center; color: #d6e4ef;
    }
    .screensaver-box { width: 90vw; max-width: 1500px; }
    .screensaver-logo {
        font-size: 6.5vw; line-height: 1; font-weight: 950; color: #24313a;
        letter-spacing: 0.16em; margin-bottom: 3vh;
    }
    .screensaver-status {
        display: inline-block; padding: 1.1vh 2vw; border: 2px solid #7fb3d5;
        border-radius: 999px; background: #102b3a; color: #7fb3d5;
        font-size: 1.25vw; font-weight: 950; letter-spacing: 0.04em;
        animation: parpadeo 2.5s infinite;
    }
    .screensaver-title {
        margin-top: 4vh; font-size: 3.3vw; font-weight: 950; color: #f2f6f8;
        text-transform: uppercase;
    }
    .screensaver-sub {
        margin-top: 1.2vh; font-size: 1.35vw; font-weight: 850; color: #80919c;
    }
    .frases-wrap {
        position: relative; height: 8vh; margin-top: 5vh; overflow: hidden;
    }
    .frase {
        position: absolute; inset: 0; display: flex; align-items: center;
        justify-content: center; opacity: 0; color: #2ecc71;
        font-size: 2.1vw; font-weight: 950; animation: rotarFrases 36s infinite;
    }
    .frase:nth-child(1) { animation-delay: 0s; }
    .frase:nth-child(2) { animation-delay: 6s; }
    .frase:nth-child(3) { animation-delay: 12s; }
    .frase:nth-child(4) { animation-delay: 18s; }
    .frase:nth-child(5) { animation-delay: 24s; }
    .frase:nth-child(6) { animation-delay: 30s; }
    @keyframes rotarFrases {
        0% { opacity: 0; transform: translateY(20px); }
        6% { opacity: 1; transform: translateY(0); }
        15% { opacity: 1; transform: translateY(0); }
        21% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 0; transform: translateY(-20px); }
    }
    .barra-bono-aviso {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
        background: #0F172A; border-top: 2px solid #334155;
        padding: clamp(6px,0.8vmin,12px) clamp(12px,2vw,32px);
        font-size: clamp(12px,1.3vmin,18px); font-weight: 700;
        color: #94A3B8; text-align: center; letter-spacing: 0.03em;
    }
    @keyframes confettiFall {
        0%   { transform: translateY(0) rotate(0deg);   opacity: 1; }
        100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
    }
    @keyframes countdown30s {
        from { width: 100%; }
        to   { width: 0%; }
    }
    @keyframes rotarFraseSeg {
        0%     { opacity: 0; transform: translateY(18px); }
        3%     { opacity: 1; transform: translateY(0); }
        7%     { opacity: 1; transform: translateY(0); }
        10%    { opacity: 0; transform: translateY(-18px); }
        10.01% { opacity: 0; transform: translateY(18px); }
        100%   { opacity: 0; transform: translateY(18px); }
    }
    .frase-seg {
        position: absolute; inset: 0; display: flex; align-items: center;
        justify-content: center; opacity: 0; text-align: center;
        font-size: clamp(26px, 3.4vmin, 52px); font-weight: 900; color: #E2E8F0;
        animation: rotarFraseSeg calc(var(--total-frases) * 5s) infinite;
        padding: 0 16px; line-height: 1.2;
    }
    .val-pct { font-size: clamp(58px, 11vmin, 130px); font-weight: 900; text-align: center; margin: -4px 0; line-height: 0.9; }
    </style>
""",
    unsafe_allow_html=True,
)

ID_LIBRO = "13ZF5TXwgEZSlrODQFF43Rvs4JmB19s6V0KNV1l72RHA"
ID_LIBRO_PROD = "1hXxm3yOx7lwzbDuUAUauKl-VoW7L-5UdfkFbjYg-s7g"
ID_LIBRO_CALIDAD = "1-u-rZ-If5NWksvG1OPexbu7PW-DZo4FQLu5WLskwdqQ"
DEFECTO_A_AREA = {
    "FISURA": "MOLDEO",
    "RECHUPE": "MOLDEO",
    "MAL LLENADO": "MOLDEO",
    "CAIDA DE ARENA": "MOLDEO",
    "SOBREMATERIAL": "MOLDEO",
    "ARRASTRE": "MOLDEO",
    "DESPLAZAMIENTO": "MOLDEO",
    "POROSIDAD": "MOLDEO",
    "SIN CORAZON": "MOLDEO",
    "SIN VARILLA": "MOLDEO",
    "ESMERIL": "CORTE",
    "CORTE": "CORTE",
    "BARRENADO": "CORTE",
}
TIMEZONE = "America/Mexico_City"
AREAS_PISO = ["MOLDEO", "CORAZONES", "CORTE", "ENSAMBLE"]
SUBS_HERRAJE = {"Ensamble de Pieza", "Empaque de pieza"}
MODO_SIN_ENSAMBLE = "SIN ENSAMBLE"
MODO_SOLO_ENSAMBLE = "SOLO ENSAMBLE"
REFRESH_INTERVAL_MS = 30 * 1000  # Rotación optimizada a cada 30 segundos
MINI_FILAS_POR_PAGINA = 1
PROD_ROWS_POR_PAGINA = 4  # filas visibles por página en tablas gigantes
PROD_SEGS_POR_PAGINA = (
    15  # segundos por página — 2 páginas = 30s = exactamente un slot de rotación
)
RESPALDO_DIR = Path(".respaldo_tablero")
CORTES = [
    {"nombre": "11:00 AM (3h)", "label": "11:00", "base": 0.0, "aporte": 33.3},
    {"nombre": "14:00 PM (6h)", "label": "14:00", "base": 33.3, "aporte": 33.3},
    {"nombre": "17:00 PM (9h)", "label": "17:00", "base": 66.6, "aporte": 33.4},
]
AREA_MOLDEO = "MOLDEO"
HORA_INICIO_DIFERIDOS_MOLDEO = 15.0
SUBPROCESOS_DIFERIDOS_MOLDEO = ("VACIADO", "DESMOLDEO", "DESMOLDE")
NOMBRES_LIDERES = frozenset(
    [
        "JOSÉ ANTONIO REYES RUBIO",
        "LUIS DAVID ESPINOSA TORRES",
        "ARELI PALOMA FLORES GARFIAS",
    ]
)
FRASES_ESPERA_PROGRAMA = [
    "Cada pieza cuenta.",
    "La calidad empieza en cada proceso.",
    "Trabajamos seguros, trabajamos mejor.",
    "Hoy también podemos mejorar.",
    "El avance se construye paso a paso.",
    "Un buen turno empieza con orden.",
]
FRASES_SEGURIDAD = [
    "🏠 ¡Todos llegamos a casa con nuestra familia!",
    "🦺 Usa siempre tu equipo de protección personal",
    "🚶 Mantén los pasillos despejados en todo momento",
    "👀 Si ves algo inseguro, detente y repórtalo",
    "💪 ¡Equipo unido, equipo seguro!",
    "🔧 Revisa tu área antes de iniciar el turno",
    "⚠️ Reporta condiciones inseguras al instante",
    "🏆 ¡Seguimos cuidándonos — vamos por los 100 días!",
    "🧤 Guantes, lentes, calzado — cada uno importa",
    "🚨 Ante una emergencia: para, avisa, actúa",
]


# --- 2. SOPORTE ---
def ahora_local():
    return datetime.now(pytz.timezone(TIMEZONE))


def normalizar_clave(texto):
    if texto is None:
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def encontrar_columna(df, aliases, contiene_todos=None):
    if df is None or df.empty:
        return None
    aliases_norm = {normalizar_clave(a) for a in aliases}
    for col in df.columns:
        if normalizar_clave(col) in aliases_norm:
            return col

    if contiene_todos:
        tokens = [normalizar_clave(token) for token in contiene_todos]
        for col in df.columns:
            clave = normalizar_clave(col)
            if all(token in clave for token in tokens):
                return col
    return None


def convertir_serie_numerica(serie):
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(",", "")
        .str.replace(r"[^\d\.\-]", "", regex=True),
        errors="coerce",
    )


def normalizar_fecha_serie(serie):
    serie_texto = serie.astype(str).str.strip()
    fechas = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        pendientes = fechas.isna()
        if not pendientes.any():
            break
        fechas.loc[pendientes] = pd.to_datetime(
            serie_texto.loc[pendientes], format=formato, errors="coerce"
        )
    numeros = pd.to_numeric(serie_texto, errors="coerce")
    mask_serial = fechas.isna() & numeros.between(20000, 60000)
    if mask_serial.any():
        fechas.loc[mask_serial] = pd.to_datetime(
            numeros.loc[mask_serial], unit="D", origin="1899-12-30", errors="coerce"
        )
    return fechas.dt.strftime("%d/%m/%Y").fillna(serie_texto)


def columnas_completas(diccionario):
    return all(valor is not None for valor in diccionario.values())


def es_area_moldeo(area_nom):
    return normalizar_clave(area_nom) == normalizar_clave(AREA_MOLDEO)


def es_subproceso_diferido_moldeo(subproceso):
    clave = normalizar_clave(subproceso)
    return any(token in clave for token in SUBPROCESOS_DIFERIDOS_MOLDEO)


def filtrar_subprocesos_exigibles_area(df_area, area_nom, t_dec):
    if (
        df_area.empty
        or not es_area_moldeo(area_nom)
        or t_dec >= HORA_INICIO_DIFERIDOS_MOLDEO
        or "__BDD_SUBPROCESO" not in df_area.columns
    ):
        return df_area.copy(), False

    mask_diferidos = df_area["__BDD_SUBPROCESO"].apply(es_subproceso_diferido_moldeo)
    return df_area[~mask_diferidos].copy(), bool(mask_diferidos.any())


def filtrar_bdd_activa(df_bdd, col_b):
    if df_bdd.empty or not col_b.get("subproceso"):
        return pd.DataFrame()

    df_filtrado = df_bdd.copy()
    col_activo = col_b.get("activo")
    if col_activo:
        df_filtrado = df_filtrado[
            df_filtrado[col_activo].astype(str).str.upper().str.strip() == "TRUE"
        ].copy()

    df_filtrado = df_filtrado[df_filtrado[col_b["subproceso"]].str.len() > 1].copy()
    df_filtrado = df_filtrado[df_filtrado[col_b["subproceso"]] != "0"].copy()
    return df_filtrado


def ruta_respaldo(nombre):
    RESPALDO_DIR.mkdir(exist_ok=True)
    return RESPALDO_DIR / f"{nombre}.pkl"


def guardar_respaldo_local(nombre, valor):
    try:
        with ruta_respaldo(nombre).open("wb") as archivo:
            pickle.dump(valor, archivo)
    except Exception:
        pass


def leer_respaldo_local(nombre, default=None):
    try:
        ruta = ruta_respaldo(nombre)
        if ruta.exists():
            with ruta.open("rb") as archivo:
                return pickle.load(archivo)
    except Exception:
        pass
    return pd.DataFrame() if default is None else default


def leer_datos_con_respaldo(nombre_hoja, fila_encabezado, id_libro=ID_LIBRO):
    """Soporta la lectura de múltiples libros inyectando el id_libro dinámico."""
    clave = f"ultimo_df_{nombre_hoja}"
    df = leer_datos_seguro(id_libro, nombre_hoja, fila_encabezado)
    if df is None or df.empty:
        version_rescate = int(datetime.now().timestamp())
        df = leer_datos_seguro(id_libro, nombre_hoja, fila_encabezado, version_rescate)
    if df is not None and not df.empty:
        st.session_state[clave] = df
        guardar_respaldo_local(clave, df)
        return df
    df_memoria = st.session_state.get(clave, pd.DataFrame())
    if df_memoria is not None and not df_memoria.empty:
        return df_memoria
    return leer_respaldo_local(clave)


def guardar_respaldo_resultado(df_res, col_a, fecha_hoy):
    if df_res is None or df_res.empty:
        return
    paquete = {
        "fecha": fecha_hoy.strftime("%d/%m/%Y"),
        "df_res": df_res,
        "col_a": col_a,
    }
    st.session_state["ultimo_df_res"] = df_res
    st.session_state["ultimo_col_a"] = col_a
    st.session_state["ultimo_df_res_fecha"] = paquete["fecha"]
    guardar_respaldo_local("ultimo_resultado", paquete)


def leer_respaldo_resultado(fecha_hoy, col_a_actual):
    fecha_str = fecha_hoy.strftime("%d/%m/%Y")
    if st.session_state.get("ultimo_df_res_fecha") == fecha_str:
        return (
            st.session_state.get("ultimo_df_res", pd.DataFrame()),
            st.session_state.get("ultimo_col_a", col_a_actual),
        )

    paquete = leer_respaldo_local("ultimo_resultado", {})
    if isinstance(paquete, dict) and paquete.get("fecha") == fecha_str:
        return paquete.get("df_res", pd.DataFrame()), paquete.get("col_a", col_a_actual)
    return pd.DataFrame(), col_a_actual


def paginar_resumen(resumen, pagina, filas_por_pagina=MINI_FILAS_POR_PAGINA):
    if resumen.empty:
        return resumen, 0, 0
    total_paginas = max(1, (len(resumen) + filas_por_pagina - 1) // filas_por_pagina)
    pagina_actual = pagina % total_paginas
    inicio = pagina_actual * filas_por_pagina
    fin = inicio + filas_por_pagina
    return resumen.iloc[inicio:fin], pagina_actual + 1, total_paginas


def calcular_pct_corte_area(
    df_area, df_a, col_a, col_p, area_nom, fecha_hoy, corte_actual, corte_anterior
):
    if (
        df_area.empty
        or df_a.empty
        or not col_a
        or not col_a.get("area")
        or not col_a.get("fecha")
        or not col_a.get("pieza")
        or not col_a.get("subproceso")
        or not col_a.get("real")
        or not col_a.get("corte")
    ):
        return None

    df_a_area = df_a[
        (df_a[col_a["area"]].apply(normalizar_clave) == normalizar_clave(area_nom))
    ].copy()
    if df_a_area.empty:
        return 0.0

    df_a_area["__FECHA"] = normalizar_fecha_serie(df_a_area[col_a["fecha"]])
    df_a_area = df_a_area[df_a_area["__FECHA"] == fecha_hoy.strftime("%d/%m/%Y")].copy()
    if df_a_area.empty:
        return 0.0

    df_a_area[col_a["real"]] = convertir_serie_numerica(
        df_a_area[col_a["real"]]
    ).fillna(0)

    llave_base = df_area[[col_p["pieza"], "__BDD_SUBPROCESO", col_p["total"]]].copy()
    llave_base[col_p["total"]] = convertir_serie_numerica(
        llave_base[col_p["total"]]
    ).fillna(0)

    df_actual = (
        df_a_area[df_a_area[col_a["corte"]] == corte_actual]
        .groupby([col_a["pieza"], col_a["subproceso"]])[col_a["real"]]
        .max()
        .reset_index()
        .rename(columns={col_a["real"]: "__REAL_CORTE_ACTUAL"})
    )

    if corte_anterior:
        df_anterior = (
            df_a_area[df_a_area[col_a["corte"]] == corte_anterior]
            .groupby([col_a["pieza"], col_a["subproceso"]])[col_a["real"]]
            .max()
            .reset_index()
            .rename(columns={col_a["real"]: "__REAL_CORTE_ANTERIOR"})
        )
    else:
        df_anterior = pd.DataFrame(
            columns=[col_a["pieza"], col_a["subproceso"], "__REAL_CORTE_ANTERIOR"]
        )

    df_corte = pd.merge(
        llave_base,
        df_actual,
        left_on=[col_p["pieza"], "__BDD_SUBPROCESO"],
        right_on=[col_a["pieza"], col_a["subproceso"]],
        how="left",
    )
    df_corte = pd.merge(
        df_corte,
        df_anterior,
        left_on=[col_p["pieza"], "__BDD_SUBPROCESO"],
        right_on=[col_a["pieza"], col_a["subproceso"]],
        how="left",
        suffixes=("", "_ANT"),
    ).fillna(0)

    aporte_real = (
        convertir_serie_numerica(df_corte["__REAL_CORTE_ACTUAL"]).fillna(0)
        - convertir_serie_numerica(df_corte["__REAL_CORTE_ANTERIOR"]).fillna(0)
    ).clip(lower=0)
    total_seguro = convertir_serie_numerica(df_corte[col_p["total"]]).fillna(0)
    pct_corte = pd.Series(0.0, index=df_corte.index)
    mask_total = total_seguro > 0
    pct_corte.loc[mask_total] = (
        aporte_real.loc[mask_total] / total_seguro.loc[mask_total] * 100
    )
    return round(float(pct_corte.mean()), 1)


def obtener_info_horario(t_dec):
    if t_dec < 11.0:
        corte = CORTES[0]
        prog_b = (t_dec - 8.0) / 3.0
        ideal = max(0.0, prog_b * corte["aporte"])
        return {
            "bloque": "BLOQUE 1",
            "corte_actual": corte,
            "corte_anterior": None,
            "siguiente": CORTES[0],
            "ideal": min(100.0, ideal),
            "meta_corte": max(0.0, min(corte["aporte"], ideal - corte["base"])),
        }
    if t_dec < 14.0:
        corte = CORTES[1]
        prog_b = (t_dec - 11.0) / 3.0
        ideal = corte["base"] + (prog_b * corte["aporte"])
        return {
            "bloque": "BLOQUE 2",
            "corte_actual": corte,
            "corte_anterior": CORTES[0],
            "siguiente": CORTES[1],
            "ideal": min(100.0, ideal),
            "meta_corte": max(0.0, min(corte["aporte"], ideal - corte["base"])),
        }

    corte = CORTES[2]
    prog_b = (t_dec - 14.0) / 3.0
    ideal = corte["base"] + (prog_b * corte["aporte"])
    return {
        "bloque": "BLOQUE 3",
        "corte_actual": corte,
        "corte_anterior": CORTES[1],
        "siguiente": CORTES[2],
        "ideal": min(100.0, ideal),
        "meta_corte": max(0.0, min(corte["aporte"], ideal - corte["base"])),
    }


def cortes_auditados_area(df_a, col_a, area_nom, fecha_hoy):
    if (
        df_a.empty
        or not col_a
        or not col_a.get("area")
        or not col_a.get("fecha")
        or not col_a.get("corte")
    ):
        return []

    df_area = df_a[
        df_a[col_a["area"]].apply(normalizar_clave) == normalizar_clave(area_nom)
    ].copy()
    if df_area.empty:
        return []

    df_area["__FECHA"] = normalizar_fecha_serie(df_area[col_a["fecha"]])
    df_area = df_area[df_area["__FECHA"] == fecha_hoy.strftime("%d/%m/%Y")]
    if df_area.empty:
        return []

    valores = set(df_area[col_a["corte"]].astype(str).str.strip())
    return [corte for corte in CORTES if corte["nombre"] in valores]


def corte_con_captura_area(df_a, col_a, area_nom, fecha_hoy, corte_nombre):
    if (
        df_a.empty
        or not col_a
        or not col_a.get("area")
        or not col_a.get("fecha")
        or not col_a.get("corte")
        or not col_a.get("real")
    ):
        return False

    df_area = df_a[
        df_a[col_a["area"]].apply(normalizar_clave) == normalizar_clave(area_nom)
    ].copy()
    if df_area.empty:
        return False

    df_area["__FECHA"] = normalizar_fecha_serie(df_area[col_a["fecha"]])
    df_area = df_area[
        (df_area["__FECHA"] == fecha_hoy.strftime("%d/%m/%Y"))
        & (
            df_area[col_a["corte"]].astype(str).apply(normalizar_clave)
            == normalizar_clave(corte_nombre)
        )
    ]
    if df_area.empty:
        return False

    real_capturado = (
        convertir_serie_numerica(df_area[col_a["real"]]).fillna(0).gt(0).any()
    )
    if real_capturado:
        return True

    col_notas = col_a.get("notas")
    if col_notas and col_notas in df_area.columns:
        notas = df_area[col_notas].astype(str).str.strip()
        notas_validas = notas[~notas.str.upper().isin(["", "NAN", "NONE", "0"])]
        if not notas_validas.empty:
            return True

    return False


def corte_completo_area(df_area, df_a, col_a, col_p, area_nom, fecha_hoy, corte_nombre):
    if (
        df_area.empty
        or df_a.empty
        or not col_a
        or not col_a.get("area")
        or not col_a.get("fecha")
        or not col_a.get("pieza")
        or not col_a.get("subproceso")
        or not col_a.get("corte")
    ):
        return False

    columnas_base = [col_p.get("pieza"), "__BDD_SUBPROCESO"]
    if any(col is None or col not in df_area.columns for col in columnas_base):
        return False

    esperadas = {
        (
            normalizar_clave(fila[col_p["pieza"]]),
            normalizar_clave(fila["__BDD_SUBPROCESO"]),
        )
        for _, fila in df_area[columnas_base].dropna(how="any").iterrows()
    }
    if not esperadas:
        return False

    df_a_area = df_a[
        df_a[col_a["area"]].apply(normalizar_clave) == normalizar_clave(area_nom)
    ].copy()
    if df_a_area.empty:
        return False

    df_a_area["__FECHA"] = normalizar_fecha_serie(df_a_area[col_a["fecha"]])
    df_a_area = df_a_area[
        (df_a_area["__FECHA"] == fecha_hoy.strftime("%d/%m/%Y"))
        & (
            df_a_area[col_a["corte"]].astype(str).apply(normalizar_clave)
            == normalizar_clave(corte_nombre)
        )
    ]
    if df_a_area.empty:
        return False

    auditadas = {
        (
            normalizar_clave(fila[col_a["pieza"]]),
            normalizar_clave(fila[col_a["subproceso"]]),
        )
        for _, fila in df_a_area[[col_a["pieza"], col_a["subproceso"]]]
        .dropna(how="any")
        .iterrows()
    }
    return esperadas.issubset(auditadas)


def corte_anterior_de(corte):
    idx = CORTES.index(corte)
    return CORTES[idx - 1] if idx > 0 else None


def corte_vencido(t_dec):
    if t_dec >= 17.0:
        return CORTES[2]
    if t_dec >= 14.0:
        return CORTES[1]
    if t_dec >= 11.0:
        return CORTES[0]
    return None


def calcular_fechas_semana_corta(fecha_base):
    """Calcula matemáticamente el rango de la semana actual de Jueves a Miércoles."""
    # weekday() de Python: 0=Lunes, 1=Martes, ..., 3=Jueves, ..., 6=Domingo
    dias_desde_jueves = (fecha_base.weekday() - 3) % 7
    inicio_semana = fecha_base - timedelta(days=dias_desde_jueves)
    fin_semana = inicio_semana + timedelta(days=6)
    return inicio_semana, fin_semana


def filtrar_subs_por_modo(subs, modo):
    modo_n = str(modo).strip().upper() if pd.notna(modo) and modo != "" else ""
    if modo_n == MODO_SIN_ENSAMBLE:
        return [s for s in subs if s not in SUBS_HERRAJE]
    if modo_n == MODO_SOLO_ENSAMBLE:
        return [s for s in subs if s in SUBS_HERRAJE]
    return list(subs)


# --- 3. MOTOR ---
def obtener_datos_unificados(df_aud, df_prog, df_bdd, col_p, col_b, fecha):
    try:
        f_str = fecha.strftime("%d/%m/%Y")
        col_a = {
            "area": encontrar_columna(df_aud, ["AREA", "PROCESO"]),
            "fecha": encontrar_columna(df_aud, ["FECHA"]),
            "pieza": encontrar_columna(df_aud, ["PIEZA"]),
            "subproceso": encontrar_columna(
                df_aud,
                ["SUBPROCESO", "SUB PROCESO", "SUB_PROCESO"],
                contiene_todos=["SUB", "CESO"],
            ),
            "real": encontrar_columna(df_aud, ["REAL"]),
            "corte": encontrar_columna(df_aud, ["CORTE"]),
            "notas": encontrar_columna(df_aud, ["NOTAS", "NOTA"]),
        }
        if df_aud.empty or df_prog.empty or df_bdd.empty:
            return pd.DataFrame(), col_a

        col_a_requeridas = {
            "fecha": col_a["fecha"],
            "pieza": col_a["pieza"],
            "subproceso": col_a["subproceso"],
            "real": col_a["real"],
        }
        col_b_requeridas = {
            "pieza": col_b["pieza"],
            "subproceso": col_b["subproceso"],
            "proceso": col_b["proceso"],
        }
        if (
            not columnas_completas(col_p)
            or not columnas_completas(col_b_requeridas)
            or not columnas_completas(col_a_requeridas)
        ):
            return pd.DataFrame(), col_a

        df_prog = df_prog.copy()
        df_prog["__FECHA"] = normalizar_fecha_serie(df_prog[col_p["fecha"]])
        df_p_v = df_prog[df_prog["__FECHA"] == f_str].copy()
        if df_p_v.empty:
            return pd.DataFrame(), col_a

        mask_m = df_p_v[col_p["area"]].apply(normalizar_clave) == "MOLDEO"
        df_p_final = pd.concat(
            [
                df_p_v[
                    mask_m
                    & df_p_v[col_p["pieza"]].str.contains(
                        "GENERAL|VACIADO|ADOBES", case=False, na=False
                    )
                ],
                df_p_v[~mask_m],
            ]
        )
        df_p_final[col_p["total"]] = convertir_serie_numerica(
            df_p_final[col_p["total"]]
        ).fillna(0)
        df_p_final = df_p_final[df_p_final[col_p["total"]] > 0].copy()

        df_a_v = df_aud.copy()
        df_a_v[col_a["real"]] = pd.to_numeric(
            df_a_v[col_a["real"]], errors="coerce"
        ).fillna(0)
        df_a_v["__FECHA"] = normalizar_fecha_serie(df_a_v[col_a["fecha"]])
        df_max_a = (
            df_a_v.groupby(["__FECHA", col_a["pieza"], col_a["subproceso"]])[
                col_a["real"]
            ]
            .max()
            .reset_index()
        )

        df_bdd_base = df_bdd[
            [col_b["pieza"], col_b["subproceso"], col_b["proceso"]]
        ].copy()
        df_bdd_base.columns = ["__BDD_PIEZA", "__BDD_SUBPROCESO", "__BDD_PROCESO"]

        df_base = pd.merge(
            df_p_final,
            df_bdd_base,
            left_on=col_p["pieza"],
            right_on="__BDD_PIEZA",
            how="inner",
        )
        df_base = df_base[
            df_base[col_p["area"]].apply(normalizar_clave)
            == df_base["__BDD_PROCESO"].apply(normalizar_clave)
        ]

        col_modo = col_p.get("modo_herraje")
        if col_modo and col_modo in df_base.columns:
            mask_ensamble = df_base[col_p["area"]].apply(normalizar_clave) == "ENSAMBLE"
            modo_vals = df_base[col_modo].fillna("").astype(str).str.strip().str.upper()
            mask_sin = mask_ensamble & (modo_vals == MODO_SIN_ENSAMBLE)
            mask_solo = mask_ensamble & (modo_vals == MODO_SOLO_ENSAMBLE)
            mask_excluir = (
                (mask_sin & df_base["__BDD_SUBPROCESO"].isin(SUBS_HERRAJE))
                | (mask_solo & ~df_base["__BDD_SUBPROCESO"].isin(SUBS_HERRAJE))
            )
            df_base = df_base[~mask_excluir]

        df_uni = pd.merge(
            df_base,
            df_max_a,
            left_on=["__FECHA", col_p["pieza"], "__BDD_SUBPROCESO"],
            right_on=["__FECHA", col_a["pieza"], col_a["subproceso"]],
            how="left",
        ).fillna(0)
        total_seguro = convertir_serie_numerica(df_uni[col_p["total"]]).fillna(0)
        real_seguro = convertir_serie_numerica(df_uni[col_a["real"]]).fillna(0)
        df_uni["% REAL"] = 0.0
        mask_total = total_seguro > 0
        df_uni.loc[mask_total, "% REAL"] = (
            real_seguro[mask_total] / total_seguro[mask_total] * 100
        )
        return df_uni, col_a
    except Exception as exc:
        st.error(f"Error al preparar datos del tablero: {exc}")
        return pd.DataFrame(), None


# --- 4. PANTALLA DE PRODUCTIVIDAD POR ÁREAS ---
def clasificar_colaborador_area(row, col_area, col_actividad):
    """Clasifica al operador en una de las 3 áreas usando AREA primero, ACTIVIDAD como fallback."""
    if col_area and col_area in row and str(row[col_area]).strip():
        val = normalizar_clave(row[col_area])
        if "MOLDEO" in val or "CORAZONES" in val:
            return "MOLDEO Y CORAZONES"
        if "CORTE" in val:
            return "CORTE"
        if "ENSAMBLE" in val:
            return "ENSAMBLE"

    if col_actividad and col_actividad in row and str(row[col_actividad]).strip():
        val = normalizar_clave(row[col_actividad])
        if any(
            x in val
            for x in [
                "MOLDEO",
                "DESMOLDEO",
                "DESMOLDE",
                "VACIADO",
                "ADOBES",
                "ARENA",
                "MOLER",
            ]
        ):
            return "MOLDEO Y CORAZONES"
        if any(x in val for x in ["CORTE", "LIJADO", "ESMERIL", "REBABA"]):
            return "CORTE"
        if any(
            x in val
            for x in [
                "ENSAMBLE",
                "LIMADO",
                "MOTOTOOL",
                "DISCO",
                "EMPLAYADO",
                "ENGRASADO",
            ]
        ):
            return "ENSAMBLE"
    return "OTROS"


def _color_prod(valor):
    return "#2ecc71" if valor >= 90 else ("#f1c40f" if valor >= 70 else "#E32B13")


def _calcular_aporte_bono(prod_pct):
    """Fórmula exacta de RRHH (NSG-RH-AC-002) — idéntica a la usada en nómina.
    Dos tramos lineales: 0–70% prod → 0–15% aporte; 70–100% prod → 15–40% aporte."""
    p = prod_pct / 100.0
    if p <= 0:
        return 0.0
    if p >= 1.0:
        return 40.0
    if p < 0.70:
        return (p / 0.70) * 15.0  # tramo bajo: 0–15%, trabajo sí se contabiliza
    return 15.0 + ((p - 0.70) / 0.30) * 25.0


def _aporte_bono_html(val):
    """Badge con el aporte calculado — misma fórmula que RRHH usa en nómina."""
    aporte = _calcular_aporte_bono(val)
    aporte_r = round(aporte, 1)
    _s = "font-weight:900;white-space:nowrap;border-radius:8px;padding:5px 14px;font-size:clamp(13px,1.5vmin,22px);"
    if aporte_r >= 30.0:
        bg, fg, brd = "#0f3b22", "#2ecc71", "#2ecc71"
    elif aporte_r >= 15.0:
        bg, fg, brd = "#3f3508", "#f1c40f", "#f1c40f"
    else:
        bg, fg, brd = "#441111", "#ff4444", "#ff4444"
    return f'<span style="{_s}background:{bg};color:{fg};border:2px solid {brd};">APORTE: {aporte:.1f}%</span>'


_FILA_PX = 110  # altura td tabla diaria — igual que semanal para misma altura de card
_PAGINA_PX = _FILA_PX * PROD_ROWS_POR_PAGINA  # 440 px por página diaria
_FILA_DOBLE_PX = 110  # altura td tabla semanal (2 líneas: nombre + métricas)
_PAGINA_DOBLE_PX = _FILA_DOBLE_PX * PROD_ROWS_POR_PAGINA  # 440 px por página semanal


def _tabla_paginada_html(ranking_vals, titulo, color_titulo, pie_nota=None):
    """Card HTML con paginación snap automática — sin scroll manual, apta para kiosco.
    ranking_vals: (nom, val) diaria | (nom, val, aporte_html, asistencia_str) semanal.
    """
    semanal = bool(ranking_vals) and len(ranking_vals[0]) == 4
    pagina_h = _PAGINA_DOBLE_PX if semanal else _PAGINA_PX

    if not ranking_vals:
        return (
            f'<div class="prod-card">'
            f'<div class="prod-card-title" style="color:{color_titulo};">{titulo}</div>'
            f'<div style="text-align:center;color:#555;padding:40px 20px;'
            f'font-size:clamp(20px,2vmin,30px);">Sin registros</div>'
            f"</div>"
        )

    paginas_html = []
    for i in range(0, len(ranking_vals), PROD_ROWS_POR_PAGINA):
        grupo = ranking_vals[i : i + PROD_ROWS_POR_PAGINA]
        if semanal:
            # Línea 1: nombre izq + asistencia der | Línea 2: % prod izq + badge aporte der
            filas = "".join(
                f'<tr><td style="height:{_FILA_DOBLE_PX}px!important;padding:0 20px;'
                f"vertical-align:middle;box-sizing:border-box;overflow:hidden;"
                f'border-bottom:2px solid #1E293B;">'
                f'<div style="display:flex;justify-content:space-between;align-items:baseline;">'
                f'<span style="font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                f'font-size:clamp(20px,2.3vmin,34px);">{nom}</span>'
                f'<span style="color:#94A3B8;white-space:nowrap;margin-left:12px;'
                f'font-size:clamp(14px,1.6vmin,22px);font-weight:700;">{asistencia}</span>'
                f"</div>"
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">'
                f'<span style="color:{_color_prod(val)};font-weight:900;'
                f'font-size:clamp(18px,2vmin,30px);">{val:.1f}%</span>'
                f"{aporte}"
                f"</div></td></tr>"
                for nom, val, aporte, asistencia in grupo
            )
        else:
            filas = "".join(
                f'<tr><td style="padding:6px 20px;vertical-align:middle;box-sizing:border-box;overflow:hidden;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{nom}</span>'
                f'<span style="color:{_color_prod(val)};white-space:nowrap;margin-left:16px;font-weight:900;">{val:.1f}%</span>'
                f'</div>'
                f'<div style="height:6px;background:#1E293B;border-radius:4px;margin-top:6px;overflow:hidden;">'
                f'<div style="height:100%;width:{val:.1f}%;background:{_color_prod(val)};border-radius:4px;"></div>'
                f'</div>'
                f"</td></tr>"
                for nom, val in grupo
            )
        paginas_html.append(
            f'<div style="height:{pagina_h}px;">'
            f'<table class="table-piso-gigante"><tbody>{filas}</tbody></table>'
            f"</div>"
        )

    num_pags = len(paginas_html)
    shift_px = -(pagina_h * num_pags)
    anim = (
        "animation:none;"
        if num_pags == 1
        else f"animation:prodPisoTrack {num_pags * PROD_SEGS_POR_PAGINA}s steps({num_pags}) infinite;"
    )

    thead = (
        f'<thead><tr><th style="white-space:nowrap;">OPERADOR · EFICIENCIA Y APORTE SEMANAL</th></tr></thead>'
        if semanal
        else f'<thead><tr><th style="white-space:nowrap;">OPERADOR - EFICIENCIA DEL DÍA</th></tr></thead>'
    )

    pie_html = (
        (
            f'<div style="margin-top:10px;padding:10px 16px;background:#1E293B;border-radius:10px;'
            f'font-size:clamp(13px,1.4vmin,19px);color:#94A3B8;font-weight:700;text-align:center;">'
            f"{pie_nota}</div>"
        )
        if pie_nota
        else ""
    )

    return (
        f'<div class="prod-card">'
        f'<div class="prod-card-title" style="color:{color_titulo};">{titulo}</div>'
        f'<table class="table-piso-gigante">{thead}</table>'
        f'<div class="prod-piso-wrap" style="height:{pagina_h}px;">'
        f'<div style="--prod-shift:{shift_px}px; {anim}">'
        f'{"".join(paginas_html)}'
        f"</div></div>"
        f"{pie_html}"
        f"</div>"
    )


def renderizar_pantalla_productividad_por_area(fecha_hoy, area_objetivo, lider_nombre):
    """Muestra la productividad de un área específica con su líder y texto gigante."""
    df_prod = leer_datos_con_respaldo("REGISTRO", 0, id_libro=ID_LIBRO_PROD)
    if df_prod.empty:
        st.markdown(
            '<div class="screensaver"><div class="screensaver-status">⚠️ SIN DATOS DE PRODUCTIVIDAD</div></div>',
            unsafe_allow_html=True,
        )
        return

    try:
        col_fecha = encontrar_columna(df_prod, ["FECHA"])
        col_colab = encontrar_columna(df_prod, ["COLABORADOR", "NOMBRE", "OPERADOR"])
        col_eficiencia = (
            encontrar_columna(df_prod, ["PRODUCTIVIDADR"])
            or encontrar_columna(df_prod, ["PRODUCTIVIDAD", "EFICIENCIA"])
        )
        col_actividad = encontrar_columna(df_prod, ["ACTIVIDAD"])
        col_area = encontrar_columna(df_prod, ["AREA", "PROCESO"])

        if not col_fecha or not col_colab or not col_eficiencia:
            st.error(
                "Columnas requeridas no encontradas (FECHA, COLABORADOR, PRODUCTIVIDAD)."
            )
            return

        df_prod["__FECHA_DT"] = pd.to_datetime(
            normalizar_fecha_serie(df_prod[col_fecha]),
            format="%d/%m/%Y",
            errors="coerce",
        ).dt.date
        df_prod["__PROD_NUM"] = pd.to_numeric(
            df_prod[col_eficiencia].astype(str).str.replace("%", "").str.strip(),
            errors="coerce",
        ).fillna(0.0)
        df_prod["__AREA_PISO"] = df_prod.apply(
            lambda r: clasificar_colaborador_area(r, col_area, col_actividad), axis=1
        )

        # Excluir líderes: no compiten como operadores en ninguna área
        lideres_norm = {normalizar_clave(n) for n in NOMBRES_LIDERES}
        df_area_total = df_prod[
            (df_prod["__AREA_PISO"] == area_objetivo)
            & (
                ~df_prod[col_colab]
                .astype(str)
                .apply(normalizar_clave)
                .isin(lideres_norm)
            )
        ].copy()

        inicio_sem, fin_sem = calcular_fechas_semana_corta(fecha_hoy)
        corte_sem = min(fecha_hoy, fin_sem)

        # ── Detección de festivos: días donde AL MENOS UN operador de TODA LA PLANTA registró
        rango_laborable = [
            d.date()
            for d in pd.date_range(str(inicio_sem), str(corte_sem))
            if d.weekday() < 5
        ]
        fechas_con_registro = set(
            df_prod[
                (df_prod["__FECHA_DT"] >= inicio_sem)
                & (df_prod["__FECHA_DT"] <= corte_sem)
            ]["__FECHA_DT"]
            .dropna()
            .unique()
        )
        fechas_activas_planta = [d for d in rango_laborable if d in fechas_con_registro]
        total_dias_semana = max(len(fechas_activas_planta), 1)

        # ── Datos del área: hoy y semana (antes de clip para contar días reales)
        df_hoy_raw = df_area_total[df_area_total["__FECHA_DT"] == fecha_hoy].copy()
        df_area_sem_raw = df_area_total[
            df_area_total["__FECHA_DT"].isin(fechas_activas_planta)
        ].copy()

        # Días reales trabajados por operador (antes del clip y del reindexado)
        dias_por_op = (
            df_area_sem_raw.groupby(col_colab)["__FECHA_DT"].nunique().to_dict()
        )

        # Aplicar límite 100%
        df_hoy_raw["__PROD_NUM"] = df_hoy_raw["__PROD_NUM"].clip(upper=100.0)
        df_area_sem_raw["__PROD_NUM"] = df_area_sem_raw["__PROD_NUM"].clip(upper=100.0)
        df_hoy = df_hoy_raw

        prod_lider_hoy = (
            df_hoy.groupby(col_colab)["__PROD_NUM"].mean().mean()
            if not df_hoy.empty else 0.0
        )

        df_diario_op = (
            df_area_sem_raw.groupby([col_colab, "__FECHA_DT"])["__PROD_NUM"]
            .mean()
            .reset_index()
        )
        df_diario_activo = df_diario_op[df_diario_op["__PROD_NUM"] > 0]
        if not df_diario_activo.empty:
            prod_lider_sem = (
                df_diario_activo.groupby(col_colab)["__PROD_NUM"].mean().mean()
            )
        else:
            prod_lider_sem = 0.0

        def _box_style(fg):
            if fg == "#2ecc71":
                return "background:#0f3b22;border:2px solid #2ecc71;"
            elif fg == "#f1c40f":
                return "background:#3f3508;border:2px solid #f1c40f;"
            else:
                return "background:#441111;border:2px solid #ff4444;"

        aporte_lider_sem = _calcular_aporte_bono(prod_lider_sem)
        _aporte_r = round(aporte_lider_sem, 1)
        if _aporte_r >= 30.0:
            color_aporte_lider = "#2ecc71"
        elif _aporte_r >= 15.0:
            color_aporte_lider = "#f1c40f"
        else:
            color_aporte_lider = "#ff4444"

        c_hoy = _color_prod(prod_lider_hoy)
        c_sem = _color_prod(prod_lider_sem)

        if prod_lider_sem >= 90:
            lider_msg = "🌟 ¡EXCELENTE TRABAJO! Tu equipo está brillando esta semana"
            lider_msg_color = "#2ecc71"
        elif prod_lider_sem >= 70:
            lider_msg = "💪 ¡BUEN RITMO! Sigue motivando a tu equipo para llegar a la meta"
            lider_msg_color = "#f1c40f"
        elif prod_lider_sem > 0:
            lider_msg = "🎯 ¡TU EQUIPO TE NECESITA! Es momento de reorganizar y empujar"
            lider_msg_color = "#ff4444"
        else:
            lider_msg = "📋 Sin registros del día — captura tu primera auditoría"
            lider_msg_color = "#475569"

        st.markdown(
            f"""<div class="leader-banner">
                <div class="leader-title">📊 LÍDER DE ÁREA: {area_objetivo}</div>
                <div class="leader-name">{"👩‍✈️" if normalizar_clave(lider_nombre.split()[0]) in {"ARELI","MARIA","SANDRA","LAURA","ANA","PATRICIA","ROSA","CARMEN","LUCIA","ELENA"} else "👨‍✈️"} {lider_nombre}</div>
                <div style="font-size:clamp(14px,1.6vmin,22px);font-weight:800;color:{lider_msg_color};
                     margin:4px 0 2px 0;letter-spacing:0.02em;">{lider_msg}</div>
                <div class="leader-metrics">
                    <div class="leader-met-box" style="{_box_style(c_hoy)}">
                        <div style="color:#94A3B8; font-weight:bold; font-size:18px;">EFICIENCIA EQUIPO HOY</div>
                        <div class="leader-met-val" style="color:{c_hoy};">{prod_lider_hoy:.1f}%</div>
                    </div>
                    <div class="leader-met-box" style="{_box_style(c_sem)}">
                        <div style="color:#94A3B8; font-weight:bold; font-size:18px;">ACUMULADO SEMANAL</div>
                        <div class="leader-met-val" style="color:{c_sem};">{prod_lider_sem:.1f}%</div>
                    </div>
                    <div class="leader-met-box" style="{_box_style(color_aporte_lider)}">
                        <div style="color:#94A3B8; font-weight:bold; font-size:18px;">APORTE SEMANAL</div>
                        <div class="leader-met-val" style="color:{color_aporte_lider};">{aporte_lider_sem:.1f}%</div>
                    </div>
                </div>
            </div>
            <div class="barra-bono-aviso">
                ⚠&nbsp; BONO FINAL = productividad 40% + asistencia 30% + puntualidad 30% &nbsp;·&nbsp; Consulta a RRHH
            </div>""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)

        def _ranking(df, con_aporte=False):
            if df.empty:
                return []
            ranking = (
                df.groupby(col_colab)["__PROD_NUM"]
                .mean()
                .reset_index()
                .sort_values("__PROD_NUM", ascending=False)
                .values.tolist()
            )
            def _etiqueta(i, nom, val):
                if i == 0 and val >= 90.0:
                    return f"👑 {nom}"
                if val == 100.0:
                    return f"{nom} 🔥"
                return nom

            if con_aporte:
                return [
                    (
                        _etiqueta(i, nom, val),
                        val,
                        _aporte_bono_html(val),
                        f"{dias_por_op.get(nom, 0)} de {total_dias_semana} días laborados",
                    )
                    for i, (nom, val) in enumerate(ranking)
                ]
            return [(_etiqueta(i, nom, val), val) for i, (nom, val) in enumerate(ranking)]

        with c1:
            st.markdown(
                _tabla_paginada_html(
                    _ranking(df_hoy),
                    f'🎯 DESEMPEÑO DE HOY ({fecha_hoy.strftime("%d/%m/%Y")})',
                    "#10B981",
                ),
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                _tabla_paginada_html(
                    _ranking(df_area_sem_raw, con_aporte=True),
                    f'📅 CÓMO VA MI SEMANA ({inicio_sem.strftime("%d/%m")} — {fin_sem.strftime("%d/%m")})',
                    "#3B82F6",
                ),
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"Error en productividad de área: {e}")


# --- 5. CALIDAD ---
_TTL_CALIDAD = 300  # 5 minutos — refresca capturas extraordinarias sin martillar la API


def _cache_valido(clave_ts):
    ts = st.session_state.get(clave_ts, 0)
    return (datetime.now().timestamp() - ts) < _TTL_CALIDAD


def cargar_datos_vaciado():
    clave = "df_vaciado"
    clave_ts = "df_vaciado_ts"
    if (
        _cache_valido(clave_ts)
        and clave in st.session_state
        and not st.session_state[clave].empty
    ):
        return st.session_state[clave]
    df = leer_datos_seguro(ID_LIBRO_CALIDAD, "VACIADO", header_row=0)
    if df is None or df.empty:
        return st.session_state.get(clave, pd.DataFrame())
    col_fecha = df.columns[0]
    col_total = next(
        (c for c in df.columns if "TOTAL" in str(c).upper() and "PZ" in str(c).upper()),
        None,
    )
    if col_total is None:
        return st.session_state.get(clave, pd.DataFrame())
    df = df[[col_fecha, col_total]].copy()
    df.columns = ["FECHA", "TOTAL_PZ"]
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df["TOTAL_PZ"] = pd.to_numeric(df["TOTAL_PZ"], errors="coerce").fillna(0)
    df = df.dropna(subset=["FECHA"])
    st.session_state[clave] = df
    st.session_state[clave_ts] = datetime.now().timestamp()
    return df


def cargar_datos_calidad():
    clave = "df_calidad"
    clave_ts = "df_calidad_ts"
    if (
        _cache_valido(clave_ts)
        and clave in st.session_state
        and not st.session_state[clave].empty
    ):
        return st.session_state[clave]
    df = leer_datos_seguro(ID_LIBRO_CALIDAD, "LISTA_DEFECTOS", header_row=0)
    if df is None or df.empty:
        return st.session_state.get(clave, pd.DataFrame())
    df = df.iloc[:, :4].copy()
    df.columns = ["FECHA", "PIEZA", "CANTIDAD", "DEFECTO"]
    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0)
    df["AREA"] = df["DEFECTO"].str.strip().str.upper().map(DEFECTO_A_AREA)
    df = df.dropna(subset=["FECHA"])
    st.session_state[clave] = df
    st.session_state[clave_ts] = datetime.now().timestamp()
    return df


def _html_calidad_area(df_cal, area_nom, fecha_hoy):
    if df_cal is None or df_cal.empty:
        return ""
    _ini, _ = calcular_fechas_semana_corta(fecha_hoy)
    inicio_sem = pd.Timestamp(_ini)
    fin_sem = pd.Timestamp(fecha_hoy)
    inicio_sem_ant = inicio_sem - timedelta(days=7)
    fin_sem_ant = inicio_sem - timedelta(days=1)
    areas_con_rechazo = set(DEFECTO_A_AREA.values())
    if area_nom not in areas_con_rechazo:
        return ""
    df_area = df_cal[
        (df_cal["AREA"] == area_nom)
        & (df_cal["DEFECTO"].str.strip().str.upper() != "PRUEBA CALIDAD")
    ]
    esta_sem = int(
        df_area[(df_area["FECHA"] >= inicio_sem) & (df_area["FECHA"] <= fin_sem)][
            "CANTIDAD"
        ].sum()
    )
    sem_ant = int(
        df_area[
            (df_area["FECHA"] >= inicio_sem_ant) & (df_area["FECHA"] <= fin_sem_ant)
        ]["CANTIDAD"].sum()
    )
    if sem_ant == 0 and esta_sem == 0:
        color_sem = "#475569"
        tendencia_txt = "sin rechazos esta semana"
    elif sem_ant == 0:
        color_sem = "#94A3B8"
        tendencia_txt = "SEM. ANT. SIN DATOS"
    else:
        cambio = (esta_sem - sem_ant) / sem_ant * 100
        if cambio <= -10:
            color_sem = "#2ecc71"
            tendencia_txt = f"▼ {abs(cambio):.0f}% vs sem. ant."
        elif cambio <= 10:
            color_sem = "#f1c40f"
            tendencia_txt = f"≈ similar sem. ant."
        else:
            color_sem = "#ff4444"
            tendencia_txt = f"▲ {cambio:.0f}% vs sem. ant."
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f"background:#0D1B2A;border:1px solid {color_sem}55;border-radius:8px;"
        f'padding:clamp(3px,0.5vmin,7px) clamp(8px,1vmin,14px);margin:3px 0;">'
        f'<span style="color:#64748B;font-size:clamp(10px,1.1vmin,15px);font-weight:800;white-space:nowrap;">'
        f"⬡ RECHAZOS SEM.</span>"
        f'<span style="color:{color_sem};font-size:clamp(12px,1.3vmin,18px);font-weight:900;white-space:nowrap;">'
        f"{esta_sem} pzas &nbsp;·&nbsp; {tendencia_txt}</span>"
        f"</div>"
    )


OBJETIVO_RECHAZO_PCT = 5.0


def renderizar_pantalla_reconocimiento(fecha_hoy):
    """Muestra el mejor operador del día y de la semana por área."""
    df_prod = leer_datos_con_respaldo("REGISTRO", 0, id_libro=ID_LIBRO_PROD)
    if df_prod.empty:
        st.markdown(
            '<div style="background:#0F1720;min-height:96vh;display:flex;align-items:center;'
            'justify-content:center;"><span style="color:#475569;font-size:2vmin;">Sin datos</span></div>',
            unsafe_allow_html=True,
        )
        return
    try:
        col_fecha = encontrar_columna(df_prod, ["FECHA"])
        col_colab = encontrar_columna(df_prod, ["COLABORADOR", "NOMBRE", "OPERADOR"])
        col_eficiencia = (
            encontrar_columna(df_prod, ["PRODUCTIVIDADR"])
            or encontrar_columna(df_prod, ["PRODUCTIVIDAD", "EFICIENCIA"])
        )
        col_actividad = encontrar_columna(df_prod, ["ACTIVIDAD"])
        col_area = encontrar_columna(df_prod, ["AREA", "PROCESO"])
        if not col_fecha or not col_colab or not col_eficiencia:
            return

        df_prod["__FECHA_DT"] = pd.to_datetime(
            df_prod[col_fecha], dayfirst=True, errors="coerce"
        ).dt.date
        df_prod["__PROD_NUM"] = pd.to_numeric(
            df_prod[col_eficiencia].astype(str).str.replace("%", "").str.strip(),
            errors="coerce",
        ).fillna(0.0).clip(upper=100.0)
        df_prod["__AREA_PISO"] = df_prod.apply(
            lambda r: clasificar_colaborador_area(r, col_area, col_actividad), axis=1
        )

        lideres_norm = {normalizar_clave(n) for n in NOMBRES_LIDERES}
        df_ops = df_prod[
            ~df_prod[col_colab].astype(str).apply(normalizar_clave).isin(lideres_norm)
        ].copy()

        inicio_sem, fin_sem = calcular_fechas_semana_corta(fecha_hoy)
        corte_sem = min(fecha_hoy, fin_sem)

        AREAS = [
            ("MOLDEO Y CORAZONES", "🔵 MOLDEO", "#3B82F6"),
            ("CORTE", "🟡 CORTE", "#F59E0B"),
            ("ENSAMBLE", "🟢 ENSAMBLE", "#10B981"),
        ]

        def _mejor(df_area, tipo):
            if df_area.empty:
                return None, 0.0
            if tipo == "hoy":
                df_f = df_area[df_area["__FECHA_DT"] == fecha_hoy]
                if df_f.empty:
                    return None, 0.0
                r = df_f.groupby(col_colab)["__PROD_NUM"].mean().sort_values(ascending=False)
            else:
                df_sem = df_area[
                    (df_area["__FECHA_DT"] >= inicio_sem)
                    & (df_area["__FECHA_DT"] <= corte_sem)
                ]
                if df_sem.empty:
                    return None, 0.0
                df_d = df_sem.groupby([col_colab, "__FECHA_DT"])["__PROD_NUM"].mean().reset_index()
                df_d = df_d[df_d["__PROD_NUM"] > 0]
                if df_d.empty:
                    return None, 0.0
                r = df_d.groupby(col_colab)["__PROD_NUM"].mean().sort_values(ascending=False)
            return (r.index[0], float(r.iloc[0])) if not r.empty else (None, 0.0)

        def _color_v(v):
            if v >= 90: return "#2ecc71"
            if v >= 70: return "#f1c40f"
            return "#ff4444"

        def _card(area_key, area_label, color, tipo):
            badge_icon = "⭐" if tipo == "hoy" else "📅"
            badge_txt = "MEJOR DEL DÍA" if tipo == "hoy" else "MEJOR DE LA SEMANA"
            trofeo = "🥇" if tipo == "hoy" else "👑"
            df_a = df_ops[df_ops["__AREA_PISO"] == area_key]
            nombre, pct = _mejor(df_a, tipo)
            if nombre is None:
                return (
                    f'<div style="background:#161E2E;border:2px solid #1E293B;border-radius:24px;'
                    f'padding:clamp(12px,1.8vmin,24px);text-align:center;flex:1;display:flex;'
                    f'flex-direction:column;align-items:center;justify-content:center;gap:4px;">'
                    f'<div style="font-size:clamp(18px,2.4vmin,34px);font-weight:900;color:{color};'
                    f'text-transform:uppercase;letter-spacing:0.08em;">{area_label}</div>'
                    f'<div style="font-size:clamp(14px,1.8vmin,26px);font-weight:800;color:#64748B;'
                    f'text-transform:uppercase;">{badge_icon} {badge_txt}</div>'
                    f'<div style="color:#334155;font-size:clamp(18px,2.2vmin,30px);margin-top:12px;">Sin datos</div>'
                    f'</div>'
                )
            c = _color_v(pct)
            nombre_corto = " ".join(str(nombre).split()[:2])
            return (
                f'<div style="background:#161E2E;border:2px solid {color}55;border-radius:24px;'
                f'padding:clamp(12px,1.8vmin,24px);text-align:center;flex:1;display:flex;'
                f'flex-direction:column;align-items:center;gap:clamp(2px,0.5vmin,6px);">'
                f'<div style="font-size:clamp(18px,2.4vmin,34px);font-weight:900;color:{color};'
                f'text-transform:uppercase;letter-spacing:0.08em;">{area_label}</div>'
                f'<div style="font-size:clamp(14px,1.8vmin,26px);font-weight:800;color:#64748B;'
                f'text-transform:uppercase;letter-spacing:0.04em;">{badge_icon} {badge_txt}</div>'
                f'<div style="font-size:clamp(52px,9vmin,130px);line-height:1;margin-top:auto;">{trofeo}</div>'
                f'<div style="font-size:clamp(26px,4.5vmin,66px);font-weight:950;color:#F1F5F9;'
                f'line-height:1.1;">{nombre_corto}</div>'
                f'<div style="font-size:clamp(44px,10vmin,144px);font-weight:950;color:{c};'
                f'line-height:1;margin-bottom:auto;">{pct:.1f}%</div>'
                f'</div>'
            )

        cards_hoy = "".join(_card(ak, al, col, "hoy") for ak, al, col in AREAS)
        cards_sem = "".join(_card(ak, al, col, "sem") for ak, al, col in AREAS)

        st.markdown(
            f'<div style="background:#0F1720;min-height:96vh;padding:clamp(10px,1.4vmin,20px) clamp(18px,2.2vw,40px);'
            f'display:flex;flex-direction:column;gap:clamp(8px,1.2vmin,14px);box-sizing:border-box;">'
            f'<div style="text-align:center;font-size:clamp(22px,2.8vmin,42px);font-weight:900;color:#F1F5F9;'
            f'text-transform:uppercase;letter-spacing:0.06em;">🏆 RECONOCIMIENTO AL DESEMPEÑO</div>'
            f'<div style="display:flex;gap:clamp(10px,1.4vmin,18px);flex:1;">{cards_hoy}</div>'
            f'<div style="display:flex;gap:clamp(10px,1.4vmin,18px);flex:1;">{cards_sem}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.error(f"Error en pantalla de reconocimiento: {exc}")


def renderizar_pantalla_calidad(fecha_hoy):
    try:
        df_cal = cargar_datos_calidad()
        df_vac = cargar_datos_vaciado()

        _ini_sem, _ = calcular_fechas_semana_corta(fecha_hoy)
        inicio_sem = pd.Timestamp(_ini_sem)
        fin_sem = pd.Timestamp(fecha_hoy)
        inicio_sem_ant = inicio_sem - timedelta(days=7)
        fin_sem_ant = inicio_sem - timedelta(days=1)

        # Separar rechazos reales de pruebas de calidad
        es_prueba = lambda df: (
            df["DEFECTO"].str.strip().str.upper() == "PRUEBA CALIDAD"
            if not df.empty
            else pd.Series(dtype=bool)
        )
        df_rechazos = df_cal[~es_prueba(df_cal)] if not df_cal.empty else pd.DataFrame()
        df_pruebas = df_cal[es_prueba(df_cal)] if not df_cal.empty else pd.DataFrame()

        def _suma_rec(desde, hasta):
            if df_rechazos.empty:
                return 0
            return int(
                df_rechazos[
                    (df_rechazos["FECHA"] >= desde) & (df_rechazos["FECHA"] <= hasta)
                ]["CANTIDAD"].sum()
            )

        def _suma_vac(df, desde, hasta):
            if df is None or df.empty:
                return 0
            return int(
                df[(df["FECHA"] >= desde) & (df["FECHA"] <= hasta)]["TOTAL_PZ"].sum()
            )

        def _filas_vac(desde, hasta):
            if df_vac is None or df_vac.empty:
                return 0
            return len(df_vac[(df_vac["FECHA"] >= desde) & (df_vac["FECHA"] <= hasta)])

        def _filas_pruebas(desde, hasta):
            if df_pruebas.empty:
                return 0
            return len(
                df_pruebas[
                    (df_pruebas["FECHA"] >= desde) & (df_pruebas["FECHA"] <= hasta)
                ]
            )

        rechazados_sem = _suma_rec(inicio_sem, fin_sem)
        producidos_sem = _suma_vac(df_vac, inicio_sem, fin_sem)
        rechazados_ant = _suma_rec(inicio_sem_ant, fin_sem_ant)
        producidos_ant = _suma_vac(df_vac, inicio_sem_ant, fin_sem_ant)

        pct_rechazo = (
            (rechazados_sem / producidos_sem * 100) if producidos_sem > 0 else 0.0
        )
        pct_calidad = 100.0 - pct_rechazo
        pct_rechazo_ant = (
            (rechazados_ant / producidos_ant * 100) if producidos_ant > 0 else 0.0
        )

        # Rechazo del mes en curso
        inicio_mes = pd.Timestamp(fecha_hoy.replace(day=1))
        rechazados_mes = _suma_rec(inicio_mes, fin_sem)
        producidos_mes = _suma_vac(df_vac, inicio_mes, fin_sem)
        pct_rechazo_mes = (
            (rechazados_mes / producidos_mes * 100) if producidos_mes > 0 else 0.0
        )
        if pct_rechazo_mes <= OBJETIVO_RECHAZO_PCT:
            color_mes = "#2ecc71"
        elif pct_rechazo_mes <= 7.0:
            color_mes = "#f1c40f"
        else:
            color_mes = "#ff4444"

        # Cumplimiento pruebas de calidad
        hoy_ts = pd.Timestamp(fecha_hoy)
        vaciadas_hoy = _filas_vac(hoy_ts, hoy_ts)
        pruebas_hoy = _filas_pruebas(hoy_ts, hoy_ts)
        vaciadas_sem = _filas_vac(inicio_sem, fin_sem)
        pruebas_sem = _filas_pruebas(inicio_sem, fin_sem)
        cumpl_hoy = (pruebas_hoy / vaciadas_hoy * 100) if vaciadas_hoy > 0 else None
        cumpl_sem = (pruebas_sem / vaciadas_sem * 100) if vaciadas_sem > 0 else None

        def _color_prueba(pct):
            if pct is None:
                return "#94A3B8"
            if pct >= 100:
                return "#2ecc71"
            if pct >= 80:
                return "#f1c40f"
            return "#ff4444"

        cp_hoy_color = _color_prueba(cumpl_hoy)
        cp_sem_color = _color_prueba(cumpl_sem)
        cp_hoy_txt = (
            f"{pruebas_hoy}/{vaciadas_hoy} · {cumpl_hoy:.0f}%"
            if cumpl_hoy is not None
            else "Sin vaciadas hoy"
        )
        cp_sem_txt = (
            f"{pruebas_sem}/{vaciadas_sem} · {cumpl_sem:.0f}%"
            if cumpl_sem is not None
            else "Sin datos"
        )

        # Semáforo calidad
        if pct_rechazo <= OBJETIVO_RECHAZO_PCT:
            color_cal = "#2ecc71"
            estado_badge = "OBJETIVO CUMPLIDO"
            badge_bg = "#0f3b22"
        elif pct_rechazo <= 7.0:
            color_cal = "#f1c40f"
            estado_badge = "CERCA DEL LÍMITE"
            badge_bg = "#3f3508"
        else:
            color_cal = "#ff4444"
            estado_badge = "FUERA DE OBJETIVO"
            badge_bg = "#441111"

        # Ranking defectos (excluye PRUEBA CALIDAD)
        df_sem_rec = (
            df_rechazos[
                (df_rechazos["FECHA"] >= inicio_sem) & (df_rechazos["FECHA"] <= fin_sem)
            ]
            if not df_rechazos.empty
            else pd.DataFrame()
        )
        defectos = (
            df_sem_rec.groupby("DEFECTO")["CANTIDAD"].sum().sort_values(ascending=False)
            if not df_sem_rec.empty
            else pd.Series(dtype=float)
        )
        max_def = defectos.max() if len(defectos) > 0 else 1

        def _icono_prueba(pct):
            if pct is None: return "⚪"
            if pct >= 100: return "✅"
            if pct >= 80: return "⚠️"
            return "❌"

        icono_hoy = _icono_prueba(cumpl_hoy)
        icono_sem = _icono_prueba(cumpl_sem)

        filas_def = ""
        for defecto, cantidad in defectos.head(7).items():
            area_def = DEFECTO_A_AREA.get(str(defecto).strip().upper(), "")
            color_area = "#3B82F6" if area_def == "MOLDEO" else "#F59E0B" if area_def == "CORTE" else "#94A3B8"
            emoji_area = "🔵" if area_def == "MOLDEO" else "🟡" if area_def == "CORTE" else "⚪"
            pct_bar = (cantidad / max_def * 100) if max_def > 0 else 0
            pct_tot = (cantidad / rechazados_sem * 100) if rechazados_sem > 0 else 0
            filas_def += (
                f'<div style="display:flex;align-items:center;gap:clamp(12px,1.5vw,24px);'
                f'min-height:clamp(50px,7vmin,90px);border-bottom:1px solid #1E293B;padding:0 6px;">'
                f'<div style="width:32%;min-width:0;display:flex;align-items:center;gap:10px;">'
                f'<span style="font-size:clamp(18px,2.2vmin,32px);">{emoji_area}</span>'
                f'<div style="min-width:0;">'
                f'<div style="font-size:clamp(18px,2.3vmin,34px);font-weight:900;color:#F1F5F9;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{defecto}</div>'
                f'<div style="font-size:clamp(11px,1.2vmin,16px);color:{color_area};font-weight:800;'
                f'text-transform:uppercase;letter-spacing:0.04em;">{area_def}</div>'
                f'</div></div>'
                f'<div style="flex:1;">'
                f'<div style="background:#1E293B;border-radius:8px;height:clamp(24px,3.5vmin,48px);overflow:hidden;">'
                f'<div style="width:{pct_bar:.1f}%;height:100%;background:{color_cal};border-radius:8px;"></div>'
                f'</div></div>'
                f'<div style="min-width:clamp(60px,8vw,110px);text-align:right;white-space:nowrap;">'
                f'<span style="font-size:clamp(22px,2.8vmin,42px);font-weight:950;color:#F1F5F9;">{int(cantidad)}</span>'
                f'<span style="margin-left:6px;font-size:clamp(13px,1.5vmin,20px);color:#64748B;font-weight:700;">{pct_tot:.0f}%</span>'
                f'</div>'
                f'</div>'
            )

        # Pieza más afectada (siempre visible)
        inicio_4sem = pd.Timestamp(inicio_sem - timedelta(days=28))

        def _build_pieza_html(label, pieza, cant_sem, p_color, p_txt, cant_color):
            return (
                f'<div style="background:#0D1B2A;border:2px solid {p_color}44;border-radius:14px;padding:clamp(10px,1.4vmin,18px) clamp(16px,2vw,32px);display:flex;align-items:center;gap:20px;">'
                f'<div style="flex:0 0 auto;">'
                f'<div style="font-size:clamp(10px,1.1vmin,15px);color:#64748B;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;">{label}</div>'
                f'<div style="font-size:clamp(20px,2.8vmin,40px);font-weight:950;color:#F1F5F9;">{pieza}</div>'
                f"</div>"
                f'<div style="width:2px;background:#1E293B;align-self:stretch;border-radius:2px;"></div>'
                f'<div style="flex:0 0 auto;text-align:center;">'
                f'<div style="font-size:clamp(10px,1.1vmin,15px);color:#64748B;font-weight:800;text-transform:uppercase;">RECHAZOS SEM.</div>'
                f'<div style="font-size:clamp(24px,3.2vmin,46px);font-weight:950;color:{cant_color};">{cant_sem}</div>'
                f"</div>"
                f'<div style="width:2px;background:#1E293B;align-self:stretch;border-radius:2px;"></div>'
                f'<div style="flex:1;">'
                f'<span style="font-size:clamp(13px,1.6vmin,22px);font-weight:900;color:{p_color};">{p_txt}</span>'
                f"</div>"
                f"</div>"
            )

        if not df_sem_rec.empty:
            # Hay rechazos esta semana — mostrar la pieza más afectada
            pieza_rechazos = df_sem_rec.groupby("PIEZA")["CANTIDAD"].sum()
            top_pieza = pieza_rechazos.idxmax()
            top_pieza_cant = int(pieza_rechazos.max())
            df_pieza_hist = df_rechazos[df_rechazos["PIEZA"] == top_pieza].copy()
            df_pieza_4sem = df_pieza_hist[
                (df_pieza_hist["FECHA"] >= inicio_4sem)
                & (df_pieza_hist["FECHA"] < inicio_sem)
            ]
            if not df_pieza_4sem.empty:
                df_pieza_4sem["_SEM"] = (
                    df_pieza_4sem["FECHA"] - inicio_4sem
                ).dt.days // 7
                prom_4sem = df_pieza_4sem.groupby("_SEM")["CANTIDAD"].sum().mean()
                cambio_p = (
                    ((top_pieza_cant - prom_4sem) / prom_4sem * 100)
                    if prom_4sem > 0
                    else 0
                )
                if cambio_p <= -10:
                    p_color = "#2ecc71"
                    p_txt = f"▼ {abs(cambio_p):.0f}% vs prom. 4 sem. ({prom_4sem:.0f} pzas/sem)"
                elif cambio_p <= 10:
                    p_color = "#f1c40f"
                    p_txt = f"≈ similar al promedio 4 sem. ({prom_4sem:.0f} pzas/sem)"
                else:
                    p_color = "#ff4444"
                    p_txt = (
                        f"▲ {cambio_p:.0f}% vs prom. 4 sem. ({prom_4sem:.0f} pzas/sem)"
                    )
            else:
                df_pieza_antes = df_pieza_hist[df_pieza_hist["FECHA"] < inicio_sem]
                if not df_pieza_antes.empty:
                    ultima_fecha = df_pieza_antes["FECHA"].max()
                    ultima_cant = int(
                        df_pieza_hist[df_pieza_hist["FECHA"] == ultima_fecha][
                            "CANTIDAD"
                        ].sum()
                    )
                    sem_atras = max(
                        1, (inicio_sem.date() - ultima_fecha.date()).days // 7
                    )
                    p_color = "#f1c40f"
                    p_txt = (
                        f"Último rechazo: hace {sem_atras} sem. ({ultima_cant} pzas)"
                    )
                else:
                    p_color = "#ff4444"
                    p_txt = "⚠ PRIMER RECHAZO REGISTRADO"
            pieza_html = _build_pieza_html(
                "PIEZA MÁS AFECTADA",
                top_pieza,
                top_pieza_cant,
                p_color,
                p_txt,
                color_cal,
            )
        else:
            # Sin rechazos esta semana — mostrar pieza históricamente más problemática como referencia
            df_hist_4sem = (
                df_rechazos[
                    (df_rechazos["FECHA"] >= inicio_4sem)
                    & (df_rechazos["FECHA"] < inicio_sem)
                ]
                if not df_rechazos.empty
                else pd.DataFrame()
            )
            if not df_hist_4sem.empty:
                pieza_ref = df_hist_4sem.groupby("PIEZA")["CANTIDAD"].sum().idxmax()
                cant_ref = int(df_hist_4sem.groupby("PIEZA")["CANTIDAD"].sum().max())
                pieza_html = _build_pieza_html(
                    "PIEZA A VIGILAR (HISTORIAL 4 SEM.)",
                    pieza_ref,
                    0,
                    "#2ecc71",
                    f"✓ Sin rechazos esta semana · Historial: {cant_ref} pzas en 4 sem.",
                    "#2ecc71",
                )
            else:
                pieza_html = (
                    f'<div style="background:#0D1B2A;border:2px solid #2ecc7144;border-radius:14px;padding:clamp(10px,1.4vmin,18px) clamp(16px,2vw,32px);display:flex;align-items:center;justify-content:center;">'
                    f'<span style="font-size:clamp(16px,2vmin,28px);font-weight:900;color:#2ecc71;">✓ SEMANA LIMPIA — Sin rechazos registrados</span>'
                    f"</div>"
                )

        # Tendencia rechazos
        if rechazados_ant > 0:
            cambio = (rechazados_sem - rechazados_ant) / rechazados_ant * 100
            if cambio <= -10:
                t_color, t_icon, t_txt = (
                    "#2ecc71",
                    "▼",
                    f"{abs(cambio):.1f}% menos rechazos que la semana anterior",
                )
            elif cambio <= 10:
                t_color, t_icon, t_txt = (
                    "#f1c40f",
                    "≈",
                    f"Similar a la semana anterior ({rechazados_ant} pzas rechazadas)",
                )
            else:
                t_color, t_icon, t_txt = (
                    "#ff4444",
                    "▲",
                    f"{cambio:.1f}% más rechazos que la semana anterior",
                )
            sem_ant_txt = (
                f'<span style="color:{t_color};font-weight:900;font-size:clamp(14px,1.6vmin,22px);">{t_icon} {t_txt}</span>'
                f'<span style="color:#64748B;font-size:clamp(12px,1.3vmin,18px);margin-left:16px;">Sem. ant.: {rechazados_ant} pzas &nbsp;·&nbsp; {pct_rechazo_ant:.1f}% rechazo</span>'
            )
        else:
            sem_ant_txt = '<span style="color:#64748B;font-size:clamp(13px,1.4vmin,18px);">Sin datos de semana anterior</span>'

        tabla_defectos = (
            f'<div style="display:flex;flex-direction:column;height:100%;">{filas_def}</div>'
            if filas_def
            else (
                f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;'
                f'flex:1;padding:clamp(16px,3vmin,48px) 0;">'
                f'<div style="font-size:clamp(40px,6vmin,80px);">✅</div>'
                f'<div style="font-size:clamp(22px,3vmin,44px);font-weight:950;color:#2ecc71;margin-top:12px;">'
                f'SEMANA LIMPIA</div>'
                f'<div style="font-size:clamp(14px,1.7vmin,24px);color:#475569;font-weight:700;margin-top:8px;">'
                f'Sin rechazos registrados esta semana</div>'
                f'</div>'
            )
        )

        _div = lambda: '<div style="width:2px;background:#1E293B;border-radius:2px;align-self:stretch;"></div>'
        _lbl = lambda t: f'<div style="font-size:clamp(13px,1.5vmin,21px);color:#64748B;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">{t}</div>'
        _num_color = lambda v, c: f'<div style="font-size:clamp(38px,5.8vmin,82px);font-weight:950;color:{c};line-height:1;">{v}</div>'
        _sub = lambda t: f'<div style="font-size:clamp(11px,1.2vmin,16px);color:#475569;font-weight:700;margin-top:2px;">{t}</div>'

        html = (
            f'<div style="background:#0F1720;min-height:96vh;padding:clamp(14px,1.8vmin,26px) clamp(18px,2.2vw,40px);'
            f'display:flex;flex-direction:column;gap:clamp(8px,1.2vmin,14px);box-sizing:border-box;">'
            # Encabezado
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-size:clamp(20px,2.4vmin,36px);font-weight:900;color:#94A3B8;'
            f'text-transform:uppercase;letter-spacing:0.06em;">🔬 CALIDAD DE LA SEMANA</span>'
            f'<span style="background:{badge_bg};color:{color_cal};border:2px solid {color_cal};'
            f'border-radius:999px;padding:clamp(4px,0.6vmin,8px) clamp(14px,1.8vw,26px);'
            f'font-size:clamp(14px,1.6vmin,22px);font-weight:900;">{estado_badge}</span>'
            f'</div>'
            # Fila de métricas UNIFICADA — 5 columnas en una sola tarjeta
            f'<div style="background:#161E2E;border:2px solid #1E293B;border-radius:20px;'
            f'padding:clamp(10px,1.4vmin,20px) clamp(16px,2vw,36px);'
            f'display:flex;align-items:center;justify-content:space-around;gap:0;">'
            # % RECHAZO — destacado con color semáforo, borde izquierdo de acento
            f'<div style="text-align:center;padding:0 clamp(8px,1.2vw,20px);'
            f'border-left:4px solid {color_cal};padding-left:clamp(12px,1.5vw,24px);">'
            f'{_lbl("% RECHAZO")}'
            f'<div style="font-size:clamp(38px,5.5vmin,78px);font-weight:950;color:{color_cal};line-height:1;">{pct_rechazo:.1f}%</div>'
            f'{_sub(f"META: &lt; {OBJETIVO_RECHAZO_PCT:.0f}%")}'
            f'</div>'
            f'{_div()}'
            # RECHAZADAS
            f'<div style="text-align:center;padding:0 clamp(8px,1.2vw,20px);">'
            f'{_lbl("RECHAZADAS")}'
            f'{_num_color(rechazados_sem, "#F1F5F9")}'
            f'{_sub("piezas")}'
            f'</div>'
            f'{_div()}'
            # PRODUCIDAS
            f'<div style="text-align:center;padding:0 clamp(8px,1.2vw,20px);">'
            f'{_lbl("PRODUCIDAS")}'
            f'{_num_color(f"{producidos_sem:,}", "#F1F5F9")}'
            f'{_sub("esta semana")}'
            f'</div>'
            f'{_div()}'
            # % CALIDAD
            f'<div style="text-align:center;padding:0 clamp(8px,1.2vw,20px);">'
            f'{_lbl("% CALIDAD")}'
            f'{_num_color(f"{pct_calidad:.1f}%", "#F1F5F9")}'
            f'{_sub(f"obj. &ge; {100 - OBJETIVO_RECHAZO_PCT:.0f}%")}'
            f'</div>'
            f'{_div()}'
            # % RECHAZO MES
            f'<div style="text-align:center;padding:0 clamp(8px,1.2vw,20px);">'
            f'{_lbl("% RECHAZO MES")}'
            f'<div style="font-size:clamp(38px,5.5vmin,78px);font-weight:950;color:{color_mes};line-height:1;">{pct_rechazo_mes:.1f}%</div>'
            f'{_sub(f"{rechazados_mes} pzas &nbsp;·&nbsp; {producidos_mes:,} prod.")}'
            f'</div>'
            f'</div>'
            # Pieza más afectada
            f'{pieza_html}'
            # Ranking defectos
            f'<div style="background:#161E2E;border:2px solid #1E293B;border-radius:20px;'
            f'padding:clamp(12px,1.6vmin,22px) clamp(16px,2vw,32px);flex:1;display:flex;flex-direction:column;">'
            f'<div style="font-size:clamp(15px,1.8vmin,26px);font-weight:900;color:#3B82F6;'
            f'text-transform:uppercase;letter-spacing:0.06em;border-bottom:2px solid #1E293B;'
            f'padding-bottom:8px;margin-bottom:4px;">📊 RANKING DE DEFECTOS</div>'
            f'{tabla_defectos}'
            f'</div>'
            # Barra tendencia + pruebas de calidad
            f'<div style="background:#0D1B2A;border:1px solid #1E293B;border-radius:12px;'
            f'padding:clamp(8px,1.2vmin,16px) clamp(16px,2vw,32px);display:flex;align-items:center;'
            f'justify-content:space-between;gap:16px;">'
            f'<div style="display:flex;align-items:center;gap:16px;">{sem_ant_txt}</div>'
            f'<div style="display:flex;align-items:center;gap:clamp(6px,0.8vw,14px);'
            f'border-left:1px solid #1E293B;padding-left:clamp(12px,1.5vw,24px);flex-shrink:0;">'
            f'<span style="font-size:clamp(10px,1.2vmin,16px);color:#64748B;font-weight:800;'
            f'text-transform:uppercase;letter-spacing:0.04em;">PRUEBAS CAL.</span>'
            f'<span style="font-size:clamp(16px,2vmin,26px);">{icono_hoy}</span>'
            f'<span style="font-size:clamp(11px,1.3vmin,17px);color:{cp_hoy_color};font-weight:900;">'
            f'HOY&nbsp;{cp_hoy_txt}</span>'
            f'<span style="color:#334155;font-size:clamp(14px,1.6vmin,20px);">·</span>'
            f'<span style="font-size:clamp(16px,2vmin,26px);">{icono_sem}</span>'
            f'<span style="font-size:clamp(11px,1.3vmin,17px);color:{cp_sem_color};font-weight:900;">'
            f'SEM&nbsp;{cp_sem_txt}</span>'
            f'</div>'
            f'</div>'
            f"</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Error en pantalla de calidad: {exc}")


# --- 6. SEGURIDAD ---
DIAS_META_CELEBRACION = 100


def cargar_datos_seguridad():
    clave = "df_seguridad"
    clave_ts = "df_seguridad_ts"
    if (
        _cache_valido(clave_ts)
        and clave in st.session_state
        and not st.session_state.get(clave, pd.DataFrame()).empty
    ):
        return st.session_state[clave]
    df = leer_datos_seguro(ID_LIBRO, "SEGURIDAD", header_row=0)
    if df is None or df.empty:
        return st.session_state.get(clave, pd.DataFrame())
    col_fecha = encontrar_columna(df, ["FECHA"])
    col_area = encontrar_columna(df, ["AREA"])
    col_tipo = encontrar_columna(df, ["TIPO"])
    col_desc = encontrar_columna(df, ["DESCRIPCION", "DESC", "DETALLE"])
    if col_fecha is None:
        return st.session_state.get(clave, pd.DataFrame())
    cols = {k: v for k, v in {
        "FECHA": col_fecha, "AREA": col_area,
        "TIPO": col_tipo, "DESCRIPCION": col_desc,
    }.items() if v is not None}
    df_out = df[[v for v in cols.values()]].copy()
    df_out.columns = list(cols.keys())
    df_out["FECHA"] = pd.to_datetime(df_out["FECHA"], dayfirst=True, errors="coerce")
    df_out = df_out.dropna(subset=["FECHA"]).sort_values("FECHA").reset_index(drop=True)
    st.session_state[clave] = df_out
    st.session_state[clave_ts] = datetime.now().timestamp()
    return df_out


def _metricas_seguridad(df, fecha_hoy):
    fecha_ts = pd.Timestamp(fecha_hoy)
    if df.empty:
        return 0, 0, None, []
    tiene_tipo = "TIPO" in df.columns
    if tiene_tipo:
        tipos = df["TIPO"].str.strip().str.upper()
        df_acc = df[tipos == "ACCIDENTE"].copy()
        df_ini = df[tipos == "INICIO"].copy()
        df_hist = df[tipos != "INICIO"].copy()
    else:
        df_acc = df.copy()
        df_ini = pd.DataFrame()
        df_hist = df.copy()
    ultimo_acc = df_acc["FECHA"].max() if not df_acc.empty else None
    dias_hoy = int((fecha_ts - ultimo_acc).days) if ultimo_acc is not None else int((fecha_ts - df["FECHA"].min()).days)
    fechas_acc = sorted(df_acc["FECHA"].tolist()) if not df_acc.empty else []
    gaps = []
    if not df_ini.empty and fechas_acc:
        g0 = (fechas_acc[0] - df_ini["FECHA"].min()).days
        if g0 > 0:
            gaps.append(g0)
    for i in range(len(fechas_acc) - 1):
        g = (fechas_acc[i + 1] - fechas_acc[i]).days
        if g > 0:
            gaps.append(g)
    gaps.append(dias_hoy)
    record = max(gaps) if gaps else dias_hoy
    historial = df_hist.tail(5).iloc[::-1].to_dict("records")
    return dias_hoy, record, ultimo_acc, historial


def _confetti_html():
    colors = ["#2ecc71", "#f1c40f", "#3B82F6", "#ff4444", "#a855f7", "#f97316", "#fff", "#e91e8c"]
    pieces = ""
    for i in range(80):
        color = colors[i % len(colors)]
        left = (i * 1.27) % 100
        delay = (i * 0.17) % 4
        dur = 2.5 + (i % 6) * 0.42
        size = 8 + (i % 5) * 2
        shape = "border-radius:50%;" if i % 3 == 0 else ""
        pieces += (
            f'<div style="position:fixed;left:{left:.1f}%;top:-20px;width:{size}px;height:{size}px;'
            f'background:{color};{shape}animation:confettiFall {dur:.2f}s {delay:.2f}s linear infinite;'
            f'z-index:9997;pointer-events:none;"></div>'
        )
    return pieces


def renderizar_pantalla_seguridad(fecha_hoy):
    try:
        df = cargar_datos_seguridad()
        dias_hoy, record, ultimo_acc, historial = _metricas_seguridad(df, fecha_hoy)
        if dias_hoy >= 30:
            color_seg, estado_seg, badge_bg = "#2ecc71", "EXCELENTE", "#0f3b22"
        elif dias_hoy >= 10:
            color_seg, estado_seg, badge_bg = "#f1c40f", "EN ALERTA", "#3f3508"
        else:
            color_seg, estado_seg, badge_bg = "#ff4444", "ATENCIÓN INMEDIATA", "#441111"
        es_record_actual = dias_hoy >= record and dias_hoy > 0
        record_color = "#2ecc71" if es_record_actual else "#f1c40f"
        record_label = "🏆 ¡NUEVO RÉCORD!" if es_record_actual else "🏆 RÉCORD"
        faltan = max(0, DIAS_META_CELEBRACION - dias_hoy)
        pct_meta = min(dias_hoy / DIAS_META_CELEBRACION * 100, 100)
        meta_txt = "🎉 ¡META DE 100 DÍAS CUMPLIDA!" if dias_hoy >= DIAS_META_CELEBRACION else f"Faltan {faltan} días para la comida 🍽"
        meta_color = "#2ecc71" if dias_hoy >= DIAS_META_CELEBRACION else "#94A3B8"
        ultimo_txt = (
            f'Último accidente: {ultimo_acc.strftime("%d/%m/%Y")}' if ultimo_acc is not None
            else "Sin accidentes registrados"
        )
        # Fondo teñido según semáforo
        if dias_hoy >= 30:
            card_bg = "linear-gradient(160deg,#0a1f10 0%,#161E2E 60%)"
        elif dias_hoy >= 10:
            card_bg = "linear-gradient(160deg,#1a1500 0%,#161E2E 60%)"
        else:
            card_bg = "linear-gradient(160deg,#1a0505 0%,#161E2E 60%)"
        # Frases rotativas (motivacionales + prevención)
        n_frases = len(FRASES_SEGURIDAD)
        dur_total = n_frases * 5
        frases_divs = "".join(
            f'<div class="frase-seg" style="animation-delay:{i * 5}s;">{f}</div>'
            for i, f in enumerate(FRASES_SEGURIDAD)
        )

        # Anillo SVG de progreso
        # Incidencias por área
        area_filas = ""
        if not df.empty and "AREA" in df.columns and "TIPO" in df.columns:
            df_ev = df[df["TIPO"].str.strip().str.upper().isin(["ACCIDENTE", "INCIDENTE"])].copy()
            if not df_ev.empty:
                df_ev["_M"] = df_ev["FECHA"].dt.month
                df_ev["_Y"] = df_ev["FECHA"].dt.year
                for area in AREAS_PISO:
                    df_a = df_ev[df_ev["AREA"].str.strip().str.upper() == area]
                    n_mes = len(df_a[(df_a["_M"] == fecha_hoy.month) & (df_a["_Y"] == fecha_hoy.year)])
                    n_year = len(df_a[df_a["_Y"] == fecha_hoy.year])
                    c = "#2ecc71" if n_mes == 0 else ("#f1c40f" if n_mes == 1 else "#ff4444")
                    area_filas += (
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:clamp(10px,1.3vmin,18px) clamp(10px,1.2vw,18px);border-bottom:1px solid #1E293B;">'
                        f'<span style="font-size:clamp(18px,2.2vmin,32px);font-weight:800;color:#F1F5F9;">{area}</span>'
                        f'<div style="display:flex;gap:32px;">'
                        f'<div style="text-align:center;">'
                        f'<div style="font-size:clamp(12px,1.3vmin,17px);color:#475569;font-weight:700;text-transform:uppercase;">Mes</div>'
                        f'<div style="font-size:clamp(26px,3.4vmin,48px);font-weight:950;color:{c};">{n_mes}</div>'
                        f'</div>'
                        f'<div style="text-align:center;">'
                        f'<div style="font-size:clamp(12px,1.3vmin,17px);color:#475569;font-weight:700;text-transform:uppercase;">Año</div>'
                        f'<div style="font-size:clamp(26px,3.4vmin,48px);font-weight:950;color:#94A3B8;">{n_year}</div>'
                        f'</div></div></div>'
                    )

        # Historial
        hist_filas = ""
        for ev in historial:
            f_ev = ev.get("FECHA")
            t_ev = str(ev.get("TIPO", "")).strip().upper()
            a_ev = str(ev.get("AREA", "")).strip()
            d_ev = str(ev.get("DESCRIPCION", "")).strip()
            c_t = "#ff4444" if t_ev == "ACCIDENTE" else ("#f1c40f" if t_ev == "INCIDENTE" else "#94A3B8")
            f_str = f_ev.strftime("%d/%m/%Y") if pd.notna(f_ev) else "—"
            det = d_ev[:38] if d_ev and d_ev not in ("", "nan") else ""
            hist_filas += (
                f'<div style="display:flex;align-items:center;gap:14px;'
                f'padding:clamp(7px,1vmin,14px) 0;border-bottom:1px solid #0D1B2A;">'
                f'<span style="color:#64748B;font-size:clamp(15px,1.8vmin,24px);white-space:nowrap;font-weight:700;">{f_str}</span>'
                f'<span style="background:{c_t}22;color:{c_t};border:1px solid {c_t}55;border-radius:999px;'
                f'padding:4px 12px;font-size:clamp(13px,1.5vmin,20px);font-weight:900;white-space:nowrap;">{t_ev}</span>'
                f'<span style="color:#94A3B8;font-size:clamp(15px,1.8vmin,24px);font-weight:700;white-space:nowrap;">{a_ev}</span>'
                f'<span style="color:#475569;font-size:clamp(14px,1.6vmin,21px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{det}</span>'
                f'</div>'
            )

        celebracion_html = ""
        if dias_hoy >= DIAS_META_CELEBRACION:
            celebracion_html = (
                f'<div style="position:fixed;inset:0;pointer-events:none;z-index:9996;">'
                f'{_confetti_html()}'
                f'</div>'
                f'<div style="position:fixed;bottom:clamp(60px,8vh,100px);left:50%;transform:translateX(-50%);'
                f'z-index:9999;background:linear-gradient(135deg,#0a2e1a,#0f3b22);'
                f'border:4px solid #2ecc71;border-radius:28px;'
                f'padding:clamp(14px,2vmin,24px) clamp(28px,4vw,60px);text-align:center;'
                f'box-shadow:0 0 60px #2ecc7166;animation:parpadeo 2s infinite;">'
                f'<div style="font-size:clamp(24px,3vmin,44px);font-weight:950;color:#2ecc71;'
                f'text-transform:uppercase;letter-spacing:0.06em;">🎉 ¡{dias_hoy} DÍAS SIN ACCIDENTES!</div>'
                f'<div style="font-size:clamp(22px,2.6vmin,38px);font-weight:900;color:#fff;margin-top:8px;">'
                f'🍽&nbsp;&nbsp;¡LA CASA INVITA!&nbsp;&nbsp;🍽</div>'
                f'</div>'
            )

        # Anillo SVG — más grande
        _r, _cx, _cy = 88, 110, 110
        _circ = 2 * 3.14159 * _r
        _dash = _circ * pct_meta / 100
        _gap = _circ - _dash
        anillo_svg = (
            f'<div style="position:relative;width:clamp(220px,38vmin,460px);height:clamp(220px,38vmin,460px);margin:0 auto;">'
            f'<svg viewBox="0 0 220 220" style="width:100%;height:100%;">'
            f'<circle cx="{_cx}" cy="{_cy}" r="{_r}" fill="none" stroke="#1E293B" stroke-width="14"/>'
            f'<circle cx="{_cx}" cy="{_cy}" r="{_r}" fill="none" stroke="{color_seg}" stroke-width="14"'
            f' stroke-dasharray="{_dash:.1f} {_gap:.1f}" stroke-linecap="round"'
            f' transform="rotate(-90 {_cx} {_cy})"/>'
            f'</svg>'
            f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">'
            f'<div style="font-size:clamp(80px,14vmin,180px);font-weight:950;color:{color_seg};line-height:0.85;">{dias_hoy}</div>'
            f'<div style="font-size:clamp(14px,1.7vmin,24px);color:#475569;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;">días</div>'
            f'</div>'
            f'</div>'
        )

        no_area = '<div style="color:#475569;text-align:center;padding:28px;font-size:clamp(17px,2vmin,28px);font-weight:700;">Sin incidencias registradas ✓</div>'
        no_hist = '<div style="color:#2ecc71;text-align:center;padding:18px;font-size:clamp(17px,2vmin,28px);font-weight:700;">✓ Sin eventos registrados</div>'

        # Frases rotativas con animación CSS
        frases_wrap = (
            f'<div style="position:relative;height:clamp(68px,8.5vmin,120px);width:100%;overflow:hidden;'
            f'--total-frases:{n_frases};">'
            f'<style>.frase-seg{{animation-duration:{dur_total}s!important;}}</style>'
            f'{frases_divs}'
            f'</div>'
        )

        html = (
            f'<div style="background:#0F1720;min-height:96vh;padding:clamp(12px,1.6vmin,22px) clamp(16px,2vw,36px);'
            f'display:flex;flex-direction:column;gap:clamp(8px,1.1vmin,14px);box-sizing:border-box;">'
            # Encabezado
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-size:clamp(28px,3.6vmin,56px);font-weight:900;color:#94A3B8;'
            f'text-transform:uppercase;letter-spacing:0.06em;">🦺 SEGURIDAD EN PLANTA</span>'
            f'<span style="background:{badge_bg};color:{color_seg};border:2px solid {color_seg};'
            f'border-radius:999px;padding:clamp(5px,0.6vmin,10px) clamp(14px,1.8vw,26px);'
            f'font-size:clamp(14px,1.6vmin,22px);font-weight:900;">{estado_seg}</span>'
            f'</div>'
            # Cuerpo
            f'<div style="display:flex;gap:clamp(12px,1.6vw,24px);flex:1;align-items:stretch;">'
            # Card izquierdo — fondo teñido + anillo grande
            f'<div style="background:{card_bg};border:4px solid {color_seg};border-radius:24px;'
            f'padding:clamp(14px,1.8vmin,26px) clamp(12px,1.8vw,28px);display:flex;flex-direction:column;'
            f'align-items:center;justify-content:space-between;flex:1.2;text-align:center;">'
            f'<div style="font-size:clamp(24px,3vmin,46px);color:#64748B;font-weight:900;'
            f'text-transform:uppercase;letter-spacing:0.06em;">DÍAS SIN ACCIDENTES</div>'
            f'{anillo_svg}'
            # Meta + frases rotativas
            f'<div style="width:100%;">'
            f'<div style="font-size:clamp(15px,1.8vmin,24px);color:{meta_color};font-weight:800;margin-bottom:6px;">{meta_txt}</div>'
            f'{frases_wrap}'
            f'</div>'
            # Récord
            f'<div style="width:100%;background:{badge_bg};border:2px solid {record_color};border-radius:14px;'
            f'padding:clamp(8px,1vmin,14px);text-align:center;">'
            f'<span style="font-size:clamp(20px,2.5vmin,38px);font-weight:900;color:{record_color};">'
            f'{record_label}: {record} días</span></div>'
            f'<div style="font-size:clamp(13px,1.5vmin,20px);color:#475569;font-weight:700;">{ultimo_txt}</div>'
            f'</div>'
            # Panel derecho
            f'<div style="display:flex;flex-direction:column;gap:clamp(10px,1.3vmin,16px);flex:1;">'
            f'<div style="background:#161E2E;border:2px solid #1E293B;border-radius:20px;'
            f'padding:clamp(12px,1.6vmin,22px);flex:1;">'
            f'<div style="font-size:clamp(16px,1.9vmin,28px);font-weight:900;color:#3B82F6;'
            f'text-transform:uppercase;border-bottom:2px solid #1E293B;'
            f'padding-bottom:8px;margin-bottom:10px;">INCIDENCIAS POR ÁREA</div>'
            f'{area_filas or no_area}'
            f'</div>'
            f'<div style="background:#0D1B2A;border:2px solid #1E293B;border-radius:20px;'
            f'padding:clamp(12px,1.6vmin,22px);">'
            f'<div style="font-size:clamp(16px,1.9vmin,28px);font-weight:900;color:#64748B;'
            f'text-transform:uppercase;border-bottom:1px solid #1E293B;'
            f'padding-bottom:8px;margin-bottom:10px;">ÚLTIMOS EVENTOS</div>'
            f'{hist_filas or no_hist}'
            f'</div>'
            f'</div>'
            f'</div>'
            f'{celebracion_html}'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Error en pantalla de seguridad: {exc}")


# --- 7. MOTOR PRINCIPAL CON INTERCALADO ---
def main_piso():
    from streamlit_autorefresh import st_autorefresh

    # El autorefresh corre cada 30 segundos y dispara el cambio de pantalla
    st_autorefresh(interval=REFRESH_INTERVAL_MS, key="refresh")
    ahora = ahora_local()
    fecha_hoy = ahora.date()

    # Reloj fijo + barra countdown — visible en todas las pantallas
    _segs = REFRESH_INTERVAL_MS // 1000
    _ts = int(ahora.timestamp())  # cambia cada segundo → fuerza recreación del DOM
    st.markdown(
        f'<style>@keyframes cdf{_ts}{{from{{width:100%}}to{{width:0%}}}}</style>'
        f'<div style="position:fixed;top:10px;right:14px;z-index:10000;'
        f'background:#0D1B2A;border:1px solid #1E293B;border-radius:10px;'
        f'padding:5px 16px;font-size:clamp(18px,2.2vmin,30px);font-weight:900;color:#475569;">'
        f'🕐 {ahora.strftime("%H:%M")}</div>'
        f'<div data-ts="{_ts}" style="position:fixed;top:0;left:0;right:0;height:6px;z-index:10000;">'
        f'<div style="height:100%;background:linear-gradient(90deg,#3B82F6,#2ecc71);'
        f'animation:cdf{_ts} {_segs}s linear forwards;"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- ENRUTADOR SECUENCIAL POR SESIÓN ---
    secuencia_vistas = [
        "cumplimiento",
        "prod_moldeo",
        "cumplimiento",
        "prod_corte",
        "cumplimiento",
        "prod_ensamble",
        "reconocimiento",
        "cumplimiento",
        "calidad",
        "cumplimiento",
        "seguridad",
    ]
    if "ciclo_idx" not in st.session_state:
        st.session_state.ciclo_idx = 0
    vista_actual = secuencia_vistas[st.session_state.ciclo_idx]
    st.session_state.ciclo_idx = (st.session_state.ciclo_idx + 1) % len(
        secuencia_vistas
    )

    if vista_actual == "prod_moldeo":
        renderizar_pantalla_productividad_por_area(
            fecha_hoy, "MOLDEO Y CORAZONES", "JOSÉ ANTONIO REYES RUBIO"
        )
        return
    elif vista_actual == "prod_corte":
        renderizar_pantalla_productividad_por_area(
            fecha_hoy, "CORTE", "LUIS DAVID ESPINOSA TORRES"
        )
        return
    elif vista_actual == "prod_ensamble":
        renderizar_pantalla_productividad_por_area(
            fecha_hoy, "ENSAMBLE", "ARELI PALOMA FLORES GARFIAS"
        )
        return
    elif vista_actual == "reconocimiento":
        renderizar_pantalla_reconocimiento(fecha_hoy)
        return
    elif vista_actual == "calidad":
        renderizar_pantalla_calidad(fecha_hoy)
        return
    elif vista_actual == "seguridad":
        renderizar_pantalla_seguridad(fecha_hoy)
        return

    # --- VISTA: CUMPLIMIENTO DE PRODUCCIÓN ---
    try:
        df_p = leer_datos_con_respaldo("PROGRAMA", 1)
        df_b = leer_datos_con_respaldo("BDD", 0)
        df_a = leer_datos_con_respaldo("AUDITAR", 0)
    except Exception as exc:
        st.warning(
            f"No se pudieron refrescar datos, usando ultimo respaldo disponible: {exc}"
        )
        df_p = st.session_state.get(
            "ultimo_df_PROGRAMA", leer_respaldo_local("ultimo_df_PROGRAMA")
        )
        df_b = st.session_state.get(
            "ultimo_df_BDD", leer_respaldo_local("ultimo_df_BDD")
        )
        df_a = st.session_state.get(
            "ultimo_df_AUDITAR", leer_respaldo_local("ultimo_df_AUDITAR")
        )

    col_p = {
        "area": encontrar_columna(df_p, ["AREA", "PROCESO"]),
        "pieza": encontrar_columna(df_p, ["PIEZA"]),
        "fecha": encontrar_columna(df_p, ["FECHA"]),
        "total": encontrar_columna(df_p, ["TOTAL"]),
        "modo_herraje": encontrar_columna(df_p, ["MODO HERRAJE", "MODO_HERRAJE"]),
    }
    col_b = {
        "pieza": encontrar_columna(df_b, ["PIEZA"]),
        "subproceso": encontrar_columna(
            df_b,
            ["SUBPROCESO", "SUB PROCESO", "SUB_PROCESO"],
            contiene_todos=["SUB", "CESO"],
        ),
        "proceso": encontrar_columna(df_b, ["PROCESO", "AREA"]),
        "activo": encontrar_columna(df_b, ["ACTIVO", "ESTATUS", "COL_4"]),
    }
    df_b = filtrar_bdd_activa(df_b, col_b)

    df_res, col_a = obtener_datos_unificados(df_a, df_p, df_b, col_p, col_b, fecha_hoy)
    if df_res is not None and not df_res.empty:
        guardar_respaldo_resultado(df_res, col_a, fecha_hoy)
    else:
        df_res, col_a = leer_respaldo_resultado(fecha_hoy, col_a)

    if df_res is None or df_res.empty:
        frases_html = "".join(
            f'<div class="frase">{frase}</div>' for frase in FRASES_ESPERA_PROGRAMA
        )
        st.markdown(
            f"""
            <div class="screensaver">
                <div class="screensaver-box">
                    <div class="screensaver-logo">GRUPO NSG</div>
                    <div style="font-size:7vw;font-weight:950;color:#2d3f4a;letter-spacing:0.04em;margin-bottom:1.5vh;">
                        {ahora.strftime("%H:%M")}
                    </div>
                    <div class="screensaver-status">EN ESPERA DEL PROGRAMA DEL DIA</div>
                    <div class="screensaver-title">Preparando tablero de produccion</div>
                    <div class="screensaver-sub">En cuanto se cargue el programa, el tablero se actualizara automaticamente.</div>
                    <div class="frases-wrap">{frases_html}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Lógica de Ritmo Dinámico
    t_dec = ahora.hour + (ahora.minute / 60)
    if t_dec < 11.0:
        prog_b = (t_dec - 8.0) / 3.0
        base_corte = 0.0
        aporte_corte = 33.3
        ideal_ahora = max(0, prog_b * aporte_corte)
        b_nom = "BLOQUE 1"
        corte_actual = "11:00 AM (3h)"
        corte_anterior = None
    elif t_dec < 14.0:
        prog_b = (t_dec - 11.0) / 3.0
        base_corte = 33.3
        aporte_corte = 33.3
        ideal_ahora = base_corte + (prog_b * aporte_corte)
        b_nom = "BLOQUE 2"
        corte_actual = "14:00 PM (6h)"
        corte_anterior = "11:00 AM (3h)"
    else:
        prog_b = (t_dec - 14.0) / 3.0
        base_corte = 66.6
        aporte_corte = 33.4
        ideal_ahora = base_corte + (prog_b * aporte_corte)
        b_nom = "BLOQUE 3"
        corte_actual = "17:00 PM (9h)"
        corte_anterior = "14:00 PM (6h)"
    ideal_ahora = min(100.0, ideal_ahora)
    meta_corte_ahora = max(0.0, min(aporte_corte, ideal_ahora - base_corte))
    info_horario = obtener_info_horario(t_dec)
    corte_pendiente = corte_vencido(t_dec)
    ideal_ahora = info_horario["ideal"]
    b_nom = info_horario["bloque"]
    areas_con_programa = [
        area
        for area in AREAS_PISO
        if not df_res[
            df_res[col_p["area"]].apply(normalizar_clave) == normalizar_clave(area)
        ].empty
    ]
    auditoria_pendiente_global = corte_pendiente is not None and any(
        not corte_con_captura_area(
            df_a,
            col_a,
            area,
            fecha_hoy,
            corte_pendiente["nombre"],
        )
        for area in areas_con_programa
    )

    df_calidad = cargar_datos_calidad()
    cargar_datos_seguridad()

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    slots = [c1, c2, c3, c4]

    for idx, area_nom in enumerate(AREAS_PISO):
        with slots[idx]:
            df_area = df_res[
                df_res[col_p["area"]].apply(normalizar_clave)
                == normalizar_clave(area_nom)
            ].copy()
            if not df_area.empty:
                df_area_calculo, moldeo_diferidos_pausados = (
                    filtrar_subprocesos_exigibles_area(
                        df_area,
                        area_nom,
                        t_dec,
                    )
                )
                moldeo_sin_exigibles = (
                    moldeo_diferidos_pausados and df_area_calculo.empty
                )
                # --- CÁLCULO DE EFICIENCIA REAL ---
                total_pzs = pd.to_numeric(
                    df_area_calculo.groupby(col_p["pieza"])[col_p["total"]].first(),
                    errors="coerce",
                ).sum()
                real_pzs = int(
                    pd.to_numeric(
                        df_area_calculo.groupby(col_p["pieza"])[col_a["real"]].max(),
                        errors="coerce",
                    ).sum()
                )

                # Porcentaje de avance real, calculado igual que Auditoria:
                # promedio del % REAL de cada pieza + subproceso.
                pct_real_proceso = (
                    0.0
                    if df_area_calculo.empty
                    else round(
                        pd.to_numeric(df_area_calculo["% REAL"], errors="coerce")
                        .fillna(0)
                        .mean(),
                        1,
                    )
                )

                # REGLA SOLICITADA: Avance sobre el ideal dinámico
                # Ejemplo: Si ideal es 33% y llevas 27%, tu proporción es ~81% (Verde)
                cortes_area = cortes_auditados_area(df_a, col_a, area_nom, fecha_hoy)
                esperando_auditoria = False
                pendiente_incompleto = auditoria_pendiente_global
                esperando_primera_auditoria = (
                    t_dec < 11.0
                    and not corte_con_captura_area(
                        df_a,
                        col_a,
                        area_nom,
                        fecha_hoy,
                        CORTES[0]["nombre"],
                    )
                )
                if esperando_primera_auditoria:
                    corte_eval = CORTES[0]
                    corte_prev = None
                    corte_actual = corte_eval["nombre"]
                    corte_anterior = None
                    base_corte = corte_eval["base"]
                    aporte_corte = corte_eval["aporte"]
                    meta_corte_ahora = max(info_horario["meta_corte"], 0.01)
                    esperando_auditoria = True
                    estado_corte_html = (
                        '<div class="mini-pagina">ESPERANDO PRIMERA AUDITORIA</div>'
                    )
                elif pendiente_incompleto:
                    corte_eval = corte_pendiente
                    corte_prev = corte_anterior_de(corte_eval)
                    corte_actual = corte_eval["nombre"]
                    corte_anterior = corte_prev["nombre"] if corte_prev else None
                    base_corte = corte_eval["base"]
                    aporte_corte = corte_eval["aporte"]
                    meta_corte_ahora = aporte_corte
                    esperando_auditoria = True
                    estado_corte_html = f'<div class="mini-pagina">ESPERANDO AUDITORIA {corte_eval["label"]}</div>'
                elif cortes_area:
                    corte_eval = cortes_area[-1]
                    corte_prev = corte_anterior_de(corte_eval)
                    if corte_pendiente and CORTES.index(corte_eval) < CORTES.index(
                        corte_pendiente
                    ):
                        esperando_auditoria = True
                        corte_eval = corte_pendiente
                        corte_prev = corte_anterior_de(corte_eval)
                    corte_actual = corte_eval["nombre"]
                    corte_anterior = corte_prev["nombre"] if corte_prev else None
                    base_corte = corte_eval["base"]
                    aporte_corte = corte_eval["aporte"]
                    meta_corte_ahora = aporte_corte
                    if esperando_auditoria:
                        estado_corte_html = f'<div class="mini-pagina">ESPERANDO AUDITORIA {corte_eval["label"]}</div>'
                    elif corte_eval["nombre"] != info_horario["corte_actual"]["nombre"]:
                        idx_eval = CORTES.index(corte_eval)
                        corte_esperado = CORTES[min(idx_eval + 1, len(CORTES) - 1)]
                        estado_corte_html = (
                            f'<div class="mini-pagina">CORTE EVALUADO: {corte_eval["label"]} '
                            f'- ESPERANDO {corte_esperado["label"]}</div>'
                        )
                    else:
                        estado_corte_html = f'<div class="mini-pagina">CORTE EVALUADO: {corte_eval["label"]}</div>'
                elif t_dec >= 11.0:
                    corte_eval = info_horario["corte_actual"]
                    corte_prev = info_horario["corte_anterior"]
                    corte_actual = corte_eval["nombre"]
                    corte_anterior = corte_prev["nombre"] if corte_prev else None
                    base_corte = corte_eval["base"]
                    aporte_corte = corte_eval["aporte"]
                    meta_corte_ahora = aporte_corte
                    esperando_auditoria = True
                    estado_corte_html = f'<div class="mini-pagina">ESPERANDO AUDITORIA {corte_eval["label"]}</div>'
                else:
                    corte_eval = info_horario["corte_actual"]
                    corte_prev = info_horario["corte_anterior"]
                    corte_actual = corte_eval["nombre"]
                    corte_anterior = corte_prev["nombre"] if corte_prev else None
                    base_corte = corte_eval["base"]
                    aporte_corte = corte_eval["aporte"]
                    meta_corte_ahora = info_horario["meta_corte"]
                    estado_corte_html = f'<div class="mini-pagina">EVALUANDO CORTE {corte_eval["label"]}</div>'

                pct_real_corte = calcular_pct_corte_area(
                    df_area_calculo,
                    df_a,
                    col_a,
                    col_p,
                    area_nom,
                    fecha_hoy,
                    corte_actual,
                    corte_anterior,
                )
                if pct_real_corte is None:
                    pct_real_corte = max(
                        0.0, min(aporte_corte, pct_real_proceso - base_corte)
                    )
                if moldeo_sin_exigibles:
                    ideal_ahora = 0.0
                    meta_corte_ahora = 0.0
                    pct_real_corte = 0.0
                avance_corte = max(0.0, min(aporte_corte, pct_real_corte))
                proporcion_avance = (
                    (avance_corte / meta_corte_ahora * 100)
                    if meta_corte_ahora > 0
                    else 100
                )
                cumplimiento_acumulado = (
                    (pct_real_proceso / ideal_ahora * 100) if ideal_ahora > 0 else 100
                )
                meta_auditoria_vigente = max(base_corte + aporte_corte, 0.01)
                cumplimiento_auditoria_vigente = (
                    pct_real_proceso / meta_auditoria_vigente * 100
                )
                usar_ultima_auditoria_para_color = (
                    not esperando_auditoria
                    and corte_eval["nombre"] != info_horario["corte_actual"]["nombre"]
                )
                indicador_color = (
                    cumplimiento_auditoria_vigente
                    if usar_ultima_auditoria_para_color
                    else cumplimiento_acumulado
                )
                ritmo_mostrado = (
                    cumplimiento_auditoria_vigente
                    if usar_ultima_auditoria_para_color
                    else proporcion_avance
                )
                recuperando_atraso = (
                    not esperando_auditoria
                    and not usar_ultima_auditoria_para_color
                    and proporcion_avance >= 90
                    and cumplimiento_acumulado < 90
                )
                if moldeo_sin_exigibles:
                    ritmo_mostrado = 0.0

                if indicador_color >= 90:
                    color_cuadro = "#2ecc71"
                    estado_texto = "✅ VAMOS BIEN"
                    estado_clase = "estado-verde"
                elif recuperando_atraso:
                    color_cuadro = "#f1c40f"
                    estado_texto = "📈 RECUPERANDO"
                    estado_clase = "estado-amarillo"
                elif indicador_color >= 70:
                    color_cuadro = "#f1c40f"
                    estado_texto = "⚠ EN RIESGO"
                    estado_clase = "estado-amarillo"
                else:
                    color_cuadro = "#E32B13"
                    estado_texto = "🔴 VAMOS ATRÁS"
                    estado_clase = "estado-rojo"
                if esperando_auditoria:
                    color_cuadro = "#607d8b"
                    estado_texto = "⏳ ESPERA AUD."
                    estado_clase = "estado-espera"
                if moldeo_sin_exigibles:
                    color_cuadro = "#607d8b"
                    estado_texto = "⏸ DIFERIDO"
                    estado_clase = "estado-espera"

                cierre_turno = (
                    not esperando_auditoria
                    and corte_eval["nombre"] == CORTES[-1]["nombre"]
                    and corte_pendiente == CORTES[-1]
                )
                if cierre_turno:
                    if cumplimiento_acumulado >= 90:
                        color_cuadro = "#2ecc71"
                        estado_texto = "🏁 OBJETIVO OK"
                        estado_clase = "estado-verde"
                    elif cumplimiento_acumulado >= 80:
                        color_cuadro = "#f1c40f"
                        estado_texto = "⚠ CERCA META"
                        estado_clase = "estado-amarillo"
                    else:
                        color_cuadro = "#E32B13"
                        estado_texto = "❌ NO CUMPLIDO"
                        estado_clase = "estado-rojo"

                if esperando_auditoria:
                    flecha = "-"
                elif moldeo_sin_exigibles:
                    flecha = "-"
                elif usar_ultima_auditoria_para_color:
                    flecha = "▲" if cumplimiento_auditoria_vigente >= 90 else "▼"
                else:
                    flecha = "▲" if pct_real_proceso >= ideal_ahora else "▼"
                esp_pzs = int(total_pzs * (ideal_ahora / 100))

                # --- MINI TABLA (AVANCE POR PROCESO) ---
                resumen = df_area_calculo[
                    [
                        col_p["pieza"],
                        "__BDD_SUBPROCESO",
                        col_p["total"],
                        col_a["real"],
                        "% REAL",
                    ]
                ].copy()
                resumen[col_p["total"]] = convertir_serie_numerica(
                    resumen[col_p["total"]]
                ).fillna(0)
                resumen[col_a["real"]] = convertir_serie_numerica(
                    resumen[col_a["real"]]
                ).fillna(0)
                if usar_ultima_auditoria_para_color:
                    resumen["__P_PROP"] = (
                        pd.to_numeric(resumen["% REAL"], errors="coerce").fillna(0)
                        / meta_auditoria_vigente
                        * 100
                    )
                else:
                    resumen["__P_PROP"] = (
                        (
                            pd.to_numeric(resumen["% REAL"], errors="coerce").fillna(0)
                            - base_corte
                        ).clip(lower=0, upper=aporte_corte)
                        / meta_corte_ahora
                        * 100
                        if meta_corte_ahora > 0
                        else 100
                    )
                resumen = resumen.sort_values("__P_PROP", ascending=True)
                total_paginas = max(
                    1,
                    (len(resumen) + MINI_FILAS_POR_PAGINA - 1) // MINI_FILAS_POR_PAGINA,
                )
                paginas = []
                for pagina_idx in range(total_paginas):
                    inicio = pagina_idx * MINI_FILAS_POR_PAGINA
                    fin = inicio + MINI_FILAS_POR_PAGINA
                    resumen_pagina = resumen.iloc[inicio:fin]
                    filas_pagina = ""
                    for _, r in resumen_pagina.iterrows():
                        p_tot = r[col_p["total"]]
                        p_rea = r[col_a["real"]]
                        p_sub = str(r["__BDD_SUBPROCESO"])
                        p_pct = (
                            pd.to_numeric(pd.Series([r["% REAL"]]), errors="coerce")
                            .fillna(0)
                            .iloc[0]
                        )

                        # Color individual basado en la misma regla del 80% del ritmo
                        if usar_ultima_auditoria_para_color:
                            p_prop = p_pct / meta_auditoria_vigente * 100
                        else:
                            p_avance_corte = max(
                                0.0, min(aporte_corte, p_pct - base_corte)
                            )
                            p_prop = (
                                (p_avance_corte / meta_corte_ahora * 100)
                                if meta_corte_ahora > 0
                                else 100
                            )
                        c_f = (
                            "#2ecc71"
                            if p_prop >= 90
                            else ("#f1c40f" if p_prop >= 70 else "#E32B13")
                        )

                        filas_pagina += (
                            "<tr><td>"
                            f"<div class='mini-main'><span class='mini-piece'>{str(r[col_p['pieza']])[:24]}</span>"
                            f"<span style='color:{c_f}; font-weight:900;'>{p_pct:.0f}%</span></div>"
                            f"<div class='mini-main'><span class='mini-sub'>{p_sub[:42]}</span>"
                            f"<span class='mini-real'>{int(p_rea)}/{int(p_tot)}</span></div>"
                            "</td></tr>"
                        )

                    clase_pagina = "mini-page"
                    paginas.append(
                        f'<div class="{clase_pagina}">'
                        f'<table class="mini-tabla"><tbody>{filas_pagina}</tbody></table>'
                        f"</div>"
                    )
                clase_track = (
                    "mini-track mini-track-unica"
                    if total_paginas == 1
                    else "mini-track"
                )
                shift_vh = -8 * total_paginas
                duracion = total_paginas * 4
                animacion = (
                    "animation:none;"
                    if total_paginas == 1
                    else f"animation:miniTrack {duracion}s steps({total_paginas}) infinite;"
                )
                mini_tabla_html = (
                    "\n"
                    f'<div class="{clase_track}" style="--pages:{total_paginas}; --shift:{shift_vh}vh; {animacion}">'
                    f'{"".join(paginas)}'
                    "</div>"
                )
                pagina_html = (
                    f'\n<div class="mini-pagina">{len(resumen)} actividades - rota cada 4s</div>'
                    if total_paginas > 1
                    else ""
                )

                # --- ÚLTIMO PARO ---
                paro_html = ""
                if (
                    col_a
                    and col_a.get("area")
                    and col_a.get("fecha")
                    and col_a.get("notas")
                ):
                    df_p_a = df_a[
                        df_a[col_a["area"]].apply(normalizar_clave)
                        == normalizar_clave(area_nom)
                    ].copy()
                    df_p_a["__F"] = normalizar_fecha_serie(df_p_a[col_a["fecha"]])
                    df_p_a = df_p_a[df_p_a["__F"] == fecha_hoy.strftime("%d/%m/%Y")]
                else:
                    df_p_a = pd.DataFrame()
                if not df_p_a.empty:
                    df_n = df_p_a[
                        df_p_a[col_a["notas"]].astype(str).str.contains(r"\[", na=False)
                    ]
                    if not df_n.empty:
                        paro_html = f'<div class="paro-alert">⚠ ÚLTIMO PARO: {df_n[col_a["notas"]].iloc[-1]}</div>'

                hay_paro_real = False
                ultimo_paro = ""
                if not df_p_a.empty and col_a and col_a.get("notas"):
                    notas_paro = df_p_a[col_a["notas"]].astype(str)
                    df_paros_reales = df_p_a[
                        notas_paro.str.contains(r"\[", na=False)
                        & ~notas_paro.str.contains(
                            r"\[SIN PARO", case=False, na=False
                        )
                    ]
                    hay_paro_real = not df_paros_reales.empty
                    if hay_paro_real:
                        ultimo_paro = df_paros_reales[col_a["notas"]].iloc[-1]

                if hay_paro_real:
                    paro_html = f'<div class="paro-alert paro-rojo">⚠ ÚLTIMO PARO: {ultimo_paro}</div>'
                elif esperando_primera_auditoria:
                    paro_html = '<div class="paro-alert paro-espera">ESPERANDO CAPTURA DE PRIMERA AUDITORIA</div>'
                elif esperando_auditoria:
                    paro_html = f'<div class="paro-alert paro-espera">ESPERANDO CAPTURA DE AUDITORIA {corte_eval["label"]}</div>'
                elif proporcion_avance < 90:
                    paro_html = '<div class="paro-alert paro-amarillo">⚠ SIN PARO REPORTADO: no hay paro que justifique el atraso</div>'
                else:
                    paro_html = '<div class="paro-alert paro-verde">✓ SIN PAROS: avance dentro del mínimo esperado</div>'

                if not hay_paro_real and not esperando_auditoria:
                    if recuperando_atraso:
                        paro_html = '<div class="paro-alert paro-amarillo">VAMOS RECUPERANDO: buen ritmo, falta alcanzar la meta</div>'
                    elif proporcion_avance < 70:
                        paro_html = '<div class="paro-alert paro-rojo">VAMOS ATRASADOS: sin paro registrado que lo justifique</div>'
                    elif proporcion_avance < 90:
                        paro_html = '<div class="paro-alert paro-amarillo">RIESGO DE ATRASO: sin paro registrado que lo justifique</div>'
                    else:
                        paro_html = '<div class="paro-alert paro-verde">VAMOS BIEN: sin paros registrados</div>'

                if not hay_paro_real and not esperando_auditoria:
                    if cierre_turno and cumplimiento_acumulado >= 90:
                        paro_html = '<div class="paro-alert paro-verde">MUY BIEN: objetivo del turno cumplido</div>'
                    elif cierre_turno and cumplimiento_acumulado >= 80:
                        paro_html = '<div class="paro-alert paro-amarillo">QUEDAMOS CERCA: revisar pendientes para cierre</div>'
                    elif cierre_turno:
                        paro_html = '<div class="paro-alert paro-rojo">PROGRAMA NO CUMPLIDO: revisar causa y pendientes</div>'
                    elif indicador_color >= 90:
                        paro_html = '<div class="paro-alert paro-verde">VAMOS BIEN: avance acumulado dentro del minimo esperado</div>'
                    elif recuperando_atraso:
                        paro_html = '<div class="paro-alert paro-amarillo">VAMOS RECUPERANDO: buen ritmo, falta alcanzar la meta</div>'
                    elif indicador_color >= 70:
                        paro_html = '<div class="paro-alert paro-amarillo">RIESGO DE ATRASO: sin paro registrado que lo justifique</div>'
                    else:
                        paro_html = '<div class="paro-alert paro-rojo">VAMOS ATRASADOS: sin paro registrado que lo justifique</div>'

                if moldeo_sin_exigibles and not hay_paro_real:
                    paro_html = (
                        '<div class="paro-alert paro-espera">'
                        "PROCESOS DIFERIDOS POR FUSION: se evaluan desde 15:00"
                        "</div>"
                    )
                nota_moldeo_html = (
                    '<div class="nota-moldeo-diferido">Vaciado/Desmoldeo desde 15:00</div>'
                    if moldeo_diferidos_pausados
                    else ""
                )

                estado_corte_html = "\n" + estado_corte_html
                paro_html = "\n" + paro_html
                calidad_html = _html_calidad_area(df_calidad, area_nom, fecha_hoy)

                st.markdown(
                    f"""<div class="area-card" style="border-color: {color_cuadro};">
{nota_moldeo_html}
<div class="estado-badge {estado_clase}">{estado_texto}</div>
<div class="label-area">{area_nom} <span style="font-size:0.8vw; color:#444;">({b_nom})</span></div>
<div class="val-pct" style="color: {color_cuadro};">{pct_real_proceso:.1f}% <span style="font-size:2vmin;">{flecha}</span></div>
<div>
<div class="label-meta"><span>DEBERÍAMOS LLEVAR: {ideal_ahora:.1f}%</span><span>{esp_pzs} PZS</span></div>
<div class="bar-container">
  <div class="bar-fill-ideal" style="width:{ideal_ahora:.1f}%;"></div>
  <div class="bar-fill-real" style="width:{pct_real_proceso:.1f}%;background-color:{color_cuadro};"></div>
  <div class="bar-marker-ideal" style="left:{min(ideal_ahora, 98):.1f}%;"></div>
</div>
<div class="label-meta"><span>LLEVAMOS: {pct_real_proceso:.1f}%</span><span style="color:#455a64;">RITMO AUDITADO: {ritmo_mostrado:.0f}%</span></div>
</div>
<div class="mini-tabla-wrap">
{mini_tabla_html}
</div>
{calidad_html}
{estado_corte_html}
{pagina_html}
{paro_html}
</div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="area-card area-sin-programa">
                        <div class="label-area" style="color:#777;">{area_nom}</div>
                        <div class="sin-programa-texto">SIN ACTIVIDAD PROGRAMADA</div>
                        <div class="sin-programa-sub">No hay programa cargado para esta area hoy</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



if __name__ == "__main__":
    main_piso()
