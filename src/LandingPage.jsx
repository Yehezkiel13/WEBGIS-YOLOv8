// src/LandingPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css'; // Import file CSS yang baru dibuat

function LandingPage() {
  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1 className="landing-title">Sistem Informasi Geografis Terintegrasi AI</h1>
        <p className="landing-subtitle">
          Platform WebGIS interaktif yang mengkombinasikan data spasial konvensional (PostGIS) 
          dengan teknologi deteksi objek otomatis menggunakan Artificial Intelligence (YOLOv8) 
          pada citra satelit area Lampung.
        </p>

        {/* Tombol yang akan mengarahkan ke halaman /map */}
        <Link to="/map" className="btn-masuk-peta">
          Buka Peta Interaktif 🚀
        </Link>

        <div className="features-grid">
          <div className="feature-card">
            <h3>🤖 Deteksi AI YOLOv8</h3>
            <p>Ekstraksi otomatis fitur geografis dari citra satelit.</p>
          </div>
          <div className="feature-card">
            <h3>🗺️ Peta Interaktif</h3>
            <p>Visualisasi data spasial multi-layer menggunakan Leaflet.</p>
          </div>
          <div className="feature-card">
            <h3>🗄️ Spatial Database</h3>
            <p>Penyimpanan dan manajemen data yang solid dengan PostgreSQL & PostGIS.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;