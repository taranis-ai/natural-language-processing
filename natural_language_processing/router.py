from flask import Blueprint, jsonify, request
from flask.views import MethodView
from natural_language_processing.predictor import Predictor
from natural_language_processing.decorators import api_key_required, debug_request
from natural_language_processing.predictor_factory import PredictorFactory
from natural_language_processing.config import Config


class NLPHandler(MethodView):
    def __init__(self, processor: Predictor):
        super().__init__()
        self.processor = processor

    @debug_request(Config.DEBUG)
    @api_key_required
    def post(self):
        data = request.get_json()

        # Check if JSON data is a dictionary
        if not isinstance(data, dict):
            return jsonify({"error": "JSON payload must be an object with 'text' field"}), 400

        text = data.get("text", "")
        if not text:
            return jsonify({"error": "No text provided for NER extraction"}), 400
        try:
            return jsonify(self.processor.predict(text, Config.EXT_OUT))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


class HealthCheck(MethodView):
    @debug_request(Config.DEBUG)
    def get(self):
        return jsonify({"status": "ok"})


class ModelInfo(MethodView):
    def __init__(self, processor: Predictor):
        super().__init__()
        self.processor = processor

    @debug_request(Config.DEBUG)
    def get(self):
        return jsonify(self.processor.modelinfo)


def init(app):
    processor = PredictorFactory()
    app.url_map.strict_slashes = False
    ner_bp = Blueprint("ner", __name__)
    ner_bp.add_url_rule("/", view_func=NLPHandler.as_view("ner", processor=processor))
    ner_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
    ner_bp.add_url_rule("/modelinfo", view_func=ModelInfo.as_view("modelinfo", processor=processor))
    app.register_blueprint(ner_bp)
