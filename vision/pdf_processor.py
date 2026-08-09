
import os
import fitz
from PIL import Image
import pytesseract



TEMP_FOLDER = "HintAI/data/pdf_pages"



# ==========================================
# CONVERTIR PDF EN IMAGES
# ==========================================

def pdf_to_images(pdf_file):

    """
    Convertit chaque page PDF
    en image exploitable.
    """

    os.makedirs(
        TEMP_FOLDER,
        exist_ok=True
    )


    document = fitz.open(
        pdf_file
    )


    images = []


    for index, page in enumerate(document):


        pix = page.get_pixmap(
            dpi=200
        )


        image_path = (
            f"{TEMP_FOLDER}/page_{index}.png"
        )


        pix.save(
            image_path
        )


        images.append(
            image_path
        )


    return images




# ==========================================
# EXTRACTION TEXTE PDF
# ==========================================

def extract_pdf_text(pdf_file):


    document = fitz.open(
        pdf_file
    )


    text = ""


    for page in document:

        text += page.get_text()



    return text.strip()




# ==========================================
# OCR IMAGE PDF
# ==========================================

def ocr_pdf_pages(images):


    result = ""


    for image_path in images:


        image = Image.open(
            image_path
        )


        result += pytesseract.image_to_string(
            image,
            lang="fra"
        )


    return result




# ==========================================
# PIPELINE COMPLET
# ==========================================

def process_pdf(pdf_file):


    pages = pdf_to_images(
        pdf_file
    )


    text = extract_pdf_text(
        pdf_file
    )


    if len(text) < 20:

        text = ocr_pdf_pages(
            pages
        )



    return {

        "pages": pages,

        "text": text

    }

