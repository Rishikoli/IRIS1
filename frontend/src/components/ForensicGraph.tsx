import React, { useState, useEffect, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import CyberNode from './graph/CyberNode';

interface ForensicGraphProps {
    companySymbol: string;
}

const ForensicGraph: React.FC<ForensicGraphProps> = ({ companySymbol }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);
    const [analysis, setAnalysis] = useState<any>(null);

    // Register custom node types
    const nodeTypes = useMemo(() => ({ cyber: CyberNode }), []);

    useEffect(() => {
        const fetchGraphData = async () => {
            try {
                const response = await fetch(`/api/forensic/graph/${companySymbol}`);
                const data = await response.json();

                if (data.graph_data) {
                    // Process nodes
                    const processedNodes = data.graph_data.nodes.map((node: any) => ({
                        id: node.id,
                        // Spread out random positions more for better visibility
                        position: node.position || { x: Math.random() * 800, y: Math.random() * 600 },
                        data: {
                            label: node.data.label,
                            riskScore: node.data.riskScore,
                            isShell: node.data.isShell,
                            type: node.data.type // Pass original type to CyberNode
                        },
                        type: 'cyber' // Use our custom node
                    }));

                    // Process edges
                    const processedEdges = data.graph_data.links.map((link: any) => ({
                        id: link.id,
                        source: link.source,
                        target: link.target,
                        animated: true,
                        label: link.data.type === 'transfer' ? `₹${(link.data.amount / 100000).toFixed(1)}L` : '',
                        style: {
                            stroke: link.data.type === 'transfer' ? '#ef4444' : '#475569',
                            strokeWidth: link.data.type === 'transfer' ? 2 : 1
                        },
                        labelStyle: { fill: '#94a3b8', fontSize: 10 },
                        markerEnd: {
                            type: MarkerType.ArrowClosed,
                            color: link.data.type === 'transfer' ? '#ef4444' : '#475569',
                        },
                    }));

                    setNodes(processedNodes);
                    setEdges(processedEdges);
                    setAnalysis(data.analysis);
                }
            } catch (error) {
                console.error("Failed to fetch graph data:", error);
            } finally {
                setLoading(false);
            }
        };

        if (companySymbol) {
            fetchGraphData();
        }
    }, [companySymbol, setNodes, setEdges]);

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400 font-mono">Initializing Neural Link...</div>;
    }

    return (
        <div className="w-full h-[500px] bg-slate-50 rounded-xl border border-slate-200 relative overflow-hidden shadow-xl">
            {/* Risk Overlay */}
            <div className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur-md p-4 rounded-lg shadow-lg border border-red-50">
                <h4 className="text-sm font-bold text-slate-800 mb-2 font-mono flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                    FORENSIC INTELLIGENCE
                </h4>
                <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Shell Companies:</span>
                        <span className="font-bold text-red-600">{analysis?.shell_company_count || 0}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Circular Loops:</span>
                        <span className="font-bold text-orange-600">{analysis?.circular_trading_loops?.length || 0}</span>
                    </div>
                </div>
            </div>

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
};

export default ForensicGraph;
