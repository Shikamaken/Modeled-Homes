import React, { useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loadPdf, renderPage } from '../../utils/pdf';
import { fetchDataRequest, fetchDataSuccess, fetchDataFailure } from '../../reducers/hvacReducer';

const PDFConverter = () => {
  const canvasRef = useRef(null);
  const dispatch = useDispatch();
  const { data, loading, error } = useSelector((state) => state.hvac);
  const [pdf, setPdf] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      dispatch(fetchDataRequest());
      try {
        const url = URL.createObjectURL(file);
        const loadedPdf = await loadPdf(url);
        setPdf(loadedPdf);
        dispatch(fetchDataSuccess([])); // Update with actual data structure
      } catch (error) {
        dispatch(fetchDataFailure(error.message));
      }
    }
  };

  const renderPdfPage = async (pageNumber) => {
    if (pdf && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      await renderPage(pdf, pageNumber, context);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {pdf && (
        <div>
          <canvas ref={canvasRef}></canvas>
          <button onClick={() => renderPdfPage(1)}>Render Page 1</button>
        </div>
      )}
    </div>
  );
};

export default PDFConverter;
