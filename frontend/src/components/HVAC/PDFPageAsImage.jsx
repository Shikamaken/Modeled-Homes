// frontend/src/components/HVAC/PDFPageAsImage.jsx
import React, { useState, useEffect } from "react";
import * as pdfjsLib from "pdfjs-dist"; 
import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url";

// Set the worker globally
pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc;

export default function PDFPageAsImage({ pdfUrl, pageNumber = 1, scale = 1.5, onRendered }) {
  const [imageSrc, setImageSrc] = useState(null);

  useEffect(() => {
    async function renderPDFPage() {
      try {
        console.log("Loading PDF from:", pdfUrl);
        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(pageNumber);
        const viewport = page.getViewport({ scale });
        const canvas = document.createElement("canvas");
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        const context = canvas.getContext("2d");
        await page.render({ canvasContext: context, viewport }).promise;
        const dataUrl = canvas.toDataURL();
        console.log("PDF page rendered. Data URL length:", dataUrl.length);
        setImageSrc(dataUrl);
        if (onRendered) {
          onRendered({ dataUrl, viewport, numPages: pdf.numPages });
        }
      } catch (error) {
        console.error("Error rendering PDF page:", error);
      }
    }
    renderPDFPage();
  }, [pdfUrl, pageNumber, scale, onRendered]);

  if (!imageSrc) {
    return <p>Loading PDF image…</p>;
  }

  return (
    <img
      src={imageSrc}
      alt={`PDF page ${pageNumber}`}
      style={{ maxWidth: "100%", display: "block" }}
    />
  );
}