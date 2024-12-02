from flask import Blueprint, jsonify, request
from flask.views import MethodView
from natural_language_processing.nlp import NLPProcessor

class NLPHandler(MethodView):
    def __init__(self, processor: NLPProcessor):
        super().__init__()
        self.processor = processor

    def post(self):
        data = request.get_json()
        text = data.get("text", "")
        language = data.get("language", "en")
        if not text:
            return jsonify({"error": "No text provided for NER extraction"}), 400
        try:
            keywords = self.processor.predict(text, language)
            return jsonify({"keywords": keywords})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
def init(app, nlp_processor):
    app.url_map.strict_slashes = False
    ner_bp = Blueprint("ner", __name__)
    ner_bp.add_url_rule("/", view_func=NLPHandler.as_view("ner", processor=nlp_processor))
    app.register_blueprint(ner_bp)