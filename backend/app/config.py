import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
APP_PORT = int(os.getenv('APP_PORT', '8000'))
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'se1117')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'BX101240es')

SQLALCHEMY_DATABASE_URL = os.getenv(
    'SQLALCHEMY_DATABASE_URL',
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
JWT_SECRET = os.getenv('JWT_SECRET', 'super_secret_jwt_key_123456')
