import yaml
from pathlib import Path

CONFIG_PATH = Path("config.yaml")

def load_config():
    """Loads the YAML configuration file."""
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"'{CONFIG_PATH}' not found. "
            "Please copy 'config.example.yaml' to 'config.yaml' and fill in your details."
        )
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config

# Load config once on module import
config = load_config()
