from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse # TAMBAHAN
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
import os # TAMBAHAN

# IMPORT
from schemas import UserCreate, UserLogin, FasilitasCreate, FasilitasUpdate
from auth import create_token

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DATABASE
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "API jalan + DB"}

# =========================
# TEST DB
# =========================
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"message": "Database connected!"}

# =========================
# AUTH - REGISTER
# =========================
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    check = db.execute(
        text("SELECT * FROM users WHERE username = :u"),
        {"u": user.username}
    ).fetchone()

    if check:
        return {"error": "Username sudah digunakan"}

    db.execute(
        text("INSERT INTO users (username, password) VALUES (:u, :p)"),
        {"u": user.username, "p": user.password}
    )
    db.commit()

    return {"message": "Register berhasil"}

# =========================
# AUTH - LOGIN
# =========================
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM users WHERE username = :u AND password = :p"),
        {"u": user.username, "p": user.password}
    ).fetchone()

    if not result:
        return {"error": "Username atau password salah"}

    token = create_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# =========================
# GEOJSON ENDPOINTS
# =========================

# ENDPOINT BARU: HASIL DETEKSI YOLO
@app.get("/hasil-deteksi")
def get_yolo_result():
    # Mengambil file dari folder data/ yang dibuat oleh yolo_pipeline.py
    path = "data/hasil_deteksi.geojson"
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File hasil deteksi belum tersedia. Silakan jalankan yolo_pipeline.py terlebih dahulu."}

# WILAYAH
@app.get("/wilayah-geojson")
def wilayah_geojson(db: Session = Depends(get_db)):
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'id', id,
                        'nama', nama
                    )
                )
            ), '[]'::json)
        )
        FROM wilayah;
    """)
    
    return db.execute(query).scalar()

# JALAN
@app.get("/jalan-geojson")
def jalan_geojson(db: Session = Depends(get_db)):
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'id', id,
                        'nama', nama
                    )
                )
            ), '[]'::json)
        )
        FROM jalan;
    """)
    
    return db.execute(query).scalar()

# FASILITAS (READ)
@app.get("/fasilitas-geojson")
def fasilitas_geojson(db: Session = Depends(get_db)):
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        'id', id,
                        'nama', nama,
                        'jenis', jenis,
                        'alamat', alamat
                    )
                )
            ), '[]'::json)
        )
        FROM fasilitas_publik;
    """)
    
    return db.execute(query).scalar()

# =========================
# CRUD FASILITAS
# =========================

# CREATE
@app.post("/fasilitas")
def tambah_fasilitas(data: FasilitasCreate, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO fasilitas_publik (nama, jenis, alamat, geom)
        VALUES (
            :nama,
            :jenis,
            :alamat,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
        )
    """), {
        "nama": data.nama,
        "jenis": data.jenis,
        "alamat": data.alamat,
        "lat": data.latitude,
        "lng": data.longitude
    })

    db.commit()
    return {"message": "Fasilitas berhasil ditambahkan"}

# UPDATE
@app.put("/fasilitas/{id}")
def update_fasilitas(id: int, data: FasilitasUpdate, db: Session = Depends(get_db)):
    db.execute(text("""
        UPDATE fasilitas_publik
        SET nama=:nama,
            jenis=:jenis,
            alamat=:alamat,
            geom=ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
        WHERE id=:id
    """), {
        "id": id,
        "nama": data.nama,
        "jenis": data.jenis,
        "alamat": data.alamat,
        "lat": data.latitude,
        "lng": data.longitude
    })

    db.commit()
    return {"message": "Fasilitas berhasil diupdate"}

# DELETE
@app.delete("/fasilitas/{id}")
def delete_fasilitas(id: int, db: Session = Depends(get_db)):
    db.execute(
        text("DELETE FROM fasilitas_publik WHERE id=:id"),
        {"id": id}
    )
    db.commit()

    return {"message": "Fasilitas berhasil dihapus"}