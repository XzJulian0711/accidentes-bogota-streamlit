

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json                      
from topojson import Topology 

# =============================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# =============================================================
st.set_page_config(
    page_title="Accidentes de Transporte - Bogotá",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================
# CARGA DE DATOS (con caché para velocidad)
# =============================================================
@st.cache_data
def cargar_datos():
    """Carga el dataset limpio y ajusta tipos ordenados."""
    df = pd.read_csv("data/accidentes_bogota_limpio.csv")
    
    orden_meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                   'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    orden_dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    
    df['mes'] = pd.Categorical(df['mes'], categories=orden_meses, ordered=True)
    df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=orden_dias, ordered=True)
    
    return df


df = cargar_datos()

@st.cache_data
def cargar_geojson():
    """Carga el TopoJSON de Bogotá y lo convierte a GeoJSON."""
    with open('data/bogota_localidades.json', 'r', encoding='utf-8') as f:
        topo_data = json.load(f)
    
    # Convertir TopoJSON → GeoJSON usando la librería topojson
    # Extraemos las features directamente
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Mapeo de nombres: TopoJSON → Dataset
    mapping = {
        'ANTONIO NARIÑO': 'Antonio Nariño',
        'BARRIOS UNIDOS': 'Barrios Unidos',
        'BOSA': 'Bosa',
        'CANDELARIA': 'La Candelaria',
        'CHAPINERO': 'Chapinero',
        'CIUDAD BOLIVAR': 'Ciudad Bolívar',
        'ENGATIVA': 'Engativá',
        'FONTIBON': 'Fontibón',
        'KENNEDY': 'Kennedy',
        'LOS MARTIRES': 'Los Mártires',
        'PUENTE ARANDA': 'Puente Aranda',
        'RAFAEL URIBE URIBE': 'Rafael Uribe Uribe',
        'SAN CRISTOBAL': 'San Cristóbal',
        'SANTA FE': 'Santa Fe',
        'SUBA': 'Suba',
        'SUMAPAZ': 'Sumapaz',
        'TEUSAQUILLO': 'Teusaquillo',
        'TUNJUELITO': 'Tunjuelito',
        'USAQUEN': 'Usaquén',
        'USME': 'Usme'
    }
    
    # Convertir TopoJSON a GeoJSON manualmente
    import topojson as tp
    topo = tp.Topology(data=topo_data, object_name='bta_localidades')
    geojson_str = topo.to_geojson()
    geojson = json.loads(geojson_str)
    
    # Aplicar el mapeo de nombres
    for feature in geojson['features']:
        nombre_original = feature['properties'].get('NOMBRE', '')
        feature['properties']['localidad'] = mapping.get(nombre_original, nombre_original)
    
    return geojson




# =============================================================
# ENCABEZADO DE LA APLICACIÓN
# =============================================================
st.title(" Accidentes de Transporte en Bogotá")
st.markdown(
    "**Análisis interactivo 2015–2025** | "
    "Fuente: Datos Abiertos de Bogotá"
)
st.markdown("---")


# =============================================================
# BARRA LATERAL — FILTROS INTERACTIVOS
# =============================================================
st.sidebar.header(" Filtros")
st.sidebar.markdown("Ajusta los filtros para explorar los datos:")

# Filtro de años
anios_disponibles = sorted(df['anio'].unique())
anio_inicio, anio_fin = st.sidebar.select_slider(
    "Rango de años",
    options=anios_disponibles,
    value=(anios_disponibles[0], anios_disponibles[-1])
)

# Filtro de localidades
localidades = sorted(df[df['localidad'] != 'Sin localidad específica']['localidad'].unique())
localidades_seleccionadas = st.sidebar.multiselect(
    "Localidades",
    options=localidades,
    default=localidades,
    help="Selecciona una o más localidades"
)

# Filtro de tipo de accidente
tipos_accidente = sorted(df['tipo_accidente'].unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de accidente",
    options=tipos_accidente,
    default=tipos_accidente
)

# Filtro de sexo
sexos = sorted(df['sexo'].unique())
sexos_seleccionados = st.sidebar.multiselect(
    "Sexo de la víctima",
    options=sexos,
    default=sexos
)

# Aplicar filtros
df_filtrado = df[
    (df['anio'] >= anio_inicio) &
    (df['anio'] <= anio_fin) &
    (df['tipo_accidente'].isin(tipos_seleccionados)) &
    (df['sexo'].isin(sexos_seleccionados))
]

df_filtrado = df_filtrado[
    (df_filtrado['localidad'].isin(localidades_seleccionadas)) |
    (df_filtrado['localidad'] == 'Sin localidad específica')
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Registros filtrados:** {len(df_filtrado):,}")


# =============================================================
# KPIs PRINCIPALES — RESUMEN EJECUTIVO
# =============================================================
st.subheader("Resumen del periodo seleccionado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total de accidentes", value=f"{len(df_filtrado):,}")

with col2:
    if len(df_filtrado) > 0:
        anio_pico = df_filtrado['anio'].value_counts().idxmax()
        casos_pico = df_filtrado['anio'].value_counts().max()
        st.metric(label="Año pico", value=str(anio_pico), delta=f"{casos_pico:,} casos")

with col3:
    if len(df_filtrado) > 0:
        loc_top = df_filtrado[df_filtrado['localidad'] != 'Sin localidad específica']['localidad'].value_counts()
        if len(loc_top) > 0:
            st.metric(label="Localidad crítica", value=loc_top.idxmax(), delta=f"{loc_top.max():,} casos")

with col4:
    if len(df_filtrado) > 0:
        tipo_top = df_filtrado['tipo_accidente'].value_counts().idxmax()
        st.metric(label="Tipo predominante", value=tipo_top)

st.markdown("---")


# =============================================================
# INSIGHT 1 — EVOLUCIÓN TEMPORAL (área)
# =============================================================
st.subheader(" Insight 1: La pandemia marcó una caída histórica, pero el rebote ha sido explosivo")

accidentes_anio = df_filtrado.groupby('anio').size().reset_index(name='total')

fig1 = px.area(
    accidentes_anio,
    x='anio',
    y='total',
    title="Evolución anual de accidentes (2015–2025)",
    labels={'anio': 'Año', 'total': 'Número de accidentes'},
    color_discrete_sequence=['#2E86AB']
)

fig1.add_vline(
    x=2020, line_dash="dash", line_color="#C73E1D",
    annotation_text="Inicio pandemia", annotation_position="top"
)

fig1.update_layout(
    hovermode="x unified",
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#e5e5e5"),
    xaxis=dict(gridcolor="#e5e5e5")
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    " **Lectura:** En 2020 los accidentes cayeron drásticamente por las restricciones "
    "de movilidad durante la pandemia. Sin embargo, desde 2022 la tendencia se recuperó "
    "y en 2024 superó los niveles pre-pandemia, alcanzando el pico histórico del periodo."
)

st.markdown("---")

# =============================================================
# INSIGHT 2 — MAPA COROPLÉTICO DE BOGOTÁ 
# =============================================================
st.subheader(" Insight 2: Kennedy, Engativá y Suba concentran los accidentes en el sur-occidente de Bogotá")

# Cargar GeoJSON
geojson_bogota = cargar_geojson()

# Preparar datos: conteo por localidad
df_loc = df_filtrado[df_filtrado['localidad'] != 'Sin localidad específica'].copy()

if len(df_loc) > 0:
    conteo_loc = df_loc.groupby('localidad').size().reset_index(name='total')
    
    # Crear el mapa coroplético
    fig2 = px.choropleth_mapbox(
        conteo_loc,
        geojson=geojson_bogota,
        locations='localidad',
        featureidkey='properties.localidad',
        color='total',
        color_continuous_scale='YlOrRd',
        mapbox_style='carto-positron',
        zoom=9.5,
        center={"lat": 4.65, "lon": -74.1},
        opacity=0.75,
        labels={'total': 'Accidentes'},
        title="Mapa de calor de accidentes por localidad"
    )
    
    fig2.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=600,
        coloraxis_colorbar=dict(title="Accidentes")
    )
    
    fig2.update_traces(
        hovertemplate='<b>%{location}</b><br>Accidentes: %{z:,}<extra></extra>'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos con localidad específica en el filtro actual.")

st.info(
    " **Lectura:** El mapa revela un patrón geográfico claro: las localidades del "
    "sur-occidente de Bogotá (Kennedy, Bosa, Ciudad Bolívar) y noroccidente (Engativá, Suba) "
    "concentran la mayor cantidad de accidentes. Esto coincide con zonas de alta densidad "
    "poblacional y fuerte actividad vehicular. Localidades rurales como Sumapaz permanecen "
    "en amarillo claro, reflejando su bajo volumen de tráfico."
)

st.markdown("---")

# =============================================================
# INSIGHT 3 — TIPOS DE ACCIDENTE (donut)
# =============================================================

st.subheader("🚗 Insight 3: Choque y atropello representan casi el 90% de los accidentes")

tipo_counts = df_filtrado['tipo_accidente'].value_counts().reset_index()
tipo_counts.columns = ['tipo', 'total']

umbral = tipo_counts['total'].sum() * 0.02
tipo_counts['tipo_agrupado'] = tipo_counts.apply(
    lambda x: x['tipo'] if x['total'] >= umbral else 'Otros', axis=1
)
tipo_final = tipo_counts.groupby('tipo_agrupado')['total'].sum().reset_index()

fig3 = px.pie(
    tipo_final,
    values='total',
    names='tipo_agrupado',
    title="Distribución por tipo de accidente",
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4
)

fig3.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig3, use_container_width=True)

st.info(
    "💡 **Lectura:** Dos categorías dominan el panorama: choques entre vehículos y "
    "atropellos de peatones. Esto indica que las políticas de prevención deben focalizarse "
    "principalmente en estas dos dinámicas de siniestro."
)

st.markdown("---")


# =============================================================
# INSIGHT 4 — PIRÁMIDE POBLACIONAL (sexo + edad)
# =============================================================
st.subheader("🏛️ Insight 4: Hombres adultos (29-59 años) concentran la mayoría de víctimas")

orden_ciclo = [
    '(0 a 5) Primera Infancia',
    '(6 a 11) Infancia',
    '(12 a 17) Adolescencia',
    '(18 a 28) Juventud',
    '(29 a 59) Adultez',
    '(60 y más) Persona Mayor'
]

df_piramide = df_filtrado[df_filtrado['ciclo_vital'].isin(orden_ciclo)].copy()

if len(df_piramide) > 0:
    piramide = df_piramide.groupby(['ciclo_vital', 'sexo']).size().unstack(fill_value=0)
    piramide = piramide.reindex(orden_ciclo).fillna(0)
    
    # Asegurar que existan ambas columnas
    if 'Hombre' not in piramide.columns:
        piramide['Hombre'] = 0
    if 'Mujer' not in piramide.columns:
        piramide['Mujer'] = 0
    
    hombres = -piramide['Hombre'].values  # negativos = izquierda
    mujeres = piramide['Mujer'].values    # positivos = derecha
    
    max_val = max(abs(hombres).max(), mujeres.max())
    tick_step = max(500, int(max_val / 3 / 500) * 500)
    tick_vals = list(range(-int(max_val * 1.1 // tick_step + 1) * tick_step, 
                            int(max_val * 1.1 // tick_step + 1) * tick_step + 1, 
                            tick_step))
    tick_text = [f"{abs(v):,}" for v in tick_vals]
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        y=orden_ciclo,
        x=hombres,
        name='Hombres',
        orientation='h',
        marker_color='#3498db',
        hovertemplate='<b>%{y}</b><br>Hombres: %{customdata:,}<extra></extra>',
        customdata=-hombres
    ))
    
    fig4.add_trace(go.Bar(
        y=orden_ciclo,
        x=mujeres,
        name='Mujeres',
        orientation='h',
        marker_color='#e91e63',
        hovertemplate='<b>%{y}</b><br>Mujeres: %{x:,}<extra></extra>'
    ))
    
    fig4.update_layout(
        title="Pirámide poblacional de víctimas por sexo y grupo etario",
        barmode='relative',
        bargap=0.15,
        plot_bgcolor='white',
        xaxis=dict(
            title='Número de víctimas',
            tickvals=tick_vals,
            ticktext=tick_text,
            gridcolor='#e5e5e5'
        ),
        yaxis=dict(title=''),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        height=500
    )
    
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No hay datos demográficos disponibles con los filtros actuales.")

st.info(
    "💡 **Lectura:** La pirámide poblacional muestra claramente dos patrones: "
    "(1) una fuerte asimetría de género —los hombres representan alrededor del 70% de las víctimas—, "
    "y (2) una concentración muy marcada en la población económicamente activa (29-59 años), "
    "lo que sugiere patrones de exposición vinculados a movilidad laboral."
)

st.markdown("---")


# =============================================================
# INSIGHT 5 — LOLLIPOP CHART DE CAUSAS
# =============================================================
st.subheader("🍭 Insight 5: La desobediencia de señales es la principal causa identificada")

df_causas = df_filtrado[df_filtrado['circunstancia'] != 'Sin información'].copy()

if len(df_causas) > 0:
    causa_counts = df_causas['circunstancia'].value_counts().head(8).reset_index()
    causa_counts.columns = ['causa', 'total']
    causa_counts = causa_counts.sort_values('total', ascending=True)
    
    fig5 = go.Figure()
    
    # Líneas (palitos)
    for i, row in causa_counts.iterrows():
        fig5.add_shape(
            type='line',
            x0=0, x1=row['total'],
            y0=row['causa'], y1=row['causa'],
            line=dict(color='#C73E1D', width=2)
        )
    
    # Círculos (piruletas)
    fig5.add_trace(go.Scatter(
        x=causa_counts['total'],
        y=causa_counts['causa'],
        mode='markers+text',
        marker=dict(
            size=20,
            color=causa_counts['total'],
            colorscale='Reds',
            showscale=False,
            line=dict(color='white', width=2)
        ),
        text=causa_counts['total'].apply(lambda x: f'{x:,}'),
        textposition='middle right',
        textfont=dict(size=11, color='#1a1a1a'),
        hovertemplate='<b>%{y}</b><br>%{x:,} casos<extra></extra>'
    ))
    
    fig5.update_layout(
        title="Top 8 causas identificadas (excluyendo 'Sin información')",
        xaxis=dict(
            title='Número de casos',
            gridcolor='#e5e5e5',
            range=[0, causa_counts['total'].max() * 1.22]
        ),
        yaxis=dict(title=''),
        plot_bgcolor='white',
        showlegend=False,
        height=500,
        margin=dict(l=250)
    )
    
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("No hay causas identificadas con los filtros actuales.")

st.info(
    "💡 **Lectura:** Entre los casos con causa identificada, desobedecer señales de "
    "tránsito lidera con gran diferencia, seguido por exceso de velocidad. Ambas son "
    "causas prevenibles vinculadas directamente al comportamiento de los conductores, "
    "lo que sugiere que campañas educativas y de control podrían tener un impacto sustancial."
)

st.markdown("---")


# =============================================================
# DATOS CRUDOS (expandible)
# =============================================================
with st.expander("📋 Ver datos crudos filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)
    st.markdown(f"Mostrando **{len(df_filtrado):,}** registros")


# =============================================================
# PIE DE PÁGINA
# =============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Proyecto 2 - Herramientas y Visualización de Datos | "
    "Fundación Universitaria Los Libertadores"
    "</div>",
    unsafe_allow_html=True
)