
import pytesseract
from PIL import Image


def extract_text(image):

    """
    Extraction texte depuis une image.
    """

    try:

        text = pytesseract.image_to_string(
            Image.open(image),
            lang="fra"
        )

        return text.strip()


    except Exception as e:

        return f"OCR_ERROR: {str(e)}"

