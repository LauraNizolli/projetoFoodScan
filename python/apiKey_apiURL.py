
import os
from dotenv import load_dotenv
load_dotenv()


OCR_API_KEY = os.getenv(
    "OCR_SPACE_API_KEY"
)

OCR_API_URL = (
    "https://api.ocr.space/parse/image"
)