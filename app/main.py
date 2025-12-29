import streamlit as st
import tempfile
import os
from pathlib import Path
from pdf_utils import crop_page, create_planche

# UI settings: title + favicon
ROOT_DIR = Path(__file__).resolve().parent.parent
FAVICON = ROOT_DIR / "SR-Planche.png"
st.set_page_config(
    page_title="SR Planche",
    page_icon=str(FAVICON) if FAVICON.exists() else "🖨️",
    layout="centered",
)

st.title("Créateur de Planches PDF A4")

uploaded_file = st.file_uploader("Déposer un fichier pdf avec les pages à imposer", type=["pdf"])

if uploaded_file is not None:
    if st.button("Composer les planches"):
        with tempfile.TemporaryDirectory() as tmpdirname:
            input_path = os.path.join(tmpdirname, "input.pdf")
            cropped_path = os.path.join(tmpdirname, "cropped.pdf")

            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            crop_page(input_path, cropped_path)

            # base = nom du fichier fourni par l’utilisateur, sans extension
            base_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
            output_path = create_planche(cropped_path, base_name=base_name)

            with open(output_path, "rb") as f:
                st.download_button(
                    label="Télécharger le PDF généré",
                    data=f,
                    file_name=os.path.basename(output_path),  # ex: 2516-SR CODI EXPRESS-planche.pdf
                    mime="application/pdf"
                )
