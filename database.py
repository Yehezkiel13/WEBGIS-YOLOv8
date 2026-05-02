from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:admin123@127.0.0.1:5433/SIG_122140233"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)