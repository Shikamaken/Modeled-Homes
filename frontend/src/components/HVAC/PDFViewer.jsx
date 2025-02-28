// frontend/src/components/HVAC/PDFViewer.jsx
import React, { useState } from "react";
import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// ✅ Set worker for proper rendering
pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

export default function PDFViewer({ pdfUrl, onPageSelect }) {
  const [numPages, setNumPages] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);

  const handleLoadSuccess = ({ numPages }) => setNumPages(numPages);

  return (
    <div className="flex flex-col items-center mt-6">
      <Document file={pdfUrl} onLoadSuccess={handleLoadSuccess} loading="Loading PDF...">
        <Page pageNumber={currentPage} />
      </Document>

      {/* Page Navigation */}
      <div className="flex items-center justify-center mt-4 space-x-4">
        <button
          className="p-2 bg-gray-300 rounded"
          disabled={currentPage <= 1}
          onClick={() => setCurrentPage(currentPage - 1)}
        >
          Previous
        </button>
        <span>
          Page {currentPage} of {numPages || "..."}
        </span>
        <button
          className="p-2 bg-gray-300 rounded"
          disabled={currentPage >= numPages}
          onClick={() => setCurrentPage(currentPage + 1)}
        >
          Next
        </button>
      </div>

      {/* Select Current Page */}
      <button
        className="mt-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={() => onPageSelect(currentPage)}
      >
        Select This Page
      </button>
    </div>
  );
}