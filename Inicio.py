
import streamlit as st
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="HablaTrazo",
    page_icon="🎨",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS
# --------------------------------------------------

st.markdown("""
<style>

/* Fondo general */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .stApp {
    background: linear-gradient(
        120deg,
        #DDF4E9 0%,
        #E9F5F8 40%,
        #FFF3CE 75%,
        #E3EEFF 100%
    ) !important;
    background-attachment: fixed !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Encabezado principal */
.encabezado-app {
    width: 100%;
    padding: 25px 35px;
    margin-bottom: 28px;
    border-radius: 25px;
    background: linear-gradient(
        110deg,
        #258B65 0%,
        #70C69E 45%,
        #176BFF 100%
    );
    display: flex;
    align-items: center;
    gap: 22px;
    box-shadow: 0 8px 20px rgba(36, 75, 120, 0.15);
}

.encabezado-icono {
    background: #FFEAA9;
    width: 75px;
    height: 75px;
    min-width: 75px;
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
}

.encabezado-app h1 {
    color: white !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.encabezado-app p {
    color: white !important;
    font-size: 1.1rem !important;
    margin: 5px 0 0 0 !important;
}

/* Títulos */
h2, h3 {
    color: #244B78 !important;
    font-weight: 800 !important;
}

p, label, li {
    color: #285E73;
}

/* Tarjetas */
.tarjeta {
    background: rgba(255, 255, 255, 0.75);
    border: 2px solid rgba(255,255,255,0.8);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 15px rgba(36,75,120,0.07);
}

.tarjeta-verde {
    background: #D2F1E1;
}

.tarjeta-amarilla {
    background: #FFF2C5;
}

.tarjeta-azul {
    background: #DCEAFF;
}

/* Botones */
.stButton > button {
    background: #176BFF !important;
    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #258B65 !important;
    color: white !important;
    transform: translateY(-2px);
}

/* Botones de descarga */
.stDownloadButton > button {
    background: #258B65 !important;
    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    font-weight: 700 !important;
}

/* Campos */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #BFEBD5,
        #DCEAFF
    ) !important;
}

/* Separadores */
hr {
    border-color: rgba(36,75,120,0.15);
}

/* Pie de página */
.pie {
    text-align: center;
    color: #527B8C;
    padding: 20px;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# ENCABEZADO
# --------------------------------------------------

st.markdown("""
<div class="encabezado-app">
    <div class="encabezado-icono">🎨</div>
    <div>
        <h1>HablaTrazo</h1>
        <p>Dibujar, imaginar y aprender jugando</p>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------

def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def analyze_drawing(image, client, objective, age):
    image_base64 = image_to_base64(image)

    prompt = f"""
    Eres un asistente de apoyo para terapeutas de lenguaje
    que trabajan con niños.

    Analiza el dibujo realizado por un niño de {age} años.

    Objetivo de la sesión: {objective}

    Organiza tu respuesta de esta manera:

    1. ¿QUÉ OBSERVAMOS?
    Describe de manera sencilla qué parece representar el dibujo.
    No afirmes que sabes exactamente qué quiso dibujar el niño.

    2. PALABRAS PARA APRENDER
    Sugiere entre 4 y 6 palabras relacionadas con el dibujo.
    Incluye palabras variadas y apropiadas para su edad.

    3. PREGUNTAS PARA CONVERSAR
    Propón 4 preguntas abiertas que el terapeuta pueda hacerle
    al niño para estimular la conversación.

    4. ACTIVIDAD SUGERIDA
    Propón una actividad sencilla relacionada con el objetivo
    de la sesión.

    5. CONSTRUCCIÓN DE FRASES
    Ofrece dos ejemplos de frases sencillas que el niño
    podría construir a partir del dibujo.

    6. SIGUIENTE PASO
    Sugiere una idea para continuar la actividad.

    IMPORTANTE:
    - Utiliza un lenguaje claro, amable y positivo.
    - No diagnostiques trastornos.
    - No evalúes el desarrollo del niño a partir del dibujo.
    - No supongas que el dibujo demuestra habilidades
      lingüísticas o cognitivas.
    - Las sugerencias son orientativas y deben ser revisadas
      por el terapeuta.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1200
    )

    return response.choices[0].message.content


def create_story(drawing_description, age, client):
    prompt = f"""
    Crea un cuento infantil breve inspirado en esta descripción:

    {drawing_description}

    El cuento debe estar adaptado para un niño de {age} años.

    Incluye:
    - Un título creativo.
    - Una historia divertida y sencilla.
    - Un personaje principal.
    - Un pequeño problema y su solución.
    - Tres preguntas para conversar sobre la historia.
    - Cinco palabras clave para aprender.

    Utiliza un tono alegre, imaginativo y cercano.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


# --------------------------------------------------
# ESTADO DE LA APLICACIÓN
# --------------------------------------------------

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "full_response" not in st.session_state:
    st.session_state.full_response = ""

if "drawing_bytes" not in st.session_state:
    st.session_state.drawing_bytes = None

if "story" not in st.session_state:
    st.session_state.story = ""


# --------------------------------------------------
# CONFIGURACIÓN LATERAL
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚙️ Configuración")

    st.markdown("### 👧 Edad del niño")

    age = st.selectbox(
        "Selecciona un rango de edad:",
        ["3 a 5 años", "6 a 8 años", "9 a 12 años"]
    )

    st.markdown("---")

    st.markdown("### 🎯 Objetivo de la sesión")

    objective = st.selectbox(
        "¿Qué deseas trabajar?",
        [
            "Ampliar vocabulario",
            "Reconocer y expresar acciones",
            "Describir objetos y características",
            "Construir frases sencillas",
            "Crear historias y narrar situaciones",
            "Relacionar objetos y conceptos"
        ]
    )

    st.markdown("---")

    st.markdown("### 🖍️ Herramientas de dibujo")

    drawing_mode = st.selectbox(
        "Herramienta:",
        ["freedraw", "line", "rect", "circle", "transform"],
        format_func=lambda x: {
            "freedraw": "✏️ Lápiz",
            "line": "📏 Línea",
            "rect": "⬜ Cuadrado / Rectángulo",
            "circle": "⭕ Círculo",
            "transform": "↔️ Mover elementos"
        }[x]
    )

    stroke_color = st.color_picker(
        "Color del lápiz:",
        "#176BFF"
    )

    stroke_width = st.slider(
        "Grosor del trazo:",
        min_value=1,
        max_value=25,
        value=5
    )

    st.markdown("---")

    st.markdown("### 🔑 Conexión con IA")

    api_key = st.text_input(
        "Clave API de OpenAI",
        type="password",
        placeholder="Introduce tu API Key"
    )

    st.caption("La clave se utiliza para realizar el análisis del dibujo.")


# --------------------------------------------------
# ÁREA PRINCIPAL
# --------------------------------------------------

st.markdown("""
<div class="tarjeta tarjeta-verde">
    <h2>¡Es hora de crear! 🌈</h2>
    <p>
        Invita al niño a dibujar libremente. Después podrás
        utilizar su creación para iniciar una actividad de lenguaje.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LIENZO Y HERRAMIENTAS
# --------------------------------------------------

col_lienzo, col_info = st.columns([2.2, 1])

with col_lienzo:

    st.markdown("### 🖌️ Mi espacio de dibujo")

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=420,
        width=650,
        drawing_mode=drawing_mode,
        display_toolbar=False,
        key=f"canvas_{st.session_state.canvas_key}"
    )

    st.caption("Dibuja con libertad. ¡Cada creación cuenta!")

    col_limpiar, col_guardar = st.columns(2)

    with col_limpiar:
        if st.button("🗑️ Limpiar hoja", use_container_width=True):
            st.session_state.canvas_key += 1
            st.session_state.analysis_done = False
            st.session_state.full_response = ""
            st.session_state.drawing_bytes = None
            st.session_state.story = ""
            st.rerun()

    with col_guardar:
        if canvas_result.image_data is not None:
            image_to_save = Image.fromarray(
                canvas_result.image_data.astype("uint8")
            )

            buffer = BytesIO()
            image_to_save.save(buffer, format="PNG")

            st.download_button(
                "⬇️ Guardar dibujo",
                data=buffer.getvalue(),
                file_name="mi_dibujo.png",
                mime="image/png",
                use_container_width=True
            )


with col_info:

    st.markdown("""
    <div class="tarjeta tarjeta-amarilla">
        <h3>💡 ¡Imagina!</h3>
        <p>
            Anima al niño a dibujar aquello que le gusta:
            animales, personas, lugares, objetos o personajes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tarjeta tarjeta-azul">
        <h3>🗣️ Conversa</h3>
        <p>
            Pregúntale qué está dibujando, qué sucede
            y qué otros detalles quiere agregar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tarjeta tarjeta-verde">
        <h3>✨ Aprende</h3>
        <p>
            Utiliza el dibujo como punto de partida
            para explorar nuevas palabras y construir historias.
        </p>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# BOTÓN DE ANÁLISIS
# --------------------------------------------------

st.markdown("---")
st.markdown("### 🤖 Descubramos qué podemos trabajar con este dibujo")

if st.button("✨ Analizar mi dibujo", use_container_width=True):

    if not api_key:
        st.warning("Primero debes introducir tu clave API de OpenAI.")

    elif canvas_result.image_data is None:
        st.warning("Primero realiza un dibujo en el lienzo.")

    else:
        image_array = canvas_result.image_data.astype("uint8")
        image = Image.fromarray(image_array).convert("RGB")

        # Comprobar si el lienzo está vacío
        pixels = np.array(image)
        is_blank = np.all(pixels > 245)

        if is_blank:
            st.warning("El lienzo está vacío. ¡Haz un dibujo primero!")

        else:
            try:
                client = OpenAI(api_key=api_key)

                with st.spinner("🎨 Estamos observando tu dibujo..."):

                    result = analyze_drawing(
                        image,
                        client,
                        objective,
                        age
                    )

                    st.session_state.full_response = result
                    st.session_state.drawing_bytes = image
                    st.session_state.analysis_done = True
                    st.session_state.story = ""

            except Exception as e:
                st.error(f"No se pudo realizar el análisis: {e}")


# --------------------------------------------------
# RESULTADOS DEL ANÁLISIS
# --------------------------------------------------

if st.session_state.analysis_done:

    st.markdown("---")
    st.markdown("## 🌟 ¡Descubramos lo que podemos aprender!")

    st.markdown(
        st.session_state.full_response
    )

    if st.session_state.drawing_bytes is not None:
        st.markdown("### 🖼️ Tu dibujo")

        st.image(
            st.session_state.drawing_bytes,
            use_container_width=True
        )

    st.markdown("---")

    # --------------------------------------------------
    # CREAR HISTORIA
    # --------------------------------------------------

    st.markdown("### 📖 ¡Convirtamos el dibujo en una historia!")

    st.write(
        "Puedes transformar el dibujo en un pequeño cuento "
        "para estimular la imaginación y la narración."
    )

    if st.button("📚 Crear una historia", use_container_width=True):

        try:
            client = OpenAI(api_key=api_key)

            with st.spinner("✨ Inventando una historia..."):

                story = create_story(
                    st.session_state.full_response,
                    age,
                    client
                )

                st.session_state.story = story

        except Exception as e:
            st.error(f"No se pudo crear la historia: {e}")

    if st.session_state.story:
        st.markdown("""
        <div class="tarjeta tarjeta-amarilla">
            <h3>📖 Nuestra historia</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(st.session_state.story)


# --------------------------------------------------
# PIE DE PÁGINA
# --------------------------------------------------

st.markdown("---")

st.markdown("""
<div class="pie">
    🎨 <b>HablaTrazo</b> · Dibujar, imaginar y aprender jugando.
    <br>
    Herramienta complementaria para apoyar actividades de lenguaje.
    Las sugerencias deben ser revisadas por el terapeuta.
</div>
""", unsafe_allow_html=True)
