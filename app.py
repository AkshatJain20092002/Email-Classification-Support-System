from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import EmailTranslator, PIIMasker
from models import EmailClassifier
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/classify", methods=["POST"])
def classify_email():
    """
    Endpoint to classify an email: masks PII, translates, and predicts.
    """
    if request.content_type != "application/json":
        return (
            jsonify({"error": "Content-Type must be application/json"}),
            415,
        )

    try:
        data = request.get_json()
        email_body = data.get("email_body", "")

        if not email_body:
            return (
                jsonify({
                    "error": "Missing fields",
                    "missing_parameters": ["email_body"],
                }),
                400,
            )

        masker = PIIMasker()
        translator = EmailTranslator()
        classifier = EmailClassifier()

        masked_text, entities = masker.mask_text(email_body)
        logger.info("Masked text: %s", masked_text)
        translated_text = translator.translate_email(masked_text)
        logger.info("Translated text: %s", translated_text)
        category = classifier.predict(translated_text)
        logger.info("Predicted category: %s", category)

        return jsonify({
            "input_email_body": email_body,
            "list_of_masked_entities": entities,
            "masked_email": masked_text,
            "category_of_the_email": category,
        })

    except ValueError as exc:
        logger.error("ValueError: %s", exc)
        return jsonify({"error": str(exc)}), 400

    except Exception as exc:
        logger.error("Error in /classify: %s", exc)
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
