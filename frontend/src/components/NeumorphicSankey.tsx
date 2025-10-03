'use client';

import React, { useRef, useEffect, useMemo } from 'react';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';

type Node = {
  name: string;
  nodeColor: string;
};

type Link = {
  source: number;
  target: number;
  value: number;
};


interface NeumorphicSankeyProps {
  data: {
    nodes: Node[];
    links: Link[];
  };
  width?: number | string;
  height?: number | string;
  nodeWidth?: number;
  nodePadding?: number;
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
}

interface CustomNodeProps {
  x: number;
  y: number;
  width: number;
  height: number;
  index: number;
  payload: any;
  containerWidth: number;
}

const CustomNode = (props: CustomNodeProps) => {
  const { x, y, width, height, payload, containerWidth, index = 0 } = props;
  const isOut = x > (containerWidth / 2);
  const nodeName = payload?.name || `Node ${index + 1}`;
  
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill="#f0f0f0"
        stroke="#e0e0e0"
        strokeWidth="1"
        rx="4"
        ry="4"
        style={{
          filter: 'drop-shadow(4px 4px 6px rgba(0,0,0,0.1)) drop-shadow(-4px -4px 6px rgba(255,255,255,0.8))',
        }}
      />
      <text
        x={isOut ? x - 6 : x + width + 6}
        y={y + height / 2}
        textAnchor={isOut ? 'end' : 'start'}
        dominantBaseline="middle"
        fill="#666"
        style={{
          fontSize: '12px',
          fontWeight: 500,
          textShadow: '1px 1px 2px rgba(255,255,255,0.8)',
        }}
      >
        {nodeName}
      </text>
    </g>
  );
};
interface CustomLinkProps {
  sourceX: number;
  targetX: number;
  sourceY: number;
  targetY: number;
  sourceControlX: number;
  targetControlX: number;
  linkWidth: number;
  index: number;
  payload: any;
}

const CustomLink = (props: CustomLinkProps) => {
  const { sourceX, targetX, sourceY, targetY, sourceControlX, targetControlX, linkWidth, index } = props;
  
  const gradientId = `gradient-${index}`;
  const opacity = 0.6 + (index % 5) * 0.08;
  
  return (
    <g>
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366f1" stopOpacity={opacity} />
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity={opacity} />
        </linearGradient>
      </defs>
      <path
        d={`M${sourceX},${sourceY} C ${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`}
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth={linkWidth}
        strokeOpacity="0.8"
        style={{
          transition: 'all 0.3s ease',
          cursor: 'pointer',
        }}
      />
    </g>
  );
};

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: {
      source: { name: string };
      target: { name: string };
      value: number;
    };
  }>;
}

const CustomTooltip: React.FC<TooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length > 0 && payload[0].payload) {
    const data = payload[0].payload;
    return (
      <div className="bg-white bg-opacity-90 p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-800">
          {data.source?.name || 'Source'} → {data.target?.name || 'Target'}
        </p>
        <p className="text-sm text-gray-600">Value: {data.value}</p>
      </div>
    );
  }
  return null;
};

const NeumorphicSankey: React.FC<NeumorphicSankeyProps> = ({
  data,
  width = '100%',
  height = 400,
  nodeWidth = 10,
  nodePadding = 30,
  margin = { top: 20, right: 20, bottom: 20, left: 20 },
}) => {
  console.log('NeumorphicSankey mounted with data:', data);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = React.useState(0);

  // Process nodes and links for Recharts
  const { nodes, links } = useMemo(() => {
    const processedNodes = data.nodes.map((node, index) => ({
      ...node,
      id: `node-${index}`,
    }));

    const processedLinks = data.links.map((link, index) => ({
      ...link,
      id: `link-${index}`,
    }));

    return { nodes: processedNodes, links: processedLinks };
  }, [data]);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  return (
    <div 
      ref={containerRef}
      className="relative p-8 rounded-2xl w-full h-full"
      style={{
        background: '#f0f0f0',
        boxShadow: '8px 8px 16px #e0e0e0, -8px -8px 16px #ffffff',
        minHeight: '600px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div className="w-full flex-1" style={{ minHeight: '500px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <Sankey
            data={{ nodes, links }}
            node={({ x, y, width, height, index, payload }: any) => (
              <CustomNode 
                x={x} 
                y={y} 
                width={width} 
                height={height} 
                index={index} 
                payload={payload} 
                containerWidth={containerWidth} 
              />
            )}
            link={({ sourceX, targetX, sourceY, targetY, sourceControlX, targetControlX, linkWidth, index, payload }: any) => (
              <CustomLink 
                key={`link-${index}`}
                sourceX={sourceX}
                targetX={targetX}
                sourceY={sourceY}
                targetY={targetY}
                sourceControlX={sourceControlX}
                targetControlX={targetControlX}
                linkWidth={linkWidth}
                index={index}
                payload={payload}
              />
            )}
            nodeWidth={nodeWidth}
            nodePadding={nodePadding}
            margin={margin}
            linkCurvature={0.5}
            iterations={64}
          >
            <Tooltip content={<CustomTooltip active={false} />} />
          </Sankey>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default NeumorphicSankey;
