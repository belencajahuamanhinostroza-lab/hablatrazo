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
    page_title="HablaTrazo | Tablero de lenguaje",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .titulo {
        color: #344767;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitulo {
        color: #718096;
        font-size: 1.05rem;
        margin-top: 5px;
    }

    .tarjeta {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        margin-bottom: 15px;
    }

    .pequeno {
        color: #718096;
        font-size: 0.9rem;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
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

if "drawing_base64" not in st.session_state:
    st.session_state.drawing_base64 = ""

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
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def create_client(api_key):
    """Crea el cliente de OpenAI."""
    return OpenAI(api_key=api_key)


def analyze_drawing(client, image_base64, age_group, objective):
    """Analiza el dibujo y propone actividades de lenguaje."""

    prompt = f"""
    Eres un asistente educativo que apoya a terapeutas de lenguaje
    en actividades de estimulación del lenguaje infantil.

    Vas a observar el dibujo realizado por un niño.

    INFORMACIÓN PARA ADAPTAR LA ACTIVIDAD:
    - Grupo de edad aproximado: {age_group}
    - Objetivo que desea trabajar el terapeuta: {objective}

    Analiza el dibujo y responde en español con un lenguaje claro,
    amable y sencillo.

    Organiza tu respuesta con estas secciones:

    ### 1. ¿Qué observamos en el dibujo?
    Describe brevemente los elementos que parecen aparecer.
    Si no estás seguro de qué representa algún elemento, indícalo
    y ofrece posibles interpretaciones. No inventes detalles.

    ### 2. Palabras para trabajar
    Propón entre 4 y 6 palabras relacionadas con el dibujo.
    Incluye sustantivos, características o acciones cuando corresponda.

    ### 3. Preguntas para conversar
    Propón 4 preguntas abiertas y sencillas que el terapeuta
    pueda hacerle al niño sobre su dibujo.

    ### 4. Actividad de lenguaje
    Crea una actividad breve relacionada con el objetivo:
    {objective}

    Explica cómo realizarla en unos pocos pasos.

    ### 5. Ejemplo de frase
    Propón 2 frases cortas que el niño podría construir
    utilizando los elementos de su dibujo.

    ### 6. Idea para continuar
    Sugiere una pequeña pregunta o reto para que el niño
    pueda ampliar su dibujo o seguir conversando.

    IMPORTANTE:
    - Adapta la complejidad al grupo de edad indicado.
    - Mantén un tono positivo, cercano y respetuoso.
    - No evalúes la inteligencia, el desarrollo ni las capacidades
      del niño a partir de su dibujo.
    - No realices diagnósticos ni afirmes que el niño tiene
      dificultades de lenguaje.
    - No confundas la interpretación del dibujo con una evaluación
      de pronunciación o expresión oral.
    - Estas sugerencias son orientativas y deben ser revisadas
      por el terapeuta.
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
    """Genera una historia breve basada en el dibujo."""

    prompt = f"""
    Crea una historia infantil breve y creativa basada en esta
    interpretación de un dibujo:

    {description}

    La historia debe estar adaptada para niños de {age_group}.
    Utiliza palabras sencillas, oraciones cortas y un tono divertido.

    Al final agrega:
    - 3 preguntas sencillas sobre la historia.
    - 3 palabras importantes que el niño pueda aprender o repetir.

    No agregues elementos que contradigan la descripción del dibujo.
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
    "HablaTrazo convierte los dibujos de los niños en oportunidades "
    "para conversar, aprender palabras y construir pequeñas historias."
)


# ============================================================
# PANEL LATERAL: CONFIGURACIÓN
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
        "La edad solo sirve para adaptar la dificultad de las "
        "actividades. No representa una evaluación del niño."
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
        "La clave se utiliza para realizar el análisis con el modelo "
        "de inteligencia artificial."
    )

    st.divider()

    st.markdown("### 💡 Acerca de HablaTrazo")

    st.write(
        "Una herramienta de apoyo para que los terapeutas puedan "
        "aprovechar los dibujos infantiles como punto de partida "
        "para actividades de lenguaje."
    )


# ============================================================
# TABLERO DE DIBUJO
# ============================================================

st.markdown("## 🖍️ ¡Vamos a dibujar!")

st.write(
    "Dibuja lo que quieras en el tablero. Puede ser un animal, "
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

    st.markdown("### 🌈 Tu espacio creativo")

    st.markdown("""
    <div class="tarjeta">
        <h4>¿Qué puedes dibujar?</h4>
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
        <h4>¿Cómo funciona?</h4>
        <p>1. Realiza un dibujo.</p>
        <p>2. Presiona analizar.</p>
        <p>3. Descubre qué interpreta la IA.</p>
        <p>4. Utiliza las actividades para conversar.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# BOTONES DEL TABLERO
# ============================================================

button_col1, button_col2 = st.columns([1, 1])

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


if clear_button:

    st.session_state.canvas_key += 1
    st.session_state.analysis_done = False
    st.session_state.full_response = ""
    st.session_state.drawing_base64 = ""
    st.session_state.drawing_bytes = None
    st.session_state.story = ""

    st.rerun()


# ============================================================
# ANÁLISIS DEL DIBUJO
# ============================================================

if analyze_button:

    if not api_key:

        st.warning(
            "Primero debes ingresar tu clave API de OpenAI "
            "en el panel de configuración."
        )

    elif canvas_result.image_data is None:

        st.warning("Primero realiza un dibujo en el tablero.")

    else:

        try:

            # Convertir el dibujo a una imagen
            input_array = np.array(
                canvas_result.image_data
            ).astype("uint8")

            input_image = Image.fromarray(
                input_array
            ).convert("RGB")

            # Comprobar que el lienzo no esté vacío
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

                    client = create_client(api_key)

                    # Codificar imagen
                    image_base64 = image_to_base64(input_image)

                    # Analizar dibujo
                    result = analyze_drawing(
                        client,
                        image_base64,
                        age_group,
                        objective
                    )

                    # Guardar resultados
                    buffer = BytesIO()
                    input_image.save(buffer, format="PNG")

                    st.session_state.drawing_bytes = buffer.getvalue()
                    st.session_state.drawing_base64 = image_base64
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
# RESULTADOS DEL ANÁLISIS
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
    # HISTORIA INFANTIL
    # ========================================================

    st.divider()

    st.markdown("## 📚 ¡Convirtamos el dibujo en una historia!")

    st.write(
        "A partir de lo que aparece en el dibujo, HablaTrazo "
        "puede crear una pequeña historia para seguir conversando."
    )

    if st.button(
        "✨ Crear una historia infantil",
        use_container_width=False
    ):

        try:

            with st.spinner("Inventando una historia..."):

                client = create_client(api_key)

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
    <p style="text-align:center; color:#718096; font-size:0.85rem;">
        HablaTrazo · Dibuja, descubre y conversa 🎨
        <br>
        Herramienta de apoyo. Las sugerencias deben ser revisadas
        y adaptadas por el terapeuta.
    </p>
    """,
    unsafe_allow_html=True
)
