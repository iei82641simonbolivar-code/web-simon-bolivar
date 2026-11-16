from pathlib import Path
import base64
import json
import mimetypes
import streamlit as st

st.set_page_config(page_title="I.E. 82641 Simón Bolívar", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")
base = Path(__file__).parent
assets = base / "assets"
html = (base / "index.html").read_text(encoding="utf-8")
css = (base / "styles.css").read_text(encoding="utf-8")
script = (base / "script.js").read_text(encoding="utf-8")
config = (base / "config.js").read_text(encoding="utf-8")

# Convertir las fotografías cargadas en GitHub a recursos embebidos.
images = {}
for file in assets.iterdir():
    if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        mime = mimetypes.guess_type(file.name)[0] or "image/jpeg"
        data = base64.b64encode(file.read_bytes()).decode("ascii")
        images[file.name] = f"data:{mime};base64,{data}"

if "insignia.png" in images:
    html = html.replace('src="assets/insignia.png"', f'src="{images["insignia.png"]}"')

# Portada sin estudiantes identificables. La foto original anterior no se usa de fondo.
if "patio-2.jpeg" in images:
    css += f'''
.hero {{background-image:linear-gradient(rgba(7,24,47,.78),rgba(7,24,47,.70)),url("{images['patio-2.jpeg']}");background-size:cover;background-position:center;background-repeat:no-repeat;}}
'''

html = html.replace('<link rel="stylesheet" href="styles.css">', f"<style>{css}</style>")
html = html.replace('<script src="config.js"></script>', f"<script>{config}</script>")
html = html.replace('<script src="script.js"></script>', f"<script>window.SCHOOL_IMAGES = {json.dumps(images)};\n{script}</script>")

# Barra superior de Streamlit no debe superponerse a la cabecera del colegio.
st.markdown('''
<style>
  header[data-testid="stHeader"] {display:none !important;}
  [data-testid="stToolbar"] {display:none !important;}
  #MainMenu {display:none !important;}
  .block-container {padding:0 !important;max-width:100% !important;}
  [data-testid="stAppViewContainer"] > .main {padding-top:0 !important;}
</style>
''', unsafe_allow_html=True)

st.iframe(html,width="stretch",height="content")
