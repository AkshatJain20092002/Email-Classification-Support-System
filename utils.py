import logging
import re
import textwrap
import unicodedata

from deep_translator import GoogleTranslator as DeepGoogleTranslator
from ftfy import fix_text
from googletrans import Translator
from langdetect import detect
import spacy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load spaCy models
try:
    nlp_multi = spacy.load("xx_ent_wiki_sm")
except OSError:
    spacy.cli.download("xx_ent_wiki_sm")
    nlp_multi = spacy.load("xx_ent_wiki_sm")


class PIIMasker:
    """
    Detect and mask PII in text using regex and spaCy NER.
    """

    @staticmethod
    def patterns() -> dict:
        return {
            # "full_name": (
            #     r'(?i)(?:my name is|this is)\s+([A-Z]\w*)\s+([A-Z]\w*)'
            # ),
            "email": (
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+'
                r'\.[A-Z|a-z]{2,}\b'
            ),
            "phone_number": (
                r'(?:\+\d{1,3}[-\s.]?\d{1,4}[-\s.]?\d{1,4}'
                r'[-\s.]?\d{1,10}|'
                r'\b\d{3}[-\s.]?\d{3}[-\s.]?\d{4}\b)'
            ),
            "dob": (
                r'(?i)(?:born|birth|dob|birthday)'
                r'(?:\s+(?:on|date|is|:))?\s+'
                r'(?P<dob>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ),
            "credit_debit_no": (
                r'(?:^[0-9]{4}[0-9]{4}[0-9]{4}[0-9]{4}$)|'
                r'(?:^[0-9]{4}\s[0-9]{4}\s[0-9]{4}\s[0-9]{4}$)|'
                r'(?:^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$)|'
                r'(?:\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b)'
            ),
            "aadhar_num": (
                r'(?:^[0-9]{4}[0-9]{4}[0-9]{4}$)|'
                r'(?:^[0-9]{4}\s[0-9]{4}\s[0-9]{4}$)|'
                r'(?:^[0-9]{4}-[0-9]{4}-[0-9]{4}$)|'
                r'(?:\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b)'
            ),
            "cvv_no": (
                r'(?:CVV|CVC|cvv|cvc|security code|card code)'
                r'[\s:]*\d{3}|'
                r'\b\d{3}\b(?=\s*(?:is my CVV|cvv|security code))'
            ),
            "expiry_no": (
                r'\b(?:exp|expiry|expiration|valid thru|valid until)'
                r'[\s:]*(?:\d{1,2}[/-]\d{2,4})|'
                r'\b(?:0[1-9]|1[0-2])[/-]\d{2,4}\b'
            ),
        }

    @staticmethod
    def mask_text(text: str) -> tuple:
        """
        Find and replace PII spans in `text` with placeholders.
        Returns (masked_text, list_of_entities).
        """
        all_matches = []

        for label, pattern in PIIMasker.patterns().items():
            for match in re.finditer(pattern, text):
                entity_value = None
                start, end = -1, -1

                if label == 'dob':
                    try:
                        entity_value = match.group('dob')
                        start, end = match.span('dob')
                    except IndexError:
                        continue
                else:
                    entity_value = match.group()
                    start, end = match.span()

                if entity_value is not None:
                    all_matches.append({
                        "start": start,
                        "end": end,
                        "classification": label,
                        "entity": entity_value,
                        "length": end - start
                    })

        # spaCy NER for PERSON
        doc = nlp_multi(text)
        for ent in doc.ents:
            if ent.label_ == "PER":  # PERSON
                all_matches.append({
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "classification": "full_name",
                    "entity": ent.text,
                    "length": ent.end_char - ent.start_char
                })

        all_matches.sort(key=lambda x: x["start"])
        f_matches = []
        for mat in all_matches:
            if not any(
                mat["start"] < accept["end"] and mat["end"] > accept["start"]
                for accept in f_matches
            ):
                f_matches.append(mat)

        # Replace from end to start to preserve indices
        updated_text = text
        entities = []
        for mat in sorted(f_matches, key=lambda x: x["start"], reverse=True):
            updated_text = (
                updated_text[:mat["start"]]
                + f"[{mat['classification']}]"
                + updated_text[mat["end"]:]
            )
            entities.append({
                "position": [mat["start"], mat["end"]],
                "classification": mat["classification"],
                "entity": mat["entity"]
            })

        entities.reverse()
        return updated_text, entities


class EmailTranslator:
    """
    Clean encoding and translate text to English.
    """

    @staticmethod
    def clean_encoding(text: str) -> str:
        fixed = fix_text(text)
        return unicodedata.normalize('NFKC', fixed)

    @staticmethod
    def translate_email(text, chunk_size=480):
        text = EmailTranslator.clean_encoding(text)
        langs = detect(text)
        lang = langs.strip().lower()

        if lang == 'en':
            return text

        # Portuguese via DeepTranslator
        try:
            if lang == 'pt':
                chunks = textwrap.wrap(text, chunk_size)
                translated_chunks = []
                for chunk in chunks:
                    try:
                        translated = DeepGoogleTranslator(
                            source='pt', target='en'
                        ).translate(chunk)
                        translated_chunks.append(translated)
                    except Exception:
                        logger.info("Chunk translation failed for Portuguese")
                        translated_chunks.append(chunk)
                return ' '.join(translated_chunks)

            # Other languages via googletrans
            else:
                return Translator().translate(text, dest='en').text

        except Exception:
            logger.info("Translation failed for lang=%s", lang)
            return text
