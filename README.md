# WebGIS Terintegrasi Deteksi Objek AI (YOLOv8)

Proyek ini adalah Sistem Informasi Geografis (SIG) berbasis Web yang mengintegrasikan deteksi objek AI menggunakan model YOLOv8 dengan tampilan peta interaktif. Sistem ini tidak hanya menampilkan data spasial konvensional dari database, tetapi juga mampu memproses citra udara/satelit, melakukan deteksi objek, dan memetakannya secara otomatis ke dalam koordinat geografis nyata.

## Fitur Utama

- **Deteksi Objek AI (YOLOv8):** Menggunakan model `yolov8n.pt` (*pretrained*) untuk mendeteksi objek pada citra satelit.
- **Image Tiling & Geospatial Processing:** Implementasi teknik *sliding window* (640px) pada citra berukuran besar (Orthophoto/Satelit) agar dapat diproses oleh AI.
- **Auto-Georeferencing:** Konversi otomatis hasil deteksi *bounding box* (piksel) menjadi poligon koordinat geografis (EPSG:4326) menggunakan `rasterio` dan mengekspornya ke format GeoJSON.
- **PostGIS Integration:** Menampilkan layer vektor konvensional (Wilayah, Jalan, Fasilitas Publik) yang ditarik langsung dari database spatial PostgreSQL/PostGIS.
- **Interactive WebGIS:** Dibangun menggunakan React + Leaflet dengan fitur *Layers Control* (toggle layer), *Custom Markers*, pop-up informasi, dan *Basemap toggle* (OSM & Esri Satellite).

## Stack Teknologi

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL + PostGIS, Uvicorn  
- **AI & Geospatial:** YOLOv8 (Ultralytics), Rasterio, GeoPandas, Shapely  
- **Frontend:** React 18 (Vite), react-leaflet v4, Leaflet  
- **GIS Tools:** QGIS (untuk *Georeferencing* awal citra)

## Struktur Direktori

```text
sig-api/
├── data/
│   └── hasil_deteksi.geojson   # Output hasil deteksi YOLO
├── image/                      # Folder tempat menyimpan gambar dokumentasi (.png)
│   ├── 1.png
│   ├── 2.png
│   └── 3.png
├── src/                        # Source code React Frontend
│   ├── App.jsx
│   ├── main.jsx
│   ├── LandingPage.jsx         # Tampilan awal Website
│   ├── LandingPage.css         # Styling tampilan awal
│   └── MapView.jsx             # Komponen peta utama
├── main.py                     # Entry point FastAPI backend
├── database.py                 # Koneksi PostgreSQL
├── auth.py                     # Sistem autentikasi (JWT)
├── schemas.py                  # Pydantic models
├── yolo_pipeline.py            # Script AI & Image Tiling
├── citra_saya.tif              # Citra input yang sudah di-georeferencing (EPSG:4326)
├── yolov8n.pt                  # Pretrained weights model YOLO
├── package.json                # Dependencies React
└── index.html                  # Entry point Vite
```
📸 Screenshot Hasil
1. Tampilan Awal (Landing Page)

Penjelasan:
Halaman awal (Landing Page) aplikasi WebGIS yang berfungsi sebagai gerbang masuk pengguna. Menampilkan judul sistem, deskripsi teknologi yang digunakan (YOLOv8, Leaflet, PostGIS), serta tombol navigasi utama untuk menuju peta interaktif.

2. Hasil Deteksi Objek AI (YOLOv8)

Penjelasan:
Visualisasi hasil deteksi objek otomatis pada peta. Poligon berwarna merah muda dengan garis putus-putus merupakan hasil konversi bounding box dari AI menjadi data spasial. Setiap objek dapat diklik untuk menampilkan informasi seperti jenis objek dan tingkat kepercayaan model.

3. Integrasi Layer Spasial Konvensional (PostGIS)

Penjelasan:
Menampilkan integrasi data spasial dari database PostGIS, seperti:

Jalan (garis oranye)
Wilayah (poligon hijau)
Fasilitas publik (marker titik)

Terdapat juga panel legenda untuk keterangan simbol serta panel debug untuk memantau status data dari server secara real-time.
