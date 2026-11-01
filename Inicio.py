
import base64
from io import BytesIO

import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="HablaTrazo",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# DISEÑO VISUAL
# ============================================================

st.markdown("""
<style>

/* PALETA:
   Verde menta: #70C69E
   Amarillo:    #F8E7A2
   Azul:        #176BFF
   Azul oscuro: #244B78
*/

/* FONDO COMPLETO */
.stApp {
    background: linear-gradient(
        135deg,
        #DDF4E9 0%,
        #E9F5F8 35%,
        #FFF3CE 70%,
        #E3EEFF 100%
    );
    background-attachment: fixed;
}

/* Fondo del área principal */
[data-testid="stAppViewContainer"] {
    background: transparent;
}

[data-testid="stMain"] {
    background: transparent;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* BARRA LATERAL */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #BFEBD5 0%,
        #D9F0E6 40%,
        #DDEAFF 100%
    );
    border-right: 2px solid #C4E6DA;
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

/* TÍTULO */
.titulo {
    font-size: 4.5rem;
    font-weight: 950;
    letter-spacing: -2px;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(
        100deg,
        #258B65 0%,
        #E0AC25 48%,
        #176BFF 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* SUBTÍTULO */
.subtitulo {
    font-size: 1.15rem;
    font-weight: 600;
    color: #426B79 !important;
    margin-top: 10px;
}

/* TEXTO INTRODUCTORIO */
.intro {
    background: linear-gradient(
        100deg,
        #BDEBD3,
        #D6EBFF,
        #FFF0BB
    );
    border: 1px solid #C5E6D8;
    border-radius: 18px;
    padding: 17px 22px;
    color: #315B68 !important;
    font-weight: 600;
    margin: 20px 0;
}

/* TARJETAS */
.tarjeta {
    background: linear-gradient(
        145deg,
        #FFFFFF 0%,
        #E9F8EF 55%,
        #FFF8E4 100%
    );
    border: 2px solid #D5EBDD;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 17px;
    box-shadow: 0 6px 18px rgba(56, 119, 103, 0.10);
    color: #345E67;
}

.tarjeta h4 {
    color: #278464 !important;
    font-weight: 800;
}

.tarjeta p {
    color: #426A73 !important;
}

/* TARJETA AZUL */
.tarjeta-azul {
    background: linear-gradient(
        145deg,
        #DCEAFF,
        #C9E4FA
    );
    border: 2px solid #BDD7F5;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 17px;
    color: #244B78;
}

.tarjeta-azul h4,
.tarjeta-azul p {
    color: #244B78 !important;
}

/* TARJETA AMARILLA */
.tarjeta-amarilla {
    background: linear-gradient(
        145deg,
        #FFF5D0,
        #FFEAA9
    );
    border: 2px solid #F1D989;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 17px;
    color: #755D25;
}

.tarjeta-amarilla h4,
.tarjeta-amarilla p {
    color: #755D25 !important;
}

/* BOTONES GENERALES */
div.stButton > button {
    background: #176BFF !important;
    color: #FFFFFF !important;
    border: 2px solid #176BFF !important;
    border-radius: 14px !important;
    min-height: 48px;
    font-size: 0.96rem;
    font-weight: 750;
    box-shadow: 0 5px 12px rgba(23, 107, 255, 0.18);
    transition: all 0.2s ease;
}

/* Texto interno de botones */
div.stButton > button p,
div.stButton > button span {
    color: #FFFFFF !important;
}

/* Hover */
div.stButton > button:hover {
    background: #0755DB !important;
    border-color: #0755DB !important;
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 7px 16px rgba(23, 107, 255, 0.25);
}

/* Botón principal */
div.stButton > button[kind="primary"] {
    background: linear-gradient(
        100deg,
        #258B65,
        #176BFF
    ) !important;
    border: none !important;
    color: white !important;
}

/* BOTONES DE LA BARRA LATERAL */
section[data-testid="stSidebar"] div.stButton > button {
    background: #258B65 !important;
    border-color: #258B65 !important;
}

/* SELECTORES */
div[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 2px solid #B8DCCB !important;
    border-radius: 12px !important;
}

/* INPUTS */
div[data-baseweb="input"] {
    background: #FFFFFF !important;
    border: 2px solid #B8DCCB !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input {
    color: #315B68 !important;
}

/* TEXTAREA */
div[data-baseweb="textarea"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}

/* RADIO BUTTONS */
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.65);
    border-radius: 10px;
    padding: 7px 10px;
}

/* SLIDER */
div[data-testid="stSlider"] [role="slider"] {
    background: #176BFF !important;
}

/* CHECKBOX */
div[data-testid="stCheckbox"] {
    color: #315B68;
}

/* ALERTAS */
div[data-testid="stAlert"] {
    background: linear-gradient(
        100deg,
        #E4F5E9,
        #E2EDFF
    );
    border: 2px solid #C9E5D7;
    border-radius: 15px;
}

/* MENSAJES DE ÉXITO */
div[data-testid="stAlert"][data-type="success"] {
    background: #DDF5E5;
}

/* ENCABEZADOS */
h1, h2, h3 {
    color: #285E73 !important;
    font-weight: 850;
}

h4 {
    color: #398B72 !important;
}

/* TEXTO */
p, label, li {
    color: #426B73;
}

/* SEPARADORES */
hr {
    border-color: #BFDCCF;
}

/* LIENZO */
canvas {
    border-radius: 18px !important;
    border: 3px solid #FFFFFF !important;
    box-shadow: 0 5px 18px rgba(51, 105, 106, 0.12);
}

/* IMÁGENES */
[data-testid="stImage"] img {
    border-radius: 16px;
}

/* PIE DE PÁGINA */
.footer {
    text-align: center;
    color: #567B83;
    font-size: 0.9rem;
    padding: 18px;
}

/* TABS */
button[data-baseweb="tab"] {
    color: #315B68 !important;
    font-weight: 700;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #176BFF !important;
}

/* OCULTAR ESPACIO SUPERIOR EXCESIVO */
header[data-testid="stHeader"] {
    background: transparent;
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
    Si no estás seguro, menciona posibles interpretaciones.

    ### 2. Palabras para trabajar
    Propón entre 4 y 6 palabras relacionadas con el dibujo.
    Incluye sustantivos, características y acciones.

    ### 3. Preguntas para conversar
    Propón 4 preguntas abiertas y sencillas para el niño.

    ### 4. Actividad de lenguaje
    Crea una actividad breve relacionada con:
    {objective}

    Explica cómo realizarla en pocos pasos.

    ### 5. Construcción de frases
    Propón 2 frases cortas que el niño podría construir
    con los elementos del dibujo.

    ### 6. Idea para continuar
    Sugiere un reto o pregunta para ampliar el dibujo.

    REGLAS:
    - Adapta la complejidad a la edad indicada.
    - Mantén un tono positivo y cercano.
    - No inventes detalles.
    - No realices diagnósticos.
    - No evalúes la inteligencia ni el desarrollo del niño.
    - No evalúes pronunciación a partir del dibujo.
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
    '<p class="subtitulo">'
    'Dibuja, descubre y conversa. '
    'Un espacio creativo para estimular el lenguaje infantil.'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="intro">
        🌈 ¡Bienvenido a HablaTrazo! Aquí cada dibujo se convierte
        en una oportunidad para imaginar, aprender nuevas palabras
        y crear historias.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PANEL LATERAL
# ============================================================

with st.sidebar:

    st.markdown("## 🌟 HablaTrazo")

    st.markdown("### ⚙️ Configuración")

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
                "#176BFF",
                "#258B65",
                "#9B59B6",
                "#F0C94D",
                "#FF69B4",
                "#795548"
            ],
            format_func=lambda color: {
                "#222222": "Negro",
                "#E74C3C": "Rojo",
                "#176BFF": "Azul eléctrico",
                "#258B65": "Verde",
                "#9B59B6": "Morado",
                "#F0C94D": "Amarillo",
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
        "La clave se utiliza para analizar los dibujos "
        "con inteligencia artificial."
    )

    st.divider()

    st.markdown(
        """
        <div class="tarjeta-amarilla">
            <h4>💡 Sobre HablaTrazo</h4>
            <p>
                Una herramienta de apoyo para aprovechar los dibujos
                infantiles como punto de partida para actividades
                de lenguaje.
            </p>
        </div>
        """,
        unsafe_allow_html=True
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

    st.markdown(
        """
        <div class="tarjeta">
            <h4>🌈 ¿Qué puedes dibujar?</h4>
            <p>🐶 Animales</p>
            <p>🏠 Lugares</p>
            <p>🍎 Alimentos</p>
            <p>👨‍👩‍👧 Personas</p>
            <p>🚗 Objetos</p>
            <p>🌳 Naturaleza</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tarjeta-amarilla">
            <h4>💡 ¿Cómo funciona?</h4>
            <p>1. Realiza un dibujo.</p>
            <p>2. Presiona analizar.</p>
            <p>3. Descubre qué interpreta la IA.</p>
            <p>4. Utiliza las actividades para conversar.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# BOTONES
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

        st.markdown("### 🎨 Tu dibujo")

        st.image(
            st.session_state.drawing_bytes,
            use_container_width=True
        )

    with result_col2:

        st.markdown("### 💬 Lo que interpreta HablaTrazo")

        st.markdown(
            st.session_state.full_response
        )


    # ========================================================
    # HISTORIA INFANTIL
    # ========================================================

    st.divider()

    st.markdown("## 📚 ¡Convirtamos el dibujo en una historia!")

    st.write(
        "HablaTrazo puede crear una pequeña historia a partir "
        "de los elementos identificados en el dibujo."
    )

    if st.button("✨ Crear una historia infantil"):

        try:

            with st.spinner("🌟 Inventando una historia..."):

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

        st.markdown(
            """
            <div class="tarjeta-amarilla">
                <h4>📖 Nuestra historia</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(st.session_state.story)


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🎨 <b>HablaTrazo</b> · Dibuja, descubre y conversa.
        <br><br>
        Una herramienta de apoyo. Las sugerencias deben ser
        revisadas y adaptadas por el terapeuta.
        <br>
        💚 💛 💙
    </div>
    """,
    unsafe_allow_html=True
)
