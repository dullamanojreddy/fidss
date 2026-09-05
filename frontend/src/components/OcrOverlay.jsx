import React, { useState } from "react";
import { Eye, EyeOff, Sparkles } from "lucide-react";

function getBoundingBox(bbox) {
  if (!bbox) return null;

  // Case 1: 4-point array [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
  if (Array.isArray(bbox) && bbox.length === 4 && Array.isArray(bbox[0])) {
    const xs = bbox.map((p) => p[0]);
    const ys = bbox.map((p) => p[1]);

    const minX = Math.min(...xs);
    const minY = Math.min(...ys);
    const maxX = Math.max(...xs);
    const maxY = Math.max(...ys);

    return {
      x: minX,
      y: minY,
      width: Math.max(1, maxX - minX),
      height: Math.max(1, maxY - minY),
    };
  }

  // Case 2: Object {x, y, width, height}
  if (typeof bbox === "object" && "x" in bbox && "y" in bbox) {
    return {
      x: bbox.x,
      y: bbox.y,
      width: bbox.width || 10,
      height: bbox.height || 10,
    };
  }

  return null;
}

function getConfidenceStyle(confidence = 1.0) {
  if (confidence >= 0.9) {
    return {
      stroke: "#10b981", // Emerald
      fill: "rgba(16, 185, 129, 0.12)",
      textBg: "bg-emerald-600",
      label: "High Confidence",
    };
  }
  if (confidence >= 0.75) {
    return {
      stroke: "#f59e0b", // Amber
      fill: "rgba(245, 158, 11, 0.15)",
      textBg: "bg-amber-600",
      label: "Moderate Confidence",
    };
  }
  return {
    stroke: "#ef4444", // Rose
    fill: "rgba(239, 68, 68, 0.18)",
    textBg: "bg-rose-600",
    label: "Low Confidence",
  };
}

export default function OcrOverlay({
  imageSrc,
  rawLines = [],
  imageWidth,
  imageHeight,
}) {
  const [showOverlay, setShowOverlay] = useState(true);
  const [hoveredLine, setHoveredLine] = useState(null);
  const [naturalDimensions, setNaturalDimensions] = useState({
    width: imageWidth || 1000,
    height: imageHeight || 700,
  });

  if (!imageSrc) {
    return null;
  }

  const handleImageLoad = (e) => {
    if (e.target.naturalWidth && e.target.naturalHeight) {
      setNaturalDimensions({
        width: e.target.naturalWidth,
        height: e.target.naturalHeight,
      });
    }
  };

  const viewBoxWidth = imageWidth || naturalDimensions.width;
  const viewBoxHeight = imageHeight || naturalDimensions.height;

  return (
    <div className="relative inline-block w-full max-w-full group">
      {/* Control Bar */}
      {rawLines.length > 0 && (
        <div className="absolute top-2 right-2 z-20 flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-full border border-slate-700/50 shadow-md text-xs text-white">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-[11px] font-medium text-slate-300">
            {rawLines.length} OCR {rawLines.length === 1 ? "zone" : "zones"}
          </span>
          <button
            type="button"
            onClick={() => setShowOverlay(!showOverlay)}
            className="ml-1 text-slate-300 hover:text-white transition flex items-center gap-1 bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded-full"
            title={showOverlay ? "Hide OCR bounding boxes" : "Show OCR bounding boxes"}
          >
            {showOverlay ? (
              <>
                <EyeOff className="w-3 h-3 text-slate-400" />
                <span className="text-[10px]">Hide</span>
              </>
            ) : (
              <>
                <Eye className="w-3 h-3 text-blue-400" />
                <span className="text-[10px]">Show</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Main Document Image */}
      <img
        src={imageSrc}
        alt="Document Preview"
        onLoad={handleImageLoad}
        className="block max-w-full h-auto rounded-lg shadow-inner mx-auto"
      />

      {/* OCR SVG Overlay */}
      {showOverlay && (
        <svg
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          preserveAspectRatio="none"
          className="absolute top-0 left-0 w-full h-full pointer-events-auto rounded-lg"
        >
          {rawLines.map((line, index) => {
            const box = getBoundingBox(line.bbox);
            if (!box) return null;

            const isHovered = hoveredLine === index;
            const style = getConfidenceStyle(line.confidence);

            return (
              <g
                key={index}
                className="cursor-pointer transition-all duration-150"
                onMouseEnter={() => setHoveredLine(index)}
                onMouseLeave={() => setHoveredLine(null)}
              >
                <rect
                  x={box.x}
                  y={box.y}
                  width={box.width}
                  height={box.height}
                  fill={isHovered ? "rgba(59, 130, 246, 0.25)" : style.fill}
                  stroke={isHovered ? "#2563eb" : style.stroke}
                  strokeWidth={isHovered ? "3" : "1.75"}
                  strokeDasharray={line.confidence < 0.75 ? "4 2" : "none"}
                  rx="3"
                  ry="3"
                />
              </g>
            );
          })}
        </svg>
      )}

      {/* Interactive Hover Tooltip */}
      {showOverlay && hoveredLine !== null && rawLines[hoveredLine] && (
        <div className="absolute bottom-3 left-3 right-3 z-30 bg-slate-900/95 backdrop-blur-md text-white px-3 py-2 rounded-lg border border-slate-700 shadow-xl flex items-center justify-between pointer-events-none transition-all">
          <div className="flex items-center gap-2 overflow-hidden">
            <span
              className={`w-2 h-2 rounded-full ${
                rawLines[hoveredLine].confidence >= 0.9
                  ? "bg-emerald-400"
                  : rawLines[hoveredLine].confidence >= 0.75
                  ? "bg-amber-400"
                  : "bg-rose-400"
              }`}
            />
            <span className="text-xs font-mono text-slate-100 truncate">
              "{rawLines[hoveredLine].text}"
            </span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-[11px] text-slate-400">Confidence:</span>
            <span
              className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                getConfidenceStyle(rawLines[hoveredLine].confidence).textBg
              }`}
            >
              {(rawLines[hoveredLine].confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}