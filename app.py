
from pathlib import Path
import base64
import json
import mimetypes
import streamlit as st

st.set_page_config(
    page_title="I.E. 82641 Simón Bolívar",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

base = Path(__file__).parent
assets = base / "assets"

# Leer los archivos existentes
html = (base / "index.html").read_text(
    encoding="utf-8"
)
css = (base / "styles.css").read_text(
    encoding="utf-8"
)
config = (base / "config.js").read_text(
    encoding="utf-8"
)
script = (base / "script.js").read_text(
    encoding="utf-8"
)

# Convertir fotografías en recursos internos
imagenes = {}

for archivo in assets.glob("*"):
    if archivo.suffix.lower() in [
        ".png", ".jpg", ".jpeg", ".webp"
    ]:
        mime = mimetypes.guess_type(archivo.name)[0]
        contenido = base64.b64encode(
            archivo.read_bytes()
        ).decode("utf-8")

        imagenes[archivo.name] = (
            f"data:{mime};base64,{contenido}"
        )

# Insignia oficial
if "insignia.png" in imagenes:
    html = html.replace(
        'src="assets/insignia.png"',
        f'src="{imagenes["insignia.png"]}"'
    )

# Patio real como fondo principal
if "patio.jpg" in imagenes:
    css += f"""
    .hero {{
        background-image:
            linear-gradient(
                rgba(7, 24, 47, 0.78),
                rgba(7, 24, 47, 0.70)
            ),
            url("{imagenes['patio.jpg']}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    """

# Aplicar estilos
html = html.replace(
    '<link rel="stylesheet" href="styles.css">',
    f"<style>{css}</style>"
)

# Hacer funcionar la galería de fotos
mapa = json.dumps(imagenes)

script = script.replace(
    "const url = `assets/${filename}`;",
    'const url = window.SCHOOL_IMAGES[filename] '
    '|| `assets/${filename}`;'
)

script = script.replace(
    "image.src = `assets/${card.dataset.file}`;",
    'image.src = window.SCHOOL_IMAGES[card.dataset.file] '
    '|| `assets/${card.dataset.file}`;'
)

html = html.replace(
    '<script src="config.js"></script>',
    f"<script>{config}</script>"
)

html = html.replace(
    '<script src="script.js"></script>',
    f"<script>window.SCHOOL_IMAGES = {mapa};"
    f"\n{script}</script>"
)

# Mostrar la web
st.markdown(
    """
    <style>
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.iframe(
    html,
    width="stretch",
    height="content"
)
