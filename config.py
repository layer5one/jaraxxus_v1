import os
from dotenv import load_dotenv

# Load environment variables from a .env file for sensitive data
load_dotenv()

class Config:
    """
    Application-level configuration.
    """
    # General App Settings
    APP_NAME = "Jaraxxus AI Supervisor"
    APP_VERSION = "2.0.0"
    LOG_LEVEL = "INFO"

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, 'jaraxxus_config.json')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

    # API Keys (loaded from environment variables)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # GUI Settings
    WINDOW_TITLE = "Jaraxxus Supervisor"
    WINDOW_GEOMETRY = "1200x800"

# Create a single instance of the configuration to be imported by other modules
config = Config()
