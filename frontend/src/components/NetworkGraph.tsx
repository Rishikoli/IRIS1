import React, { useCallback, useEffect, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import CyberNode from './graph/CyberNode';

interface NetworkGraphProps {
    data: {
        nodes: any[];
        edges: any[];
    };
    cycles?: string[][];
    isLoading?: boolean;
}

export default function NetworkGraph({ data, cycles = [], isLoading = false }: NetworkGraphProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    // Register custom node types
    const nodeTypes = useMemo(() => ({ cyber: CyberNode }), []);

    useEffect(() => {
        if (data && data.nodes) {
            // Process Nodes for ReactFlow
            const processedNodes = data.nodes.map((node: any) => ({
                id: node.id,
                // Assign random position if removed (ReactFlow needs position)
                position: node.position || { x: Math.random() * 1000, y: Math.random() * 800 },
                data: {
                    label: node.label || node.id,
                    ...node, // Spread all backend properties (is_shell, color, etc)
                    // Map ShellHunter logic to CyberNode logic
                    riskScore: node.riskScore || node.val || 0,
                    isShell: node.is_shell || node.type === 'shell'
                },
                type: 'cyber'
            }));

            // Process Edges
            const processedEdges = data.edges.map((edge: any) => ({
                id: edge.id || `${edge.source}-${edge.target}`,
                source: edge.source,
                target: edge.target,
                animated: true,
                label: edge.label || '',
                style: {
                    stroke: edge.color || '#475569',
                    strokeWidth: edge.is_cycle ? 2.5 : 1.5,
                    opacity: edge.is_cycle ? 1 : 0.6
                },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: edge.color || '#475569',
                },
            }));

            setNodes(processedNodes);
            setEdges(processedEdges);
        }
    }, [data, setNodes, setEdges]);


    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[600px] bg-black rounded-3xl border border-gray-800">
                <div className="flex flex-col items-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mb-4"></div>
                    <span className="text-red-500 font-mono animate-pulse">Loading Neural Network...</span>
                </div>
            </div>
        );
    }

    if (!data || !data.nodes || data.nodes.length === 0) {
        return (
            <div className="flex items-center justify-center h-[600px] bg-black rounded-3xl border border-gray-800">
                <div className="text-center text-gray-500 font-mono">
                    <p className="text-4xl mb-4">🕸️</p>
                    <p>No Data Available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-[600px] bg-slate-50 rounded-xl border border-slate-200 relative overflow-hidden shadow-xl">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                className="bg-slate-50"
            >
                <Background color="#cbd5e1" gap={20} size={1} />
                <Controls className="!bg-white !border-slate-200 !fill-slate-600 !shadow-md" />
            </ReactFlow>
        </div>
    );
}
