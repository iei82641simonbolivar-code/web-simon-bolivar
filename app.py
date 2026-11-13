from pathlib import Path
import streamlit as st
st.set_page_config(page_title="I.E. 82641 Simón Bolívar", page_icon="🏫", layout="wide")
st.iframe(Path(__file__).parent / "index.html", height=1200)
