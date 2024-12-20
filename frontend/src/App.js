import React from 'react';
import { Routes, Route } from 'react-router-dom';
import PDFConverter from './components/HVAC/PDFConverter';
import AirflowAnimation from './components/HVAC/AirflowAnimation';
import ARViewer from './components/HVAC/ARViewer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/pdf-converter" element={<PDFConverter />} />
        <Route path="/airflow-animation" element={<AirflowAnimation />} />
        <Route path="/ar-viewer" element={<ARViewer />} />
      </Routes>
    </div>
  );
}

export default App;
