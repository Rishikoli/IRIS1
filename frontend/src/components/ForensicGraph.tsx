"use client";

import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface ForensicGraphProps {
    companySymbol: string;
}

const ForensicGraph: React.FC<ForensicGraphProps> = ({ companySymbol }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);
    const [analysis, setAnalysis] = useState<any>(null);

    useEffect(() => {
        const fetchGraphData = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/forensic/graph/${companySymbol}`);
                const data = await response.json();

                if (data.graph_data) {
                    // Process nodes
                    const processedNodes = data.graph_data.nodes.map((node: any) => ({
                        id: node.id,
                        position: node.position,
                        data: {
                            label: node.data.label,
                            riskScore: node.data.riskScore,
                            isShell: node.data.isShell
                        },
                        style: {
                            background: node.data.isShell ? '#fee2e2' : '#f8fafc',
                            border: node.data.isShell ? '2px solid #ef4444' : '1px solid #94a3b8',
                            borderRadius: '8px',
                            padding: '10px',
                            width: 150,
                            fontSize: '12px',
                            fontWeight: node.data.isShell ? 'bold' : 'normal',
                            boxShadow: node.data.isShell ? '0 0 15px rgba(239, 68, 68, 0.6)' : 'none',
                            animation: node.data.isShell ? 'pulse 2s infinite' : 'none'
                        },
                        type: 'default' // Using default node type for simplicity for now
                    }));

                    // Process edges
                    const processedEdges = data.graph_data.links.map((link: any) => ({
                        id: link.id,
                        source: link.source,
                        target: link.target,
                        animated: link.animated,
                        label: link.data.type === 'transfer' ? `₹${(link.data.amount / 100000).toFixed(1)}L` : '',
                        style: { stroke: link.data.type === 'transfer' ? '#ef4444' : '#94a3b8', strokeWidth: 2 },
                        markerEnd: {
                            type: MarkerType.ArrowClosed,
                            color: link.data.type === 'transfer' ? '#ef4444' : '#94a3b8',
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
        return <div className="flex items-center justify-center h-64">Loading Forensic Graph...</div>;
    }

    return (
        <div className="w-full h-[500px] bg-slate-50 rounded-xl border border-slate-200 relative overflow-hidden">
            {/* Risk Overlay */}
            <div className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur p-4 rounded-lg shadow-lg border border-red-100">
                <h4 className="text-sm font-bold text-slate-800 mb-2">Forensic Analysis</h4>
                <div className="space-y-2 text-xs">
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Shell Companies:</span>
                        <span className="font-bold text-red-600">{analysis?.shell_company_count || 0}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Circular Loops:</span>
                        <span className="font-bold text-orange-600">{analysis?.circular_trading_loops?.length || 0}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-500">Risk Flags:</span>
                        <span className="font-bold text-red-600">{analysis?.risk_flags || 0}</span>
                    </div>
                </div>
            </div>

            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
                attributionPosition="bottom-left"
            >
                <Background color="#cbd5e1" gap={16} />
                <Controls />
            </ReactFlow>

            <style jsx global>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `}</style>
        </div>
    );
};

export default ForensicGraph;
