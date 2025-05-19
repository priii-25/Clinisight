import psycopg2
from app.config import Config

def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)