// frontend/src/components/HVAC/PDFPageSelectorImage.jsx
import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import axios from "axios";
import PDFPageAsImage from "./PDFPageAsImage";
import FloorPlanRegionSelectorImage from "./FloorPlanRegionSelectorImage";

export default function PDFPageSelectorImage({ uuid, planId, buildingPlan, token, onRegionSelected }) {
  // Polling state for pipeline completion.
  const [pipelineCompleted, setPipelineCompleted] = useState(false);
  const [pdfTimestamp, setPdfTimestamp] = useState(null);
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
      const url = `http://localhost:4000/api/projects/pdf/${uuid}/${encodeURIComponent(
        planId
      )}/${encodeURIComponent(buildingPlan.name)}?t=${pdfTimestamp}&auth=${token}`;
      console.log("Computed pdfUrl:", url);
      return url;
    }
    return "";
  }, [pipelineCompleted, buildingPlan, token, pdfTimestamp, uuid, planId]);

  // State for page selection and image data.
  const [pageNumber, setPageNumber] = useState(1);
  const [imageData, setImageData] = useState(null);

  const handleRendered = useCallback((data) => {
    // data: { dataUrl, viewport, numPages }
    setImageData(data);
  }, []);

  const handlePageChange = (newPage) => {
    setImageData(null); // Reset so that PDFPageAsImage re-renders for the new page.
    setPageNumber(newPage);
  };

  if (!pipelineCompleted) {
    return <p className="mt-4 text-gray-500">⏳ Waiting for pipeline to finish...</p>;
  }

  if (!pdfUrl) {
    return <p className="mt-4 text-gray-500">Preparing PDF...</p>;
  }

  return (
    <div>
      <div style={{ marginBottom: "10px" }}>
        <button disabled={pageNumber <= 1} onClick={() => handlePageChange(pageNumber - 1)}>
          Previous
        </button>
        <span style={{ margin: "0 10px" }}>
          Page {pageNumber} {imageData && imageData.numPages ? `of ${imageData.numPages}` : ""}
        </span>
        <button onClick={() => handlePageChange(pageNumber + 1)}>
          Next
        </button>
      </div>
      {!imageData ? (
        <PDFPageAsImage pdfUrl={pdfUrl} pageNumber={pageNumber} onRendered={handleRendered} />
      ) : (
        <FloorPlanRegionSelectorImage
          imageSrc={imageData.dataUrl}
          originalDimensions={{ width: imageData.viewport.width, height: imageData.viewport.height }}
          pageIndex={pageNumber - 1}  // Convert 1-based to 0-based
          onRegionSelected={onRegionSelected}
        />
      )}
    </div>
  );
}