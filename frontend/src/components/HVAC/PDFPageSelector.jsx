// frontend/src/components/HVAC/PDFPageSelector.jsx
import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import axios from "axios";
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import FloorPlanRegionSelector from "./FloorPlanRegionSelector";
// Bundle the worker using the ?url suffix so webpack handles it.
import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url";

pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

export default function PDFPageSelector({ uuid, planId, buildingPlan, token, onPagesSelected }) {
  // Local state for polling and PDF display
  const [pipelineCompleted, setPipelineCompleted] = useState(false);
  const [pdfTimestamp, setPdfTimestamp] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [selectedPage, setSelectedPage] = useState(null);
  const [confirmed, setConfirmed] = useState(false);

  // Refs to ensure we update state only once after completion.
  const pollingRef = useRef(null);
  const updateDoneRef = useRef(false);

  const checkPipelineStatus = useCallback(async () => {
    try {
      const response = await axios.get(
        `http://localhost:4000/api/pipeline/status?uuid=${uuid}&plan_id=${encodeURIComponent(planId)}`
      );
      if (response.data.status === "success") {
        if (!updateDoneRef.current) {
          setPipelineCompleted(true);
          setPdfTimestamp(Date.now());
          updateDoneRef.current = true;
          console.log("✅ Pipeline complete!");
        }
      } else {
        console.log("⏳ Pipeline still processing...");
        pollingRef.current = setTimeout(checkPipelineStatus, 5000);
      }
    } catch (err) {
      console.error("❌ Error checking pipeline status:", err);
      pollingRef.current = setTimeout(checkPipelineStatus, 5000);
    }
  }, [uuid, planId]);

  useEffect(() => {
    checkPipelineStatus();
    return () => {
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, [checkPipelineStatus]);

  // Compute the PDF URL once the pipeline is complete.
  const pdfUrl = useMemo(() => {
    if (pipelineCompleted && buildingPlan && token && pdfTimestamp) {
      return `http://localhost:4000/api/projects/pdf/${uuid}/${encodeURIComponent(
        planId
      )}/${encodeURIComponent(buildingPlan.name)}?t=${pdfTimestamp}&auth=${token}`;
    }
    return "";
  }, [pipelineCompleted, buildingPlan, token, pdfTimestamp, uuid, planId]);

  const onDocumentLoadSuccess = useCallback(({ numPages }) => {
    setNumPages(numPages);
    console.log("✅ PDF loaded successfully with", numPages, "pages.");
  }, []);

  const handleConfirm = useCallback(() => {
    onPagesSelected(selectedPage);
    setConfirmed(true);
  }, [onPagesSelected, selectedPage]);

  // Memoize the Document options and file props to stabilize the PDF component.
  const documentOptions = useMemo(() => ({ disableFontFace: true }), []);
  const fileProps = useMemo(() => ({
    url: pdfUrl,
    httpHeaders: {
      Authorization: `Bearer ${token}`,
    },
  }), [pdfUrl, token]);

  return (
    <div className="mt-4">
      { !pipelineCompleted ? (
        <p className="mt-4 text-gray-500">⏳ Waiting for pipeline to finish...</p>
      ) : (
        <>
          <h3 className="text-lg font-semibold mb-2">Select the Floor Plan Page</h3>
          {pdfUrl && (
            <>
              <Document
                file={fileProps}
                options={documentOptions}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={(error) => console.error("❌ Error loading PDF:", error)}
              >
                <Page pageNumber={1} width={400} />
              </Document>
              <div>
                {numPages &&
                  Array.from({ length: numPages }, (_, index) => (
                    <div
                      key={index}
                      className={`cursor-pointer my-2 p-2 border rounded-lg ${
                        selectedPage === index + 1 ? "bg-[#FF6B6B] text-white" : "hover:bg-gray-200"
                      }`}
                      onClick={() => setSelectedPage(index + 1)}
                    >
                      Page {index + 1}
                    </div>
                  ))}
              </div>
            </>
          )}
          <button
            onClick={handleConfirm}
            className="mt-4 bg-[#080653] text-white py-2 px-6 rounded-full font-bold"
            disabled={!selectedPage}
          >
            Confirm Selection
          </button>
          {confirmed && (
            <FloorPlanRegionSelector
              pdfUrl={pdfUrl}
              selectedPage={selectedPage}
              onRegionSelected={(region) => console.log("🛠 Selected Region:", region)}
            />
          )}
        </>
      )}
    </div>
  );
}