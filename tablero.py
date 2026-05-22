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
        padding: 0.55rem 1rem 0.35rem 1rem !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.55rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.75rem !important; }
    @keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    .area-card {
        padding: clamp(8px, 1vmin, 12px); border-radius: 18px; border: 4px solid #333;
        background-color: #1A1A1A; height: calc((100vh - 2.6rem) / 2); margin-bottom: 0;
        display: flex; flex-direction: column; justify-content: space-between;
        position: relative; box-sizing: border-box; overflow: hidden;
    }
    .label-area { font-size: clamp(20px, 2.2vmin, 34px); font-weight: 800; color: white; text-align: center; text-transform: uppercase; }
    .val-pct { font-size: clamp(48px, 7vmin, 92px); font-weight: 900; text-align: center; margin: -4px 0; line-height: 0.95; }
    .bar-container { width: 100%; background-color: #262626; border-radius: 6px; height: clamp(12px, 1.8vmin, 20px); margin-bottom: clamp(4px, 0.8vmin, 10px); position: relative; border: 1px solid #555; overflow: hidden; }
    .bar-fill-ideal { background-color: #455a64; height: 100%; }
    .bar-fill-real { height: 100%; transition: width 0.8s; }
    .label-meta { font-size: clamp(11px, 1.25vmin, 16px); color: #9da8ad; font-weight: 900; display: flex; justify-content: space-between; margin-bottom: 3px; }
    .mini-tabla-wrap {
        height: 12vh; overflow: hidden; margin-top: clamp(2px, 0.6vmin, 6px); padding-right: 4px;
        position: relative;
    }
    .mini-tabla-wrap::-webkit-scrollbar { width: 6px; }
    .mini-tabla-wrap::-webkit-scrollbar-thumb { background: #444; border-radius: 6px; }
    .mini-track { animation: miniTrack 8s steps(1) infinite; }
    .mini-track-unica { animation: none; }
    .mini-page { height: 12vh; }
    @keyframes miniTrack {
        from { transform: translateY(0); }
        to { transform: translateY(var(--shift)); }
    }
    .mini-tabla { font-size: clamp(14px, 1.55vmin, 22px); color: #BBB; width: 100%; border-collapse: collapse; table-layout: fixed; }
    .mini-tabla td { padding: clamp(5px, 0.9vmin, 10px) 0 clamp(6px, 1vmin, 12px) 0; border-bottom: 1px solid #252525; vertical-align: top; }
    .mini-main { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: center; }
    .mini-piece { color: #F2F2F2; font-weight: 900; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .mini-sub { color: #d6e4ef; font-size: clamp(12px, 1.3vmin, 18px); font-weight: 850; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: clamp(2px, 0.6vmin, 6px); }
    .mini-real { color: #b4c9d8; font-size: clamp(12px, 1.3vmin, 18px); font-weight: 900; text-align: right; }
    .mini-pagina { font-size: clamp(8px, 0.8vmin, 12px); color: #555; text-align: right; font-weight: bold; margin-top: 2px; }
    .paro-alert { 
        padding: clamp(6px, 0.9vmin, 10px); border-radius: 10px; font-size: clamp(11px, 1.15vmin, 16px); font-weight: bold;
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
    </style>
""",
    unsafe_allow_html=True,
)

ID_LIBRO = "13ZF5TXwgEZSlrODQFF43Rvs4JmB19s6V0KNV1l72RHA"
TIMEZONE = "America/Mexico_City"
AREAS_PISO = ["MOLDEO", "CORAZONES", "CORTE", "ENSAMBLE"]
REFRESH_INTERVAL_MS = 5 * 60 * 1000
MINI_FILAS_POR_PAGINA = 1
RESPALDO_DIR = Path(".respaldo_tablero")
CORTES = [
    {"nombre": "11:00 AM (3h)", "label": "11:00", "base": 0.0, "aporte": 33.3},
    {"nombre": "14:00 PM (6h)", "label": "14:00", "base": 33.3, "aporte": 33.3},
    {"nombre": "17:00 PM (9h)", "label": "17:00", "base": 66.6, "aporte": 33.4},
]
AREA_MOLDEO = "MOLDEO"
HORA_INICIO_DIFERIDOS_MOLDEO = 15.0
SUBPROCESOS_DIFERIDOS_MOLDEO = ("VACIADO", "DESMOLDEO", "DESMOLDE")
FRASES_ESPERA_PROGRAMA = [
    "Cada pieza cuenta.",
    "La calidad empieza en cada proceso.",
    "Trabajamos seguros, trabajamos mejor.",
    "Hoy tambien podemos mejorar.",
    "El avance se construye paso a paso.",
    "Un buen turno empieza con orden.",
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


def leer_datos_con_respaldo(nombre_hoja, fila_encabezado):
    clave = f"ultimo_df_{nombre_hoja}"
    df = leer_datos_seguro(ID_LIBRO, nombre_hoja, fila_encabezado)
    if df is None or df.empty:
        version_rescate = int(datetime.now().timestamp())
        df = leer_datos_seguro(ID_LIBRO, nombre_hoja, fila_encabezado, version_rescate)
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

    df_a_area[col_a["real"]] = convertir_serie_numerica(df_a_area[col_a["real"]]).fillna(0)

    llave_base = df_area[[col_p["pieza"], "__BDD_SUBPROCESO", col_p["total"]]].copy()
    llave_base[col_p["total"]] = convertir_serie_numerica(llave_base[col_p["total"]]).fillna(0)

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
    pct_corte.loc[mask_total] = aporte_real.loc[mask_total] / total_seguro.loc[mask_total] * 100
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

    real_capturado = convertir_serie_numerica(df_area[col_a["real"]]).fillna(0).gt(0).any()
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
        for _, fila in df_a_area[[col_a["pieza"], col_a["subproceso"]]].dropna(how="any").iterrows()
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


# --- 3. MOTOR ---
def obtener_datos_unificados(df_aud, df_prog, df_bdd, col_p, col_b, fecha):
    try:
        f_str = fecha.strftime("%d/%m/%Y")
        col_a = {
            "area": encontrar_columna(df_aud, ["AREA", "PROCESO"]),
            "fecha": encontrar_columna(df_aud, ["FECHA"]),
            "pieza": encontrar_columna(df_aud, ["PIEZA"]),
            "subproceso": encontrar_columna(
                df_aud, ["SUBPROCESO", "SUB PROCESO", "SUB_PROCESO"], contiene_todos=["SUB", "CESO"]
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


# --- 4. INTERFAZ ---
def main_piso():
    from streamlit_autorefresh import st_autorefresh

    refresh_count = st_autorefresh(interval=REFRESH_INTERVAL_MS, key="refresh") or 0
    ahora = ahora_local()
    fecha_hoy = ahora.date()

    try:
        df_p = leer_datos_con_respaldo("PROGRAMA", 1)
        df_b = leer_datos_con_respaldo("BDD", 0)
        df_a = leer_datos_con_respaldo("AUDITAR", 0)
    except Exception as exc:
        st.warning(f"No se pudieron refrescar datos, usando ultimo respaldo disponible: {exc}")
        df_p = st.session_state.get(
            "ultimo_df_PROGRAMA", leer_respaldo_local("ultimo_df_PROGRAMA")
        )
        df_b = st.session_state.get("ultimo_df_BDD", leer_respaldo_local("ultimo_df_BDD"))
        df_a = st.session_state.get(
            "ultimo_df_AUDITAR", leer_respaldo_local("ultimo_df_AUDITAR")
        )

    col_p = {
        "area": encontrar_columna(df_p, ["AREA", "PROCESO"]),
        "pieza": encontrar_columna(df_p, ["PIEZA"]),
        "fecha": encontrar_columna(df_p, ["FECHA"]),
        "total": encontrar_columna(df_p, ["TOTAL"]),
    }
    col_b = {
        "pieza": encontrar_columna(df_b, ["PIEZA"]),
        "subproceso": encontrar_columna(
            df_b, ["SUBPROCESO", "SUB PROCESO", "SUB_PROCESO"], contiene_todos=["SUB", "CESO"]
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
    auditoria_pendiente_global = (
        corte_pendiente is not None
        and any(
            not corte_con_captura_area(
                df_a,
                col_a,
                area,
                fecha_hoy,
                corte_pendiente["nombre"],
            )
            for area in areas_con_programa
        )
    )

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
                df_area_calculo, moldeo_diferidos_pausados = filtrar_subprocesos_exigibles_area(
                    df_area,
                    area_nom,
                    t_dec,
                )
                moldeo_sin_exigibles = moldeo_diferidos_pausados and df_area_calculo.empty
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
                    estado_corte_html = '<div class="mini-pagina">ESPERANDO PRIMERA AUDITORIA</div>'
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
                    if (
                        corte_pendiente
                        and CORTES.index(corte_eval) < CORTES.index(corte_pendiente)
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
                    pct_real_corte = max(0.0, min(aporte_corte, pct_real_proceso - base_corte))
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
                    (pct_real_proceso / ideal_ahora * 100)
                    if ideal_ahora > 0
                    else 100
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
                    estado_texto = "VAMOS BIEN"
                    estado_clase = "estado-verde"
                elif recuperando_atraso:
                    color_cuadro = "#f1c40f"
                    estado_texto = "VAMOS RECUP."
                    estado_clase = "estado-amarillo"
                elif indicador_color >= 70:
                    color_cuadro = "#f1c40f"
                    estado_texto = "EN RIESGO"
                    estado_clase = "estado-amarillo"
                else:
                    color_cuadro = "#E32B13"
                    estado_texto = "VAMOS ATRAS"
                    estado_clase = "estado-rojo"
                if esperando_auditoria:
                    color_cuadro = "#607d8b"
                    estado_texto = "ESPERA AUD."
                    estado_clase = "estado-espera"
                if moldeo_sin_exigibles:
                    color_cuadro = "#607d8b"
                    estado_texto = "DIFERIDO"
                    estado_clase = "estado-espera"

                cierre_turno = (
                    not esperando_auditoria
                    and corte_eval["nombre"] == CORTES[-1]["nombre"]
                    and corte_pendiente == CORTES[-1]
                )
                if cierre_turno:
                    if cumplimiento_acumulado >= 90:
                        color_cuadro = "#2ecc71"
                        estado_texto = "OBJETIVO OK"
                        estado_clase = "estado-verde"
                    elif cumplimiento_acumulado >= 80:
                        color_cuadro = "#f1c40f"
                        estado_texto = "CERCA META"
                        estado_clase = "estado-amarillo"
                    else:
                        color_cuadro = "#E32B13"
                        estado_texto = "NO CUMPLIDO"
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
                    [col_p["pieza"], "__BDD_SUBPROCESO", col_p["total"], col_a["real"], "% REAL"]
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
                        (pd.to_numeric(resumen["% REAL"], errors="coerce").fillna(0) - base_corte)
                        .clip(lower=0, upper=aporte_corte)
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
                        p_pct = pd.to_numeric(pd.Series([r["% REAL"]]), errors="coerce").fillna(0).iloc[0]

                        # Color individual basado en la misma regla del 80% del ritmo
                        if usar_ultima_auditoria_para_color:
                            p_prop = p_pct / meta_auditoria_vigente * 100
                        else:
                            p_avance_corte = max(0.0, min(aporte_corte, p_pct - base_corte))
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
                        f'</div>'
                    )
                clase_track = "mini-track mini-track-unica" if total_paginas == 1 else "mini-track"
                shift_vh = -12 * total_paginas
                duracion = total_paginas * 8
                animacion = (
                    "animation:none;"
                    if total_paginas == 1
                    else f"animation:miniTrack {duracion}s steps({total_paginas}) infinite;"
                )
                mini_tabla_html = (
                    "\n"
                    f'<div class="{clase_track}" style="--pages:{total_paginas}; --shift:{shift_vh}vh; {animacion}">'
                    f'{"".join(paginas)}'
                    '</div>'
                )
                pagina_html = (
                    f'\n<div class="mini-pagina">{len(resumen)} actividades - rota cada 8s</div>'
                    if total_paginas > 1
                    else ""
                )

                # --- ÚLTIMO PARO ---
                paro_html = ""
                if col_a and col_a.get("area") and col_a.get("fecha") and col_a.get("notas"):
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
                        & ~notas_paro.str.contains(r"\[SIN PARO\]", case=False, na=False)
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
                        'PROCESOS DIFERIDOS POR FUSION: se evaluan desde 15:00'
                        '</div>'
                    )
                nota_moldeo_html = (
                    '<div class="nota-moldeo-diferido">Vaciado/Desmoldeo desde 15:00</div>'
                    if moldeo_diferidos_pausados
                    else ""
                )

                estado_corte_html = "\n" + estado_corte_html
                paro_html = "\n" + paro_html

                st.markdown(
                    f"""<div class="area-card" style="border-color: {color_cuadro};">
{nota_moldeo_html}
<div class="estado-badge {estado_clase}">{estado_texto}</div>
<div class="label-area">{area_nom} <span style="font-size:0.8vw; color:#444;">({b_nom})</span></div>
<div class="val-pct" style="color: {color_cuadro};">{pct_real_proceso:.1f}% <span style="font-size:2vmin;">{flecha}</span></div>
<div>
<div class="label-meta"><span>DEBERIAMOS LLEVAR: {ideal_ahora:.1f}%</span><span>{esp_pzs} PZS</span></div>
<div class="bar-container"><div class="bar-fill-ideal" style="width: {ideal_ahora}%;"></div></div>
<div class="label-meta"><span>LLEVAMOS: {pct_real_proceso:.1f}%</span><span>RITMO AUDITADO: {ritmo_mostrado:.0f}%</span></div>
<div class="bar-container"><div class="bar-fill-real" style="width: {pct_real_proceso}%; background-color: {color_cuadro};"></div></div>
</div>
<div class="mini-tabla-wrap">
{mini_tabla_html}
</div>
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
