import os
import rasterio
from rasterio.windows import Window
from ultralytics import YOLO
import geopandas as gpd
from shapely.geometry import Polygon


# Kelas COCO yang masuk akal untuk citra satelit / aerial view
# Anda bisa edit list ini sesuai kebutuhan
KELAS_RELEVAN_AERIAL = {
    "car",
    "truck",
    "bus",
    "boat",
    "airplane",
    "motorcycle",
    "bicycle",
}


def run_detection(
    image_path,
    output_geojson="data/hasil_deteksi.geojson",
    model_path="yolov8n.pt",
    conf_threshold=0.25,
    tile_size=640,
    filter_kelas=True,
):
    """
    Menjalankan deteksi objek pada citra satelit dan menyimpan hasilnya ke GeoJSON.

    Parameters
    ----------
    image_path : str
        Path ke file citra .tif yang sudah di-georeferencing.
    output_geojson : str
        Path file output GeoJSON.
    model_path : str
        Path ke file weights YOLO (.pt).
    conf_threshold : float
        Ambang batas confidence (0.0 - 1.0).
    tile_size : int
        Ukuran tile untuk inference (default 640, sesuai input YOLO).
    filter_kelas : bool
        Jika True, hanya simpan deteksi yang ada di KELAS_RELEVAN_AERIAL.
    """

    # =========================================================
    # 1. VALIDASI & SETUP
    # =========================================================
    os.makedirs(os.path.dirname(output_geojson) or ".", exist_ok=True)

    if not os.path.exists(image_path):
        print(f"❌ Error: File '{image_path}' tidak ditemukan!")
        return

    print(f"📦 Memuat model YOLO: {model_path}")
    model = YOLO(model_path)

    geometries = []
    labels = []
    confidences = []

    # =========================================================
    # 2. BACA CITRA SATELIT
    # =========================================================
    print(f"🛰️  Membaca citra satelit: {image_path}")

    with rasterio.open(image_path) as src:
        print(f"   - Dimensi   : {src.width} x {src.height} px")
        print(f"   - CRS asli  : {src.crs}")
        print(f"   - Bands     : {src.count}")

        if src.crs is None:
            print("❌ Error: Citra tidak punya CRS! Pastikan sudah di-georeferencing di QGIS.")
            return

        total_tiles = (
            ((src.height + tile_size - 1) // tile_size)
            * ((src.width + tile_size - 1) // tile_size)
        )
        tile_count = 0

        # =====================================================
        # 3. SLIDING WINDOW: PROSES PER-TILE
        # =====================================================
        for y in range(0, src.height, tile_size):
            for x in range(0, src.width, tile_size):
                tile_count += 1

                # Definisikan window dengan ukuran aman (tidak melebihi tepi citra)
                w = min(tile_size, src.width - x)
                h = min(tile_size, src.height - y)
                window = Window(x, y, w, h)

                # Baca tile dari raster
                img_tile = src.read(window=window)

                # Format rasterio: (bands, H, W) → format gambar: (H, W, bands)
                img_tile = img_tile.transpose(1, 2, 0)

                # Buang channel alpha jika ada (RGBA → RGB)
                if img_tile.shape[2] == 4:
                    img_tile = img_tile[:, :, :3]
                # Kalau cuma 1 band (grayscale), skip — YOLO butuh 3 channel
                elif img_tile.shape[2] == 1:
                    continue

                # ============================================
                # 4. INFERENCE YOLO
                # ============================================
                results = model.predict(
                    source=img_tile,
                    conf=conf_threshold,
                    verbose=False,
                )

                for result in results:
                    boxes = result.boxes
                    if boxes is None or len(boxes) == 0:
                        continue

                    for box in boxes:
                        # Koordinat bbox dalam pixel TILE
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        label_name = model.names[cls_id]

                        # Filter kelas (kalau diaktifkan)
                        if filter_kelas and label_name not in KELAS_RELEVAN_AERIAL:
                            continue

                        # ====================================
                        # 5. PIXEL → KOORDINAT GEOGRAFIS
                        # ====================================
                        # Konversi koordinat tile → koordinat global citra
                        gx1, gy1 = x + x1, y + y1  # top-left
                        gx2, gy2 = x + x2, y + y2  # bottom-right

                        # Pakai src.xy(row, col) — perhatikan urutannya: ROW dulu, baru COL
                        # Hasilnya (X, Y) dalam CRS asli citra
                        x_min, y_max = src.xy(gy1, gx1)  # top-left  → (x kiri, y atas)
                        x_max, y_min = src.xy(gy2, gx2)  # bot-right → (x kanan, y bawah)

                        # Bikin polygon (urut counter-clockwise agar valid)
                        poly = Polygon([
                            (x_min, y_min),  # bottom-left
                            (x_max, y_min),  # bottom-right
                            (x_max, y_max),  # top-right
                            (x_min, y_max),  # top-left
                            (x_min, y_min),  # close ring
                        ])

                        geometries.append(poly)
                        labels.append(label_name)
                        confidences.append(round(conf, 4))

            # Progress sederhana per-row tile
            print(f"   - Progress tile: {tile_count}/{total_tiles}", end="\r")

        print()  # newline setelah progress

        # =====================================================
        # 6. SIMPAN GEOJSON
        # =====================================================
        if not geometries:
            print("⚠️  Tidak ada objek terdeteksi.")
            print("   Tips: turunkan conf_threshold, atau matikan filter_kelas,")
            print("   atau cek apakah citra punya objek yg dikenali model COCO.")
            return

        gdf = gpd.GeoDataFrame(
            {
                "label": labels,
                "confidence": confidences,
                "geometry": geometries,
            },
            crs=src.crs,
        )

        # Konversi ke EPSG:4326 (WGS84) — standar untuk web maps (Leaflet)
        gdf = gdf.to_crs(epsg=4326)

        # Hapus file lama kalau ada (driver GeoJSON kadang tidak overwrite)
        if os.path.exists(output_geojson):
            os.remove(output_geojson)

        gdf.to_file(output_geojson, driver="GeoJSON")

        # Statistik ringkas per kelas
        print(f"✅ Berhasil! {len(geometries)} objek disimpan ke '{output_geojson}'")
        print("   Distribusi kelas:")
        for kelas, count in gdf["label"].value_counts().items():
            print(f"     - {kelas:12s} : {count}")


if __name__ == "__main__":
    run_detection(
        image_path="citra_saya.tif",
        output_geojson="data/hasil_deteksi.geojson",
        conf_threshold=0.25,
        filter_kelas=True,  # ganti False kalau ingin lihat SEMUA deteksi (untuk debugging)
    )