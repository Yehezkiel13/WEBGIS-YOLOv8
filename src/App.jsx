import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./LandingPage";
import MapView from "./MapView";

function App() {
  return (
    <Router>
      <main>
        <Routes>
          {/* Rute untuk halaman awal (saat web pertama kali dibuka) */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Rute untuk halaman peta */}
          <Route path="/map" element={<MapView />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;