"""Análisis reproducible de casos positivos de COVID-19 en Boyacá.

Ejecutar desde la raíz del repositorio:
    python modulo-01/proyectos/demo-covid/analisis.py

El CSV se conserva en su ubicación original y no se copia a ``docs``.
"""

from html import escape
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pandas as pd
import plotly.graph_objects as go


ROOT = Path(__file__).resolve().parents[3]
RUTA_CSV = ROOT / "modulo-01" / "Proyectos" / "Casos_positivos_de_COVID-19_en_Colombia._20261031.csv"
RUTA_TABLERO = ROOT / "docs" / "proyectos" / "demo-covid"
RUTA_GRAFICOS = RUTA_TABLERO / "graficos"
DEPARTAMENTO = "BOYACA"
FUENTE_URL = "https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia-/gt2j-8ykr/about_data"
COLUMNAS_REQUERIDAS = {
    "ID de caso",
    "Fecha de notificación",
    "Nombre departamento",
    "Ubicación del caso",
}


def cargar_datos() -> pd.DataFrame:
    """Carga el CSV y valida las columnas necesarias para este análisis."""
    if not RUTA_CSV.exists():
        raise FileNotFoundError(f"No se encontró el CSV: {RUTA_CSV}")

    datos = pd.read_csv(RUTA_CSV, low_memory=False)
    faltantes = COLUMNAS_REQUERIDAS - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")
    return datos


def preparar_datos(datos: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Limpia fechas y texto, filtra Boyacá y devuelve limitaciones detectadas."""
    limitaciones = []
    datos = datos.copy()
    datos["fecha_notificacion"] = pd.to_datetime(
        datos["Fecha de notificación"], errors="coerce"
    )
    datos["departamento_normalizado"] = (
        datos["Nombre departamento"].astype("string").str.strip().str.upper()
    )
    datos["id_caso_normalizado"] = datos["ID de caso"].astype("string").str.strip()
    datos["ubicacion_normalizada"] = (
        datos["Ubicación del caso"]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.casefold()
        .str.capitalize()
    )

    fechas_invalidas = int(datos["fecha_notificacion"].isna().sum())
    ids_vacios = int(datos["id_caso_normalizado"].isin(["", "<NA>"]).sum())
    duplicados_id = int(datos["id_caso_normalizado"].duplicated().sum())
    duplicados_fila = int(datos.duplicated().sum())

    if fechas_invalidas:
        limitaciones.append(f"Se excluyeron {fechas_invalidas:,} filas con fecha de notificación inválida.")
    if ids_vacios:
        limitaciones.append(f"Se excluyeron {ids_vacios:,} filas sin ID de caso.")
    if duplicados_id:
        limitaciones.append(
            f"Se detectaron {duplicados_id:,} IDs de caso repetidos; el conteo mensual usa IDs únicos."
        )
    if duplicados_fila:
        limitaciones.append(f"Se detectaron {duplicados_fila:,} filas completas duplicadas.")

    filtrados = datos[
        (datos["departamento_normalizado"] == DEPARTAMENTO)
        & datos["fecha_notificacion"].notna()
        & ~datos["id_caso_normalizado"].isin(["", "<NA>"])
    ].copy()
    if filtrados.empty:
        raise ValueError(f"No hay registros válidos para el departamento {DEPARTAMENTO}.")

    if datos["departamento_normalizado"].nunique(dropna=True) == 1:
        limitaciones.append("El CSV local contiene un solo departamento; no permite comparar departamentos.")
    limitaciones.append(
        "El conteo usa Fecha de notificación e IDs de caso únicos; no representa necesariamente la fecha de contagio."
    )
    limitaciones.append(
        "La fuente puede actualizar, corregir o complementar los registros después de la descarga."
    )
    return filtrados, limitaciones


def calcular_resultados(datos: pd.DataFrame) -> Tuple[pd.Series, pd.Series, Dict[str, Union[str, int]]]:
    """Calcula la serie mensual y la distribución agregada por ubicación."""
    datos["mes"] = datos["fecha_notificacion"].dt.to_period("M")
    mensual = datos.groupby("mes")["id_caso_normalizado"].nunique().sort_index()
    rango_meses = pd.period_range(mensual.index.min(), mensual.index.max(), freq="M")
    mensual = mensual.reindex(rango_meses, fill_value=0)

    ubicacion = (
        datos.groupby("ubicacion_normalizada")["id_caso_normalizado"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )
    mes_pico = mensual.idxmax()
    indicadores = {
        "casos_unicos": int(datos["id_caso_normalizado"].nunique()),
        "mes_pico": str(mes_pico),
        "casos_mes_pico": int(mensual.max()),
    }
    return mensual, ubicacion, indicadores


def generar_graficos(mensual: pd.Series, ubicacion: pd.Series) -> Tuple[str, str]:
    """Construye gráficos Plotly interactivos y devuelve sus fragmentos HTML."""
    meses = mensual.index.astype(str).tolist()
    figura_mensual = go.Figure(
        go.Scatter(
            x=meses,
            y=mensual.values,
            mode="lines+markers",
            name="Casos únicos",
            hovertemplate="Mes: %{x}<br>Casos únicos: %{y:,}<extra></extra>",
            line={"color": "#264653", "width": 2},
        )
    )
    figura_mensual.update_layout(
        title="Casos positivos notificados por mes — Boyacá",
        xaxis_title="Mes de notificación",
        yaxis_title="Casos únicos",
        hovermode="x unified",
        template="plotly_white",
    )

    figura_ubicacion = go.Figure(
        go.Bar(
            x=ubicacion.values[::-1],
            y=ubicacion.index[::-1],
            orientation="h",
            name="Casos únicos",
            marker_color="#2a9d8f",
            hovertemplate="Ubicación: %{y}<br>Casos únicos: %{x:,}<extra></extra>",
        )
    )
    figura_ubicacion.update_layout(
        title="Casos únicos por ubicación del caso",
        xaxis_title="Casos únicos",
        yaxis_title="Ubicación del caso",
        template="plotly_white",
    )

    config = {"displaylogo": False, "responsive": True}
    mensual_html = figura_mensual.to_html(
        full_html=False, include_plotlyjs="cdn", config=config, div_id="grafico-mensual"
    )
    ubicacion_html = figura_ubicacion.to_html(
        full_html=False, include_plotlyjs=False, config=config, div_id="grafico-ubicacion"
    )
    return mensual_html, ubicacion_html


def construir_html(
    mensual: pd.Series,
    indicadores: Dict[str, Union[str, int]],
    limitaciones: List[str],
    graficos_html: Tuple[str, str],
) -> None:
    periodo_inicio = mensual.index.min().strftime("%B de %Y")
    periodo_fin = mensual.index.max().strftime("%B de %Y")
    hallazgo = (
        f"El mayor número mensual de casos únicos ocurrió en {indicadores['mes_pico']}, "
        f"con {indicadores['casos_mes_pico']:,} casos notificados."
    )
    limitaciones_html = "\n".join(f"<li>{escape(item)}</li>" for item in limitaciones)
    grafico_mensual_html, grafico_ubicacion_html = graficos_html
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>COVID-19 en Boyacá</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 0 auto; padding: 2rem; color: #24313a; background: #f6f8f9; }}
    header, section {{ background: white; padding: 1.4rem; margin-bottom: 1.2rem; border-radius: 12px; box-shadow: 0 2px 12px #20304012; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; }}
    .card {{ background: #e9f5f2; padding: 1rem; border-radius: 10px; }}
    .value {{ display: block; font-size: 1.7rem; font-weight: 700; margin-top: .35rem; }}
    .grafico {{ width: 100%; min-height: 430px; margin: 1rem 0 2rem; }}
    code {{ background: #eef1f3; padding: .15rem .3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Casos positivos de COVID-19 en Colombia</h1>
    <p><strong>Pregunta:</strong> ¿Cómo evolucionaron mes a mes los casos reportados durante el periodo seleccionado?</p>
    <p><strong>Departamento filtrado:</strong> Boyacá</p>
    <p><strong>Periodo:</strong> {escape(periodo_inicio)} — {escape(periodo_fin)}</p>
    <p><strong>Fecha usada:</strong> <code>Fecha de notificación</code>. El conteo corresponde a IDs de caso únicos.</p>
  </header>
  <section>
    <h2>Indicadores</h2>
    <div class="cards">
      <div class="card">Casos notificados únicos<span class="value">{indicadores['casos_unicos']:,}</span></div>
      <div class="card">Mes con más casos<span class="value">{escape(indicadores['mes_pico'])}</span><small>{indicadores['casos_mes_pico']:,} casos</small></div>
    </div>
  </section>
  <section>
    <h2>Gráficos</h2>
    <h3>Evolución mensual</h3>
    <div class="grafico">{grafico_mensual_html}</div>
    <h3>Ubicación del caso</h3>
    <div class="grafico">{grafico_ubicacion_html}</div>
  </section>
  <section>
    <h2>Hallazgo</h2>
    <p>{escape(hallazgo)}</p>
  </section>
  <section>
    <h2>Fuente</h2>
    <p><a href="{FUENTE_URL}">Portal Nacional de Datos Abiertos — Casos positivos de COVID-19 en Colombia</a>, Instituto Nacional de Salud.</p>
    <p>Archivo analizado: <code>{escape(str(RUTA_CSV.relative_to(ROOT)))}</code></p>
  </section>
  <section>
    <h2>Limitaciones</h2>
    <ul>{limitaciones_html}</ul>
  </section>
</body>
</html>
"""
    RUTA_TABLERO.mkdir(parents=True, exist_ok=True)
    (RUTA_TABLERO / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    datos, limitaciones = preparar_datos(cargar_datos())
    mensual, ubicacion, indicadores = calcular_resultados(datos)
    graficos_html = generar_graficos(mensual, ubicacion)
    construir_html(mensual, indicadores, limitaciones, graficos_html)
    print(f"Departamento: Boyacá ({DEPARTAMENTO})")
    print(f"Periodo: {mensual.index.min()} a {mensual.index.max()}")
    print(f"Casos únicos: {indicadores['casos_unicos']:,}")
    print(f"Mes pico: {indicadores['mes_pico']} ({indicadores['casos_mes_pico']:,} casos)")
    print(f"Tablero generado: {RUTA_TABLERO / 'index.html'}")


if __name__ == "__main__":
    main()