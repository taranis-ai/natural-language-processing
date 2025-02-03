from flask import Flask
from natural_language_processing import router


def create_app():
    app = Flask(__name__)
    app.config.from_object("natural_language_processing.config.Config")

    with app.app_context():
        router.init(app)

    return app


if __name__ == "__main__":
    create_app().run()
