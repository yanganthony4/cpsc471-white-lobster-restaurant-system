from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "3306")
DB_NAME: str = os.getenv("DB_NAME", "wl_restaurant_system")
DB_USER: str = os.getenv("DB_USER", "root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root123")