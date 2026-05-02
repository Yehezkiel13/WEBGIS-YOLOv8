from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Fasilitas(Base):
    __tablename__ = "fasilitas_publik"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    deskripsi = Column(String)
    geom = Column(String)  # tetap pakai PostGIS di query