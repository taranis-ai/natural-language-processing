from natural_language_processing.config import Config
from taranis_base_bot import create_app

app = create_app(Config.PACKAGE_NAME, Config)
