from pydantic import BaseModel

# =====================
# USER
# =====================
class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# =====================
# FASILITAS
# =====================
class FasilitasCreate(BaseModel):
    nama: str
    jenis: str
    alamat: str
    latitude: float
    longitude: float


class FasilitasUpdate(BaseModel):
    nama: str
    jenis: str
    alamat: str
    latitude: float
    longitude: float