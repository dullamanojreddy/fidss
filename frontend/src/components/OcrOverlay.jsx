import React from "react";

function getBoundingBox(bbox) {
  if (!bbox || bbox.length !== 4) {
    return null;
  }

  const xs = bbox.map((point) => point[0]);
  const ys = bbox.map((point) => point[1]);

  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys);

  return {
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

export default function OcrOverlay({
  imageSrc,
  rawLines = [],
  imageWidth,
  imageHeight,
}) {
  if (!imageSrc) {
    return null;
  }

  return (
    <div
      style={{
        position: "relative",
        display: "inline-block",
        maxWidth: "100%",
      }}
    >
      <img
        src={imageSrc}
        alt="Document"
        style={{
          display: "block",
          maxWidth: "100%",
          height: "auto",
        }}
      />

      <svg
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        preserveAspectRatio="none"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
      >
        {rawLines.map((line, index) => {
          const box = getBoundingBox(line.bbox);

          if (!box) {
            return null;
          }

          return (
            <g key={index}>
              <rect
                x={box.x}
                y={box.y}
                width={box.width}
                height={box.height}
                fill="none"
                stroke="red"
                strokeWidth="2"
              />

              <text
                x={box.x}
                y={Math.max(15, box.y - 4)}
                fontSize="14"
                fill="red"
              >
                {line.text} ({(line.confidence * 100).toFixed(0)}%)
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}