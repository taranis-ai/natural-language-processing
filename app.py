from flask import Flask
from natural_language_processing.router import init as router_init
from natural_language_processing.nlp import NLPProcessor
from natural_language_processing.config import Config  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        nlp_processor = NLPProcessor()  
        router_init(app, nlp_processor)

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)  
