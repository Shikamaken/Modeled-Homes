// frontend/src/components/HVAC/FloorPlanRegionSelectorImage.jsx
import React, { useState, useRef } from "react";

export default function FloorPlanRegionSelectorImage({ imageSrc, originalDimensions, onRegionSelected, pageIndex }) {
  // originalDimensions: { width, height } from the PDF viewport
  const [selection, setSelection] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [startPoint, setStartPoint] = useState(null);
  const containerRef = useRef(null);

  const handleMouseDown = (e) => {
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setStartPoint({ x, y });
    setSelection({ x, y, width: 0, height: 0 });
    setDragging(true);
    // Prevent button clicks from interfering.
    e.stopPropagation();
  };

  const handleMouseMove = (e) => {
    if (!dragging || !startPoint) return;
    const rect = containerRef.current.getBoundingClientRect();
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
    console.log("Mouse Up, final selection:", selection);
  };

  const handleConfirm = () => {
    if (!selection) {
      alert("No selection made.");
      return;
    }
    const container = containerRef.current;
    const displayedWidth = container.clientWidth;
    const displayedHeight = container.clientHeight;
    const scaleX = originalDimensions.width / displayedWidth;
    const scaleY = originalDimensions.height / displayedHeight;
    const mappedSelection = {
      x: selection.x * scaleX,
      y: selection.y * scaleY,
      width: selection.width * scaleX,
      height: selection.height * scaleY,
    };
    // Alert the bounding box and the page index (0-based)
    alert(
      `Bounding Box:\n x: ${mappedSelection.x.toFixed(2)}\n y: ${mappedSelection.y.toFixed(2)}\n width: ${mappedSelection.width.toFixed(2)}\n height: ${mappedSelection.height.toFixed(2)}\n page_index: ${pageIndex}`
    );
    // Pass the data upward if needed.
    onRegionSelected({ region: mappedSelection, pageIndex });
  };

  return (
    <div style={{ position: "relative", display: "inline-block" }} ref={containerRef}>
      <img src={imageSrc} alt="PDF page" style={{ display: "block", maxWidth: "100%" }} />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          cursor: "crosshair",
          zIndex: 1,
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        {selection && (
          <div
            style={{
              position: "absolute",
              border: "2px solid #FF6B6B",
              backgroundColor: "rgba(255, 107, 107, 0.2)",
              left: selection.x,
              top: selection.y,
              width: selection.width,
              height: selection.height,
              pointerEvents: "none", // ensures the overlay doesn't block button clicks
            }}
          />
        )}
      </div>
      {/* Place the confirm button outside (or with higher z-index) so clicks don't interfere with selection */}
      <button
        onClick={handleConfirm}
        disabled={!selection || selection.width === 0 || selection.height === 0}
        style={{
          marginTop: "10px",
          position: "relative",
          zIndex: 10,
        }}
      >
        Confirm Region
      </button>
    </div>
  );
}
