import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import psycopg2

load_dotenv()
pg_user = os.getenv('POSTGRES_USER')
pg_pass = os.getenv('POSTGRES_PASS')
engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_pass}@localhost/postgres')