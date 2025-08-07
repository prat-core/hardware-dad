import { useEffect, useRef } from 'react';

interface ConnectionWireProps {
  id: string;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  color?: string;
  fromComponent: string;
  toComponent: string;
  fromPin: string;
  toPin: string;
}

export const ConnectionWire = ({
  id,
  startX,
  startY,
  endX,
  endY,
  color = '#22d3ee',
  fromComponent,
  toComponent,
  fromPin,
  toPin,
}: ConnectionWireProps) => {
  const svgRef = useRef<SVGSVGElement>(null);

  // Calculate control points for curved wire
  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;
  const dx = endX - startX;
  const dy = endY - startY;
  const distance = Math.sqrt(dx * dx + dy * dy);
  
  // Add some curve to make it look more like a real wire
  const curvature = Math.min(distance * 0.2, 50);
  const controlX1 = startX + dx * 0.3;
  const controlY1 = startY - curvature;
  const controlX2 = endX - dx * 0.3;
  const controlY2 = endY - curvature;

  const pathData = `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;

  return (
    <svg
      ref={svgRef}
      className="absolute inset-0 pointer-events-none"
      style={{ zIndex: 10 }}
    >
      <defs>
        <filter id={`glow-${id}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Wire shadow/glow */}
      <path
        d={pathData}
        stroke={color}
        strokeWidth="4"
        fill="none"
        opacity="0.3"
        filter={`url(#glow-${id})`}
      />
      
      {/* Main wire */}
      <path
        d={pathData}
        stroke={color}
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      
      {/* Connection points */}
      <circle
        cx={startX}
        cy={startY}
        r="3"
        fill={color}
        stroke="white"
        strokeWidth="1"
      />
      <circle
        cx={endX}
        cy={endY}
        r="3"
        fill={color}
        stroke="white"
        strokeWidth="1"
      />
      
      {/* Wire label (optional) */}
      <text
        x={midX}
        y={midY - 10}
        fontSize="10"
        fill={color}
        textAnchor="middle"
        className="font-mono text-xs"
      >
        {fromPin}→{toPin}
      </text>
    </svg>
  );
};