// frontend/src/components/HVAC/PDFConverter.jsx
import React, { useState } from 'react';
import { loadPdf, renderPage } from '../../utils/pdf';

const PDFConverter = () => {
  const [pdf, setPdf] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      const loadedPdf = await loadPdf(url);
      setPdf(loadedPdf);
    }
  };

  const renderPdf = async (pageNumber) => {
    if (pdf) {
      const canvas = document.getElementById('pdf-canvas');
      const context = canvas.getContext('2d');
      await renderPage(pdf, pageNumber, context);
    }
  };

  return (
    <div>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <canvas id="pdf-canvas" width="600" height="800"></canvas>
      {pdf && (
        <div>
          <button onClick={() => renderPdf(1)}>Render Page 1</button>
          {/* Add more buttons for additional pages as needed */}
        </div>
      )}
    </div>
  );
};

export default PDFConverter;