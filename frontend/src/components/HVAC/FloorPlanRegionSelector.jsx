// frontend/src/components/HVAC/FloorPlanRegionSelector.jsx
import React, { useState, useRef, useMemo } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";

import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url"
pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

export default function FloorPlanRegionSelector({ pdfUrl, selectedPage, onRegionSelected }) {
  const [selection, setSelection] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [startPoint, setStartPoint] = useState(null);
  const canvasRef = useRef(null);

  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setStartPoint({ x, y });
    setSelection({ x, y, width: 0, height: 0 });
    setDragging(true);
  };

  const handleMouseMove = (e) => {
    if (!dragging || !startPoint) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;
    const x = Math.min(startPoint.x, currentX);
    const y = Math.min(startPoint.y, currentY);
    const width = Math.abs(currentX - startPoint.x);
    const height = Math.abs(currentY - startPoint.y);
    setSelection({ x, y, width, height });
  };

  const handleMouseUp = () => {
    setDragging(false);
  };

  const handleConfirm = () => {
    if (selection) {
      onRegionSelected(selection);
    }
  };

  const documentOptions = useMemo(() => ({ disableFontFace: true }), []);

  const fileProps = useMemo(() => ({
    url: pdfUrl,
    httpHeaders: {
      Authorization: `Bearer ${localStorage.getItem("token")}`
    }
  }), [pdfUrl]);

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Select Floor Plan Region</h3>
      {/* Render the selected PDF page */}
      <div className="relative border" style={{ width: "600px" }}>
        <Document
          file={fileProps}
          options={documentOptions}
        >
          <Page pageNumber={selectedPage} width={600} />
        </Document>
        {/* Clickable Canvas Layer for Region Selection */}
        <div
          ref={canvasRef}
          className="absolute top-0 left-0"
          style={{ width: "600px", height: "100%", cursor: "crosshair" }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {selection && (
            <div
              className="absolute border-2 border-[#FF6B6B] bg-[#FF6B6B]/20"
              style={{
                left: `${selection.x}px`,
                top: `${selection.y}px`,
                width: `${selection.width}px`,
                height: `${selection.height}px`,
              }}
            />
          )}
        </div>
      </div>
      <button
        onClick={handleConfirm}
        className="mt-4 bg-[#080653] text-white py-2 px-6 rounded-full font-bold"
        disabled={!selection || selection.width === 0 || selection.height === 0}
      >
        Confirm Region
      </button>
    </div>
  );
}