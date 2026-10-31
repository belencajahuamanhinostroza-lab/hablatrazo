
import base64
from io import BytesIO

import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="HablaTrazo | Tablero inteligente",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# ESTILOS VISUALES: VERDE Y AZUL PASTEL
# ============================================================

st.markdown("""
<style>

/* Fondo general */
.stApp {
    background: linear-gradient(
        135deg,
        #F0FAF6 0%,
        #EDF7FA 48%,
        #E8F3FA 100%
    );
}

/* Contenedor */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Título */
.titulo {
    background: linear-gradient(
        90deg,
        #55A88B,
        #579BC5,
        #7BAED0
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 850;
    margin-bottom: 0;
}

/* Subtítulo */
.subtitulo {
    color: #648B91;
    font-size: 1.05rem;
    margin-top: 5px;
}

/* Tarjetas */
.tarjeta {
    background: linear-gradient(
        145deg,
        #FFFFFF 0%,
        #F0FAF7 55%,
        #EEF7FC 100%
    );
    padding: 22px;
    border-radius: 20px;
    border: 1px solid #DCEFE9;
    box-shadow: 0 5px 18px rgba(91, 151, 143, 0.08);
    margin-bottom: 16px;
    color: #496D70;
}

/* Títulos de tarjetas */
.tarjeta h4 {
    color: #4C927F;
}

/* Texto secundario */
.pequeno {
    color: #789A9D;
    font-size: 0.9rem;
}

/* Botones */
div.stButton > button {
    background: linear-gradient(
        100deg,
        #78C5A6,
        #72B6D0
    );
    color: white;
    border: none;
    border-radius: 13px;
    font-weight: 650;
    min-height: 45px;
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(94, 166, 157, 0.18);
}

/* Efecto hover */
div.stButton > button:hover {
    background: linear-gradient(
        100deg,
        #60B493,
        #5A9FC0
    );
    color: white;
    border: none;
    transform: translateY(-2px);
}

/* Barra lateral */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #E3F4EC 0%,
        #E5F1F8 100%
    );
    border-right: 1px solid #D7EAE5;
}

/* Encabezados */
h1, h2, h3 {
    color: #477F7D;
}

/* Texto general */
p, label {
    color: #587B7D;
}

/* Selectores */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF;
    border-radius: 11px;
    border-color: #D5EAE3;
}

/* Campos de texto */
div[data-baseweb="input"] {
    background-color: #FFFFFF;
    border-radius: 11px;
}

/* Alertas */
div[data-testid="stAlert"] {
    background: linear-gradient(
        100deg,
        #E4F5EC,
        #E5F2FA
    );
    border: 1px solid #CDE8DF;
    border-radius: 14px;
}

/* Separadores */
hr {
    border-color: #D5EAE4;
}

/* Canvas */
canvas {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "full_response" not in st.session_state:
    st.session_state.full_response = ""

if "drawing_bytes" not in st.session_state:
    st.session_state.drawing_bytes = None

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

if "story" not in st.session_state:
    st.session_state.story = ""


# ============================================================
# FUNCIONES
# ============================================================

def image_to_base64(image):
    """Convierte una imagen PIL a Base64."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def analyze_drawing(client, image_base64, age_group, objective):

    prompt = f"""
    Eres un asistente educativo que apoya a terapeutas de lenguaje
    en actividades de estimulación del lenguaje infantil.

    Observa el dibujo realizado por un niño.

    INFORMACIÓN:
    - Grupo de edad aproximado: {age_group}
    - Objetivo terapéutico: {objective}

    Responde en español, de forma clara, amable y organizada.

    ### 1. ¿Qué observamos en el dibujo?
    Describe los elementos que parecen aparecer.
    Si no estás seguro, menciona las posibles interpretaciones.

    ### 2. Palabras para trabajar
    Propón entre 4 y 6 palabras relacionadas con el dibujo.
    Incluye sustantivos, características y acciones cuando corresponda.

    ### 3. Preguntas para conversar
    Propón 4 preguntas abiertas y sencillas que el terapeuta
    pueda hacerle al niño.

    ### 4. Actividad de lenguaje
    Crea una actividad breve relacionada con este objetivo:
    {objective}

    Explica cómo realizarla en pocos pasos.

    ### 5. Construcción de frases
    Propón 2 frases cortas que el niño podría construir
    utilizando los elementos del dibujo.

    ### 6. Idea para continuar
    Sugiere un pequeño reto o pregunta para ampliar el dibujo
    y continuar la conversación.

    REGLAS IMPORTANTES:
    - Adapta la complejidad al grupo de edad.
    - Mantén un tono positivo y cercano.
    - No inventes detalles que no puedas observar.
    - No evalúes la inteligencia ni el desarrollo del niño.
    - No realices diagnósticos.
    - No afirmes que el niño tiene dificultades del lenguaje.
    - No evalúes pronunciación o expresión oral a partir del dibujo.
    - Las sugerencias deben ser revisadas por el terapeuta.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


def create_story(client, description, age_group):

    prompt = f"""
    Crea una historia infantil breve y creativa basada
    en la siguiente interpretación de un dibujo:

    {description}

    Edad aproximada: {age_group}.

    La historia debe:
    - Utilizar palabras sencillas.
    - Tener oraciones cortas.
    - Ser divertida y apropiada para niños.
    - Mantener relación con el dibujo.

    Al final incluye:
    - 3 preguntas sencillas sobre la historia.
    - 3 palabras importantes para aprender.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=600
    )

    return response.choices[0].message.content


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<p class="titulo">🎨 HablaTrazo</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitulo">Dibuja, descubre y conversa. '
    'Un espacio creativo para estimular el lenguaje infantil.</p>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "HablaTrazo transforma los dibujos infantiles en oportunidades "
    "para conversar, aprender palabras y crear historias."
)


# ============================================================
# PANEL LATERAL
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuración")

    st.markdown("### 🎯 Objetivo de la actividad")

    objective = st.selectbox(
        "¿Qué desea trabajar el terapeuta?",
        [
            "Ampliar vocabulario",
            "Reconocer y expresar acciones",
            "Describir objetos y características",
            "Construir frases sencillas",
            "Crear historias y narrar situaciones",
            "Relacionar objetos y conceptos"
        ]
    )

    st.divider()

    st.markdown("### 👧 Grupo de edad")

    age_group = st.selectbox(
        "Selecciona un rango aproximado",
        [
            "3 a 5 años",
            "6 a 8 años",
            "9 a 12 años"
        ]
    )

    st.caption(
        "La edad permite adaptar las actividades. "
        "No representa una evaluación del niño."
    )

    st.divider()

    st.markdown("### ✏️ Herramientas de dibujo")

    tool = st.radio(
        "Selecciona una herramienta",
        ["Lápiz", "Borrador"],
        horizontal=True
    )

    if tool == "Lápiz":

        stroke_color = st.selectbox(
            "Color del lápiz",
            [
                "#222222",
                "#E74C3C",
                "#3498DB",
                "#2ECC71",
                "#9B59B6",
                "#F39C12",
                "#FF69B4",
                "#795548"
            ],
            format_func=lambda color: {
                "#222222": "Negro",
                "#E74C3C": "Rojo",
                "#3498DB": "Azul",
                "#2ECC71": "Verde",
                "#9B59B6": "Morado",
                "#F39C12": "Naranja",
                "#FF69B4": "Rosado",
                "#795548": "Marrón"
            }[color]
        )

    else:
        stroke_color = "#FFFFFF"

    stroke_width = st.slider(
        "Grosor del trazo",
        min_value=2,
        max_value=30,
        value=6
    )

    st.divider()

    st.markdown("### 🔑 Conexión con IA")

    api_key = st.text_input(
        "Clave API de OpenAI",
        type="password",
        placeholder="Ingresa tu API key"
    )

    st.caption(
        "La clave se utiliza para realizar el análisis "
        "con el modelo de inteligencia artificial."
    )

    st.divider()

    st.markdown("### 💡 Acerca de HablaTrazo")

    st.write(
        "Una herramienta de apoyo para que los terapeutas "
        "aprovechen los dibujos infantiles como punto de partida "
        "para actividades de lenguaje."
    )


# ============================================================
# TABLERO DE DIBUJO
# ============================================================

st.markdown("## 🖍️ ¡Vamos a dibujar!")

st.write(
    "Dibuja lo que quieras en el tablero. Puedes crear un animal, "
    "una persona, un objeto, un lugar o una pequeña escena."
)

canvas_col, info_col = st.columns([3, 1])

with canvas_col:

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=420,
        width=650,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.canvas_key}",
        display_toolbar=False
    )

with info_col:

    st.markdown("""
    <div class="tarjeta">
        <h4>🌈 ¿Qué puedes dibujar?</h4>
        <p>🐶 Animales</p>
        <p>🏠 Lugares</p>
        <p>🍎 Alimentos</p>
        <p>👨‍👩‍👧 Personas</p>
        <p>🚗 Objetos</p>
        <p>🌳 Naturaleza</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tarjeta">
        <h4>💡 ¿Cómo funciona?</h4>
        <p>1. Realiza un dibujo.</p>
        <p>2. Presiona analizar.</p>
        <p>3. Descubre qué interpreta la IA.</p>
        <p>4. Utiliza las actividades para conversar.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# BOTONES DEL TABLERO
# ============================================================

button_col1, button_col2 = st.columns(2)

with button_col1:

    analyze_button = st.button(
        "✨ Analizar dibujo",
        type="primary",
        use_container_width=True
    )

with button_col2:

    clear_button = st.button(
        "🧹 Limpiar tablero",
        use_container_width=True
    )


# ============================================================
# LIMPIAR TABLERO
# ============================================================

if clear_button:

    st.session_state.canvas_key += 1
    st.session_state.analysis_done = False
    st.session_state.full_response = ""
    st.session_state.drawing_bytes = None
    st.session_state.story = ""

    st.rerun()


# ============================================================
# ANALIZAR DIBUJO
# ============================================================

if analyze_button:

    if not api_key:

        st.warning(
            "Ingresa tu clave API de OpenAI en el panel lateral."
        )

    elif canvas_result.image_data is None:

        st.warning("Primero realiza un dibujo.")

    else:

        try:

            input_array = np.array(
                canvas_result.image_data
            ).astype("uint8")

            input_image = Image.fromarray(
                input_array
            ).convert("RGB")

            pixels = np.array(input_image)

            if not np.any(pixels < 245):

                st.warning(
                    "El tablero está vacío. Realiza un dibujo "
                    "antes de analizarlo."
                )

            else:

                with st.spinner(
                    "🎨 HablaTrazo está observando tu dibujo..."
                ):

                    client = OpenAI(api_key=api_key)

                    image_base64 = image_to_base64(input_image)

                    result = analyze_drawing(
                        client,
                        image_base64,
                        age_group,
                        objective
                    )

                    buffer = BytesIO()
                    input_image.save(buffer, format="PNG")

                    st.session_state.drawing_bytes = buffer.getvalue()
                    st.session_state.full_response = result
                    st.session_state.analysis_done = True
                    st.session_state.story = ""

                st.success("¡Tu dibujo ha sido analizado!")

        except Exception as e:

            st.error(
                "No se pudo analizar el dibujo. "
                "Revisa tu conexión y tu clave API."
            )

            st.caption(f"Detalle del error: {str(e)}")


# ============================================================
# RESULTADOS
# ============================================================

if st.session_state.analysis_done:

    st.divider()

    st.markdown("## 🧠 ¡Descubramos tu dibujo!")

    result_col1, result_col2 = st.columns([1, 2])

    with result_col1:

        st.markdown("### Tu dibujo")

        st.image(
            st.session_state.drawing_bytes,
            use_container_width=True
        )

    with result_col2:

        st.markdown("### Lo que interpreta HablaTrazo")

        st.markdown(
            st.session_state.full_response
        )


    # ========================================================
    # CREAR HISTORIA
    # ========================================================

    st.divider()

    st.markdown("## 📚 ¡Convirtamos el dibujo en una historia!")

    st.write(
        "HablaTrazo puede crear una pequeña historia a partir "
        "de los elementos identificados en el dibujo."
    )

    if st.button("✨ Crear una historia infantil"):

        try:

            with st.spinner("Inventando una historia..."):

                client = OpenAI(api_key=api_key)

                story = create_story(
                    client,
                    st.session_state.full_response,
                    age_group
                )

                st.session_state.story = story

        except Exception as e:

            st.error(
                "No se pudo crear la historia. "
                "Comprueba tu clave API."
            )

            st.caption(f"Detalle del error: {str(e)}")


    if st.session_state.story:

        st.markdown("### 📖 Nuestra historia")

        st.markdown(
            f"""
            <div class="tarjeta">
                {st.session_state.story}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()

st.markdown(
    """
    <p style="
        text-align:center;
        color:#789A9D;
        font-size:0.85rem;
    ">
        HablaTrazo · Dibuja, descubre y conversa 🎨
        <br>
        Herramienta de apoyo. Las sugerencias deben ser revisadas
        y adaptadas por el terapeuta.
    </p>
    """,
    unsafe_allow_html=True
)
