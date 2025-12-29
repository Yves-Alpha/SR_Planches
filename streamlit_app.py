"""Entrée Streamlit Cloud pour SR_Planches."""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "app"

# Ajouter le dossier app/ au PYTHONPATH pour les imports (pdf_utils, etc.)
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Exécuter le script Streamlit principal
runpy.run_path(str(APP_DIR / "main.py"), run_name="__main__")
