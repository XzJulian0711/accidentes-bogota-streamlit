"""
=================================================================
🚗 ACCIDENTES DE TRANSPORTE EN BOGOTÁ — Análisis 2015-2025
=================================================================
Aplicación interactiva para explorar patrones, hallazgos e insights
sobre los accidentes de transporte reportados en Bogotá durante
el periodo 2015-2025.

Autor: [Tu nombre]
Curso: Herramientas y Visualización de Datos
=================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
    
    # Re-establecer orden categórico (se pierde al guardar en CSV)
    orden_meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                   'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    orden_dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    
    df['mes'] = pd.Categorical(df['mes'], categories=orden_meses, ordered=True)
    df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=orden_dias, ordered=True)
    
    return df


df = cargar_datos()


# =============================================================
# ENCABEZADO DE LA APLICACIÓN
# =============================================================
st.title("🚗 Accidentes de Transporte en Bogotá")
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

# Filtro de localidades (multiselect)
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

# Aplicar filtros al dataframe
df_filtrado = df[
    (df['anio'] >= anio_inicio) &
    (df['anio'] <= anio_fin) &
    (df['tipo_accidente'].isin(tipos_seleccionados)) &
    (df['sexo'].isin(sexos_seleccionados))
]

# Filtro de localidad (manejo especial para incluir "Sin localidad específica")
df_filtrado = df_filtrado[
    (df_filtrado['localidad'].isin(localidades_seleccionadas)) |
    (df_filtrado['localidad'] == 'Sin localidad específica')
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Registros filtrados:** {len(df_filtrado):,}")


# =============================================================
# KPIs PRINCIPALES — RESUMEN EJECUTIVO
# =============================================================
st.subheader(" Resumen del periodo seleccionado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de accidentes",
        value=f"{len(df_filtrado):,}"
    )

with col2:
    if len(df_filtrado) > 0:
        anio_pico = df_filtrado['anio'].value_counts().idxmax()
        casos_pico = df_filtrado['anio'].value_counts().max()
        st.metric(
            label="Año pico",
            value=str(anio_pico),
            delta=f"{casos_pico:,} casos"
        )

with col3:
    if len(df_filtrado) > 0:
        loc_top = df_filtrado[df_filtrado['localidad'] != 'Sin localidad específica']['localidad'].value_counts()
        if len(loc_top) > 0:
            st.metric(
                label="Localidad crítica",
                value=loc_top.idxmax(),
                delta=f"{loc_top.max():,} casos"
            )

with col4:
    if len(df_filtrado) > 0:
        tipo_top = df_filtrado['tipo_accidente'].value_counts().idxmax()
        st.metric(
            label="Tipo predominante",
            value=tipo_top
        )

st.markdown("---")


# =============================================================
# INSIGHT 1 — EVOLUCIÓN TEMPORAL
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

# Línea vertical de pandemia
fig1.add_vline(
    x=2020,
    line_dash="dash",
    line_color="#C73E1D",
    annotation_text="Inicio pandemia",
    annotation_position="top"
)

fig1.update_layout(
    hovermode="x unified",
    plot_bgcolor="white",
    yaxis=dict(gridcolor="#e5e5e5"),
    xaxis=dict(gridcolor="#e5e5e5")
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **Lectura:** En 2020 los accidentes cayeron drásticamente por las restricciones "
    "de movilidad durante la pandemia. Sin embargo, desde 2022 la tendencia se recuperó "
    "y en 2024 superó los niveles pre-pandemia, alcanzando el pico histórico del periodo."
)

st.markdown("---")


# =============================================================
# INSIGHT 2 — LOCALIDADES MÁS AFECTADAS
# =============================================================
st.subheader(" Insight 2: Kennedy, Engativá y Suba concentran la mayoría de los accidentes localizados")

df_localidad = df_filtrado[df_filtrado['localidad'] != 'Sin localidad específica']
localidad_counts = df_localidad['localidad'].value_counts().reset_index()
localidad_counts.columns = ['localidad', 'total']

fig2 = px.bar(
    localidad_counts,
    x='total',
    y='localidad',
    orientation='h',
    title="Accidentes por localidad (orden descendente)",
    labels={'total': 'Número de accidentes', 'localidad': 'Localidad'},
    color='total',
    color_continuous_scale='YlOrRd'
)

fig2.update_layout(
    yaxis=dict(categoryorder='total ascending'),
    plot_bgcolor="white",
    coloraxis_showscale=False,
    height=600
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **Lectura:** Tres localidades concentran una proporción desproporcionada de "
    "los accidentes con ubicación específica. Estas son también zonas con alta densidad "
    "vehicular y poblacional, pero la concentración sugiere la necesidad de focalizar "
    "políticas de seguridad vial en estas áreas."
)

st.markdown("---")


# =============================================================
# INSIGHT 3 — TIPOS DE ACCIDENTE
# =============================================================
st.subheader("Insight 3: Choque y atropello representan casi el 90% de los accidentes")

tipo_counts = df_filtrado['tipo_accidente'].value_counts().reset_index()
tipo_counts.columns = ['tipo', 'total']

# Agrupar tipos muy pequeños en "Otros"
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
    hole=0.4  # donut chart
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
# INSIGHT 4 — PERFIL DEMOGRÁFICO
# =============================================================
st.subheader(" Insight 4: Hombres son la mayoría, concentrados en edad adulta (29–59)")

col_a, col_b = st.columns(2)

with col_a:
    sexo_counts = df_filtrado['sexo'].value_counts().reset_index()
    sexo_counts.columns = ['sexo', 'total']
    
    fig4a = px.pie(
        sexo_counts,
        values='total',
        names='sexo',
        title="Distribución por sexo",
        color_discrete_sequence=['#3498db', '#e91e63'],
        hole=0.5
    )
    fig4a.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig4a, use_container_width=True)

with col_b:
    orden_ciclo = ['(0 a 5) Primera Infancia', '(6 a 11) Infancia', '(12 a 17) Adolescencia',
                   '(18 a 28) Juventud', '(29 a 59) Adultez', '(60 y más) Persona Mayor']
    
    df_ciclo = df_filtrado[df_filtrado['ciclo_vital'].isin(orden_ciclo)].copy()
    ciclo_counts = df_ciclo['ciclo_vital'].value_counts().reindex(orden_ciclo).reset_index()
    ciclo_counts.columns = ['ciclo', 'total']
    
    fig4b = px.bar(
        ciclo_counts,
        x='ciclo',
        y='total',
        title="Víctimas por ciclo vital",
        labels={'ciclo': 'Grupo etario', 'total': 'Número de víctimas'},
        color='total',
        color_continuous_scale='Purples'
    )
    fig4b.update_layout(
        plot_bgcolor="white",
        coloraxis_showscale=False,
        xaxis_tickangle=-30
    )
    st.plotly_chart(fig4b, use_container_width=True)

st.info(
    "💡 **Lectura:** Existe una marcada asimetría de género (~70% hombres) y una clara "
    "concentración en la población económicamente activa (29–59 años). Esto revela "
    "patrones de exposición al riesgo relacionados con movilidad laboral."
)

st.markdown("---")


# =============================================================
# INSIGHT 5 — CAUSAS PRINCIPALES
# =============================================================
st.subheader(" Insight 5: La desobediencia de señales es la principal causa identificada")

df_causas = df_filtrado[df_filtrado['circunstancia'] != 'Sin información'].copy()
causa_counts = df_causas['circunstancia'].value_counts().head(8).reset_index()
causa_counts.columns = ['causa', 'total']

fig5 = px.bar(
    causa_counts,
    x='total',
    y='causa',
    orientation='h',
    title="Top 8 causas identificadas (excluyendo 'Sin información')",
    labels={'total': 'Número de casos', 'causa': 'Causa'},
    color='total',
    color_continuous_scale='Reds'
)

fig5.update_layout(
    yaxis=dict(categoryorder='total ascending'),
    plot_bgcolor="white",
    coloraxis_showscale=False,
    height=500
)

st.plotly_chart(fig5, use_container_width=True)

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
with st.expander(" Ver datos crudos filtrados"):
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