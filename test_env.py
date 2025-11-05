from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

# Print database credentials
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
