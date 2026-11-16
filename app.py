from pathlib import Path
import base64
import json
import mimetypes
import streamlit as st

st.set_page_config(page_title="I.E.I. N.º 82641 Simón Bolívar", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")
base = Path(__file__).parent
assets = base / "assets"
html = (base / "index.html").read_text(encoding="utf-8")
css = (base / "styles.css").read_text(encoding="utf-8")
script = (base / "script.js").read_text(encoding="utf-8")
config = (base / "config.js").read_text(encoding="utf-8")

# Buscar imágenes tanto en assets/ como en la raíz para evitar rutas rotas.
images = {}
for folder in (base, assets):
    if not folder.is_dir():
        continue
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            mime = mimetypes.guess_type(file.name)[0] or "image/jpeg"
            images[file.name.lower()] = f"data:{mime};base64,{base64.b64encode(file.read_bytes()).decode('ascii')}"

# Admitir jpg/jpeg indistintamente y mayúsculas/minúsculas.
for name in list(images):
    if name.endswith(".jpeg"):
        images.setdefault(name[:-5] + ".jpg", images[name])
    elif name.endswith(".jpg"):
        images.setdefault(name[:-4] + ".jpeg", images[name])

if "insignia.png" in images:
    html = html.replace('src="assets/insignia.png"', f'src="{images["insignia.png"]}"')

# Fondo original de la portada: patio.jpg.
# Revisa que la imagen no muestre menores identificables antes de publicar.
patio = images.get("patio.jpg")
if patio:
    css += f'\n.hero {{background-image:linear-gradient(rgba(5,24,46,.74),rgba(5,24,46,.72)),url("{patio}")!important;}}\n'

html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css}</style>')
html = html.replace('<script src="config.js"></script>', f'<script>{config}</script>')
html = html.replace('<script src="script.js"></script>', f'<script>window.SCHOOL_IMAGES = {json.dumps(images)};\n{script}</script>')

st.markdown("""<style>
header[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu {display:none!important}
.block-container {padding:0!important;max-width:100%!important}
[data-testid="stAppViewContainer"] > .main {padding-top:0!important}
</style>""", unsafe_allow_html=True)
st.iframe(html, width="stretch", height="content")
