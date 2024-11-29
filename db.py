import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

load_dotenv()
pg_user = os.getenv('POSTGRES_USER')
pg_pass = os.getenv('POSTGRES_PASS')

engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_pass}@localhost/postgres', echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        print("Session created")
        yield session


