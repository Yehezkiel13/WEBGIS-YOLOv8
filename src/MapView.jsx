import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Marker,
  Popup,
  LayersControl,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const API_BASE = "http://127.0.0.1:8000";

function FitBoundsSemua({ wilayah, jalan, fasilitas, deteksi }) {
  const map = useMap();

  useEffect(() => {
    const group = L.featureGroup();

    if (wilayah?.features?.length) group.addLayer(L.geoJSON(wilayah));
    if (jalan?.features?.length) group.addLayer(L.geoJSON(jalan));
    if (fasilitas?.features?.length) group.addLayer(L.geoJSON(fasilitas));
    if (deteksi?.features?.length) group.addLayer(L.geoJSON(deteksi));

    const bounds = group.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [wilayah, jalan, fasilitas, deteksi, map]);

  return null;
}

function Legend({ wilayah, jalan, fasilitas, deteksi }) {
  return (
    <div
      style={{
        position: "absolute",
        top: 10,
        right: 10,
        zIndex: 1000,
        background: "white",
        padding: "10px 12px",
        borderRadius: "8px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
        fontSize: "14px",
        lineHeight: "1.6",
        minWidth: "220px",
      }}
    >
      <b>Legenda</b>
      <div><span style={{ color: "#1B5E20" }}>■</span> Wilayah</div>
      <div><span style={{ color: "#D84315" }}>■</span> Jalan</div>
      <div><span style={{ color: "red" }}>●</span> Rumah Sakit / Puskesmas</div>
      <div><span style={{ color: "green" }}>●</span> Sekolah / Kampus</div>
      <div><span style={{ color: "orange" }}>●</span> Kantor</div>
      <div><span style={{ color: "blue" }}>●</span> Lainnya</div>
      <div><span style={{ color: "#E91E63" }}>▣</span> Deteksi AI (YOLO)</div>

      <hr />
      <div><b>Debug</b></div>
      <div>Wilayah: {wilayah?.features?.length ?? 0}</div>
      <div>Jalan: {jalan?.features?.length ?? 0}</div>
      <div>Fasilitas: {fasilitas?.features?.length ?? 0}</div>
      <div>Deteksi AI: {deteksi?.features?.length ?? 0}</div>
    </div>
  );
}

export default function MapView() {
  const [wilayah, setWilayah] = useState(null);
  const [jalan, setJalan] = useState(null);
  const [fasilitas, setFasilitas] = useState(null);
  const [deteksi, setDeteksi] = useState(null); // ⬅ STATE BARU
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [wilayahRes, jalanRes, fasilitasRes, deteksiRes] =
          await Promise.all([
            fetch(`${API_BASE}/wilayah-geojson`),
            fetch(`${API_BASE}/jalan-geojson`),
            fetch(`${API_BASE}/fasilitas-geojson`),
            fetch(`${API_BASE}/hasil-deteksi`), // ⬅ ENDPOINT BARU
          ]);

        if (!wilayahRes.ok || !jalanRes.ok || !fasilitasRes.ok) {
          throw new Error("Gagal mengambil data dari API");
        }

        const wilayahData = await wilayahRes.json();
        const jalanData = await jalanRes.json();
        const fasilitasData = await fasilitasRes.json();

        // Deteksi AI bersifat opsional — kalau gagal, peta tetap jalan
        let deteksiData = null;
        if (deteksiRes.ok) {
          deteksiData = await deteksiRes.json();
          // Cek kalau response-nya pesan error dari FastAPI (bukan GeoJSON)
          if (deteksiData?.error) {
            console.warn("Deteksi AI:", deteksiData.error);
            deteksiData = null;
          }
        }

        console.log("Wilayah:", wilayahData);
        console.log("Jalan:", jalanData);
        console.log("Fasilitas:", fasilitasData);
        console.log("Deteksi AI:", deteksiData);

        setWilayah(wilayahData);
        setJalan(jalanData);
        setFasilitas(fasilitasData);
        setDeteksi(deteksiData);
      } catch (error) {
        console.error("Gagal fetch data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const wilayahStyle = {
    color: "#1B5E20",
    weight: 4,
    fillColor: "#4CAF50",
    fillOpacity: 0.6,
  };

  const jalanStyle = {
    color: "#D84315",
    weight: 6,
  };

  // ⬅ STYLE BARU UNTUK HASIL DETEKSI YOLO
  const deteksiStyle = {
    color: "#E91E63",
    weight: 2,
    fillColor: "#F06292",
    fillOpacity: 0.35,
    dashArray: "4, 4",
  };

  function getFasilitasIcon(jenis) {
    let color = "blue";
    const jenisLower = (jenis || "").toLowerCase();

    if (jenisLower.includes("rumah sakit") || jenisLower.includes("puskesmas")) {
      color = "red";
    } else if (jenisLower.includes("sekolah") || jenisLower.includes("kampus")) {
      color = "green";
    } else if (jenisLower.includes("kantor")) {
      color = "orange";
    }

    return L.divIcon({
      className: "custom-div-icon",
      html: `
        <div style="
          background:${color};
          width:20px;
          height:20px;
          border-radius:50%;
          border:3px solid white;
          box-shadow:0 0 8px rgba(0,0,0,0.6);
        "></div>
      `,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });
  }

  function onEachWilayah(feature, layer) {
    const props = feature.properties || {};
    layer.bindPopup(`
      <div>
        <b>Data Wilayah</b><br/>
        ID: ${props.id ?? "-"}<br/>
        Nama: ${props.nama ?? "-"}
      </div>
    `);
    layer.on({
      mouseover: (e) => e.target.setStyle({ weight: 6, fillOpacity: 0.85 }),
      mouseout: (e) => e.target.setStyle(wilayahStyle),
      click: (e) => e.target._map.fitBounds(e.target.getBounds()),
    });
  }

  function onEachJalan(feature, layer) {
    const props = feature.properties || {};
    layer.bindPopup(`
      <div>
        <b>Data Jalan</b><br/>
        ID: ${props.id ?? "-"}<br/>
        Nama: ${props.nama ?? "-"}
      </div>
    `);
    layer.on({
      mouseover: (e) => e.target.setStyle({ weight: 8, color: "#FF5722" }),
      mouseout: (e) => e.target.setStyle(jalanStyle),
    });
  }

  // ⬅ HANDLER BARU UNTUK FITUR DETEKSI AI
  function onEachDeteksi(feature, layer) {
    const props = feature.properties || {};
    // SESUAIKAN nama field di bawah ini setelah cek file GeoJSON Anda
    const kelas = props.class ?? props.class_name ?? props.label ?? "Objek";
    const conf = props.confidence ?? props.score ?? props.conf;
    const confText =
      typeof conf === "number" ? `${(conf * 100).toFixed(1)}%` : "N/A";

    layer.bindPopup(`
      <div>
        <b>🤖 Hasil Deteksi AI</b><br/>
        Kelas: <b>${kelas}</b><br/>
        Confidence: ${confText}
      </div>
    `);

    layer.on({
      mouseover: (e) =>
        e.target.setStyle({ weight: 4, fillOpacity: 0.6, dashArray: "" }),
      mouseout: (e) => e.target.setStyle(deteksiStyle),
    });
  }

  if (loading) {
    return <p style={{ padding: "16px" }}>Memuat peta...</p>;
  }

  return (
    <div style={{ height: "100vh", width: "100%", position: "relative" }}>
      <Legend
        wilayah={wilayah}
        jalan={jalan}
        fasilitas={fasilitas}
        deteksi={deteksi}
      />

      <MapContainer
        center={[-5.36, 105.31]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <LayersControl position="topleft">
          {/* Base map: bisa pilih OSM atau Satellite */}
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="Citra Satelit (Esri)">
            <TileLayer
              attribution="Tiles &copy; Esri"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          {/* Overlay layers — bisa di-toggle on/off */}
          <LayersControl.Overlay checked name="Wilayah">
            <GeoJSON
              data={wilayah || { type: "FeatureCollection", features: [] }}
              style={() => wilayahStyle}
              onEachFeature={onEachWilayah}
            />
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Jalan">
            <GeoJSON
              data={jalan || { type: "FeatureCollection", features: [] }}
              style={() => jalanStyle}
              onEachFeature={onEachJalan}
            />
          </LayersControl.Overlay>

          {deteksi && (
            <LayersControl.Overlay checked name="🤖 Deteksi AI (YOLO)">
              <GeoJSON
                data={deteksi}
                style={() => deteksiStyle}
                onEachFeature={onEachDeteksi}
              />
            </LayersControl.Overlay>
          )}
        </LayersControl>

        <FitBoundsSemua
          wilayah={wilayah}
          jalan={jalan}
          fasilitas={fasilitas}
          deteksi={deteksi}
        />

        {/* Marker fasilitas tetap di luar LayersControl agar styling icon-nya konsisten */}
        {fasilitas &&
          fasilitas.features?.map((feature, index) => {
            const coords = feature.geometry?.coordinates;
            const props = feature.properties || {};
            if (!coords || coords.length < 2) return null;
            const [lng, lat] = coords;

            return (
              <Marker
                key={index}
                position={[lat, lng]}
                icon={getFasilitasIcon(props.jenis)}
                eventHandlers={{
                  click: (e) => e.target._map.flyTo([lat, lng], 17),
                }}
              >
                <Popup>
                  <div>
                    <b>Fasilitas Publik</b><br />
                    ID: {props.id ?? "-"}<br />
                    Nama: {props.nama ?? "-"}<br />
                    Jenis: {props.jenis ?? "-"}<br />
                    Alamat: {props.alamat ?? "-"}
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>
    </div>
  );
}