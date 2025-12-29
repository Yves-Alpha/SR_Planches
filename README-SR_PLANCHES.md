# SR_Planches – Installation & lancement

## Prérequis
- macOS avec connexion internet (pour installer les dépendances au premier lancement)
- Python 3.12 (python.org recommandé, inclut Tk)
- Poppler (pdftoppm) via Homebrew : `brew install poppler`

## Installation automatique (recommandée)
1. Installe Python 3.12 depuis https://www.python.org/downloads/macos/
2. Installe Poppler : `brew install poppler`
3. Lance `SR_Planches.app` (ou `launch.py`). Le script :
   - crée/rafraîchit un venv local (`./venv`) si besoin
   - installe/maj pip, setuptools, wheel
   - installe les dépendances de `requirements.txt`
   - vérifie les imports (`streamlit, pikepdf, reportlab, PyPDF2, pdf2image, pillow, tkinter`)
   - démarre Streamlit sur `http://localhost:8501`

## En cas de souci
- Si `pdftoppm` est introuvable, installe Poppler (`brew install poppler`).
- Si Python 3.12 n’est pas vu, vérifie avec `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -V`.
- Tu peux supprimer le dossier `venv/` pour forcer une réinstallation au prochain lancement.
