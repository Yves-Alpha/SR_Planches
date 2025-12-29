# pdf_utils.py
# Utilities for cropping PDF pages and generating planches (1x4 on A4)

import math
import PyPDF2
from PyPDF2 import Transformation
from PyPDF2._page import PageObject
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from pdf2image import convert_from_bytes
from reportlab.lib.utils import ImageReader
import streamlit as st
import os

# Helper constants for sizes (in points)
MM_TO_PT = 72 / 25.4
SIZE_140x70_MM = (140 * MM_TO_PT, 70 * MM_TO_PT)
SIZE_70x140_MM = (70 * MM_TO_PT, 140 * MM_TO_PT)
A4_WIDTH, A4_HEIGHT = 595.2756, 841.8898  # A4 size in points

def crop_page(input_pdf, output_pdf):
    width_pt, height_pt = SIZE_140x70_MM
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()
    for page in reader.pages:
        mb = page.mediabox
        orig_width = float(mb.width)
        orig_height = float(mb.height)
        left = (orig_width - width_pt) / 2
        bottom = (orig_height - height_pt) / 2
        right = left + width_pt
        top = bottom + height_pt
        # Set both mediabox and cropbox
        page.mediabox.lower_left = [left, bottom]
        page.mediabox.upper_right = [right, top]
        page.cropbox.lower_left = [left, bottom]
        page.cropbox.upper_right = [right, top]
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)

def _merge_at(page, src_page, scale, tx, ty):
    transformation = Transformation().scale(scale, scale).translate(tx, ty)
    src_page.add_transformation(transformation)
    page.merge_page(src_page)

def create_planche(input_pdf: str, output_pdf: str | None = None, base_name: str | None = None) -> str:
    """
    Arrange pages from input_pdf in groups of 4 vertically on A4 pages.
    Each page is scaled and placed into a 140x70 mm slot on an A4 page.
    """
    out_dir = os.path.dirname(input_pdf)
    if output_pdf is None:
        if base_name is not None:
            base = base_name
        else:
            base = os.path.splitext(os.path.basename(input_pdf))[0]
            for suffix in ("-cropped", "_cropped", " cropped"):
                if base.endswith(suffix):
                    base = base[:-len(suffix)]
                    break
        output_pdf = os.path.join(out_dir, base + "-planche.pdf")

    SLOT_W, SLOT_H = 140 * MM_TO_PT, 70 * MM_TO_PT
    A4_W, A4_H = A4_WIDTH, A4_HEIGHT
    GAP = 5  # spacing in points

    reader = PyPDF2.PdfReader(input_pdf)
    c = canvas.Canvas(output_pdf, pagesize=A4)

    margin_top = (A4_H - (4 * SLOT_H + 3 * GAP)) / 2

    num_pages = len(reader.pages)
    progress_bar = st.progress(0, text="Génération des planches...")
    total = num_pages
    done = 0

    for i in range(0, num_pages, 4):
        for j in range(4):
            page_index = i + j
            if page_index >= num_pages:
                break
            # Extract single page into bytes
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[page_index])
            buf = BytesIO()
            writer.write(buf)
            buf.seek(0)

            # Convert single page PDF bytes to image
            images = convert_from_bytes(buf.getvalue(), dpi=300, use_cropbox=True)
            img = images[0]
            img_reader = ImageReader(img)

            # Compute position
            x = (A4_W - SLOT_W) / 2
            y = A4_H - margin_top - (j + 1) * SLOT_H - j * GAP

            # Draw image on canvas
            c.drawImage(img_reader, x, y, width=SLOT_W, height=SLOT_H)
            done += 1
            progress_bar.progress(done/total, text=f"Traitement page {done}/{total}")
        c.showPage()
    progress_bar.progress(1.0, text="Terminé !")
    c.save()
    return output_pdf
