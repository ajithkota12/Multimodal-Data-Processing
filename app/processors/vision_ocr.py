from typing import Optional
from PIL import Image
import pytesseract


def extract_text_from_image(path: str, tesseract_cmd: Optional[str] = None) -> str:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    image = Image.open(path)
    text = pytesseract.image_to_string(image)
    return text


