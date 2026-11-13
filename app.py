
from pathlib import Path
import base64
import mimetypes
import re
import streamlit as st

st.set_page_config(
    page_title="I.E. 82641 Simón Bolívar",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

base = Path(__file__).parent

# Leer los archivos de la página
html = (base / "index.html").read_text(encoding="utf-8")
css = (base / "styles.css").read_text(encoding="utf-8")
config = (base / "config.js").read_text(encoding="utf-8")
script = (base / "script.js").read_text(encoding="utf-8")

# Incorporar el diseño CSS
html = html.replace(
    '<link rel="stylesheet" href="styles.css">',
    f"<style>{css}</style>"
)

# Incorporar JavaScript
html = html.replace(
    '<script src="config.js"></script>',
    f"<script>{config}</script>"
)

html = html.replace(
    '<script src="script.js"></script>',
    f"<script>{script}</script>"
)

# Incorporar imágenes locales en el HTML
assets = base / "assets"

if assets.exists():
    for imagen in assets.iterdir():
        if imagen.suffix.lower() not in (
            ".png", ".jpg", ".jpeg", ".webp"
        ):
            continue

        mime = mimetypes.guess_type(imagen.name)[0]
        if not mime:
            continue

        contenido = base64.b64encode(
            imagen.read_bytes()
        ).decode("ascii")

        data_url = f"data:{mime};base64,{contenido}"

        html = html.replace(
            f"assets/{imagen.name}",
            data_url
        )

        # Rutas utilizadas por la galería JavaScript
        html = html.replace(
            f'`assets/${{filename}}`',
            '`' + "assets/${filename}" + '`'
        )

# Ajustar el contenedor Streamlit
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

# Mostrar la página completa e interactiva
st.iframe(
    html,
    width="stretch",
    height="content"
)
