# 🚗 Accidentes de Transporte en Bogotá — App Streamlit

Aplicación web interactiva para explorar y visualizar los patrones, hallazgos e insights de los accidentes de transporte reportados en Bogotá durante el periodo **2015-2025**. Forma parte del Proyecto 2 del curso **Herramientas y Visualización de Datos** de la Fundación Universitaria Los Libertadores.

## 🌐 App desplegada

👉 **[Ver aplicación en vivo](https://accidentes-bogota.streamlit.app)**

## 📊 Descripción

Esta aplicación permite al usuario filtrar interactivamente por rango de años, localidad, tipo de accidente y sexo de la víctima, para descubrir patrones temporales, geográficos, demográficos y causales de los siniestros viales en Bogotá. Incluye 5 visualizaciones principales diseñadas aplicando los principios de diseño visual de las unidades 1, 2 y 3 del curso.

## 📁 Dataset

- **Fuente:** Datos Abiertos Bogotá — Secretaría Distrital de Gobierno
- **URL original:** [datosabiertos.bogota.gov.co](https://datosabiertos.bogota.gov.co/)
- **Descripción:** Registros de accidentes de transporte ocurridos en Bogotá entre 2015 y 2025, con información sobre ubicación (localidad), variables temporales (año, mes, día, hora), tipo de accidente, medio de transporte, causas, y perfil de la víctima (sexo, ciclo vital).
- **Dimensiones:** 12,386 registros × 19 variables originales (14 tras limpieza)
- **Preprocesamiento aplicado:** renombrado de columnas, reemplazo de "Bogotá" por "Sin localidad específica" en la columna localidad, conversión de meses y días a variables categóricas ordenadas, creación de columna `tipo_dia` (entre semana / fin de semana), eliminación de columnas irrelevantes para el análisis.

## 🔍 Hallazgos principales

1. **La pandemia marcó una caída histórica, pero el rebote ha sido explosivo.** En 2020 los accidentes cayeron a 808 casos (~25% por debajo del promedio). Desde 2022 la tendencia superó los niveles pre-pandemia y 2024 registró el pico histórico con 1,330 casos.

2. **Kennedy, Engativá y Suba concentran la mayoría de accidentes con localidad específica.** Estas tres localidades reúnen más del 40% de los casos localizados, lo que sugiere priorizar políticas focalizadas de seguridad vial.

3. **Choque y atropello dominan el panorama.** Estos dos tipos representan aproximadamente el 86% de todos los accidentes, indicando que la prevención debe centrarse en estas dos dinámicas específicas.

4. **Hombres adultos son el perfil de víctima predominante.** Aproximadamente el 70% de las víctimas son hombres, y el grupo etario de 29-59 años (adultez) concentra la mayor parte de casos, revelando patrones de exposición vinculados a la movilidad laboral.

5. **La desobediencia de señales es la principal causa identificable.** Entre los casos con causa registrada, desobedecer señales de tránsito lidera (~2,300 casos), seguido de exceso de velocidad (~1,260 casos). Ambas son causas prevenibles ligadas al comportamiento del conductor.

## 📈 Visualizaciones implementadas

1. **Evolución temporal (gráfico de área)** — Muestra la tendencia anual de accidentes con línea vertical marcando el inicio de la pandemia. Cubre el tipo "evolución temporal".

2. **Barras horizontales por localidad (paleta secuencial)** — Compara las 19 localidades con codificación de color por intensidad. Cubre "comparaciones entre categorías".

3. **Gráfico de dona de tipos de accidente (paleta cualitativa)** — Muestra la proporción de cada tipo con agrupación inteligente de categorías menores en "Otros". Cubre "composición o proporciones".

4. **Perfil demográfico (dos paneles combinados)** — Dona de sexo y barras verticales de ciclo vital con paleta secuencial. Cubre "distribución de variables".

5. **Top causas (barras horizontales)** — Ranking de las 8 causas más frecuentes con codificación secuencial. Cubre "relaciones entre variables" (causa × frecuencia).

Adicionalmente se incluyen **4 KPIs ejecutivos** (total de accidentes, año pico, localidad crítica, tipo predominante) y una **tabla expandible** con los datos crudos filtrados.

## 🛠️ Tecnologías utilizadas

- **Framework:** Streamlit 1.x
- **Lenguaje:** Python 3.13
- **Bibliotecas principales:**
  - `pandas` — manipulación y análisis de datos
  - `plotly` — gráficos interactivos
  - `numpy` — operaciones numéricas
- **Control de versiones:** Git + GitHub
- **Plataforma de despliegue:** Streamlit Community Cloud

## 💻 Instalación y ejecución local

### Requisitos previos
- Python 3.10 o superior
- Git

### Instrucciones

```bash
# 1. Clonar el repositorio
git clone https://github.com/[XzJulian0711]/accidentes-bogota-streamlit.git
cd accidentes-bogota-streamlit

# 2. Crear un entorno virtual
python -m venv venv

# 3. Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

## 📂 Estructura del proyecto
accidentes-bogota-streamlit/
├── app.py                              # Aplicación Streamlit principal
├── requirements.txt                    # Dependencias del proyecto
├── README.md                           # Este archivo
├── .gitignore                          # Archivos a ignorar por Git
└── data/
└── accidentes_bogota_limpio.csv    # Dataset procesado

## 🎨 Principios de diseño aplicados

- **Unidad 1 (Fundamentos):** elección del tipo de gráfico correcto según la naturaleza de los datos (barras para categóricas, área para temporales, dona para composición).
- **Unidad 2 (Color):** uso de paletas secuenciales para variables ordenadas (intensidad de accidentes), paletas cualitativas para categorías sin orden (tipos de accidente), y contraste adecuado para accesibilidad.
- **Unidad 3 (Diseño):** alto data-ink ratio (fondos limpios, sin decoraciones innecesarias), jerarquía visual clara (títulos descriptivos con el hallazgo, subtítulos y cuerpos), espaciado consistente.

## 🚀 Despliegue

**URL en producción:** [https://accidentes-bogota.streamlit.app](https://accidentes-bogota.streamlit.app)

Desplegado en Streamlit Community Cloud con conexión automática al repositorio de GitHub. Cada push a la rama `main` actualiza la aplicación desplegada.

## 👥 Autores

- **[Julian Camilo Cardenas Torres]** — [GitHub: @XzJulian0711](https://github.com/XzJulian0711)
- **[Juan Fernando Bueno Torres]** — [GitHub: @JuanFer2004](https://github.com/JuanFer2004)

## 📄 Licencia

Este proyecto es de carácter académico, desarrollado para la **Fundación Universitaria Los Libertadores** como parte del curso de Herramientas y Visualización de Datos.

---

<div align="center">
  <sub>Proyecto 2 · Abril 2026</sub>
</div>