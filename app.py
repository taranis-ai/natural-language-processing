from natural_language_processing.config import Config
import taranis_base_bot.config as base_config

base_config.Config = Config


from taranis_base_bot import create_app

app = create_app(Config.PACKAGE_NAME, Config)
