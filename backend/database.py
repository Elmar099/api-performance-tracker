from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///./tests.db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()