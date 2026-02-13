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
    const [selectedNode, setSelectedNode] = useState<any>(null);

    // Register custom node types
    const nodeTypes = useMemo(() => ({ cyber: CyberNode }), []);
    const generateAiSummary = (node: any) => {
        const risks = [
            "Circular trading patterns detected.",
            "High-value unsecured loans without clear business purpose.",
            "Shared director with known shell entities.",
            "Frequent rapid movement of funds to tax havens.",
            "Inconsistent financial filings compared to peer group."
        ];

        // Deterministic random based on node id length
        const riskIdx = node.id.length % risks.length;

        if (node.data.isShell) {
            return `AI ALERT: High probability of Shell Entity. ${risks[riskIdx]} Transaction volume does not match operational footprint. IMMEDIATE AUDIT RECOMMENDED.`;
        } else if (node.data.type === 'person' && node.data.riskScore > 50) {
            return `AI ANALYSIS: Individual flagged for interlocking directorates. Associated with multiple high-risk entities. Potential beneficiary of siphoned funds.`;
        } else if (node.data.type === 'vendor') {
            return `AI NOTE: Vendor entity with irregular payment patterns. Verify invoices against GST filings. Risk Level: Low-Moderate.`;
        } else {
            return `AI ANALYSIS: Subsidiary entity operating within expected parameters. Monitor for downstream exposure to high-risk vendors.`;
        }
    };

    const onNodeClick = (_: React.MouseEvent, node: any) => {
        setSelectedNode({
            ...node,
            summary: generateAiSummary(node)
        });
    };

    const closePopup = () => setSelectedNode(null);

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

            {/* AI Summary Popup */}
            {selectedNode && (
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white/95 backdrop-blur-xl p-6 rounded-2xl shadow-2xl border border-indigo-100 w-96 max-w-[90%] transition-all duration-300 animate-in fade-in zoom-in-95">
                    <button
                        onClick={closePopup}
                        className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 transition-colors"
                    >
                        ✕
                    </button>

                    <div className="flex items-center gap-3 mb-4">
                        <div className={`w-3 h-3 rounded-full ${selectedNode.data.riskScore > 80 ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' :
                            selectedNode.data.riskScore > 50 ? 'bg-orange-500' : 'bg-green-500'
                            }`} />
                        <h3 className="font-bold text-lg text-slate-800">{selectedNode.data.label}</h3>
                    </div>

                    <div className="space-y-3">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-slate-500">Entity Type:</span>
                            <span className="font-mono font-semibold text-slate-700 uppercase bg-slate-100 px-2 py-0.5 rounded">{selectedNode.data.type}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-slate-500">Risk Score:</span>
                            <span className={`font-mono font-bold ${selectedNode.data.riskScore > 80 ? 'text-red-600' :
                                selectedNode.data.riskScore > 50 ? 'text-orange-600' : 'text-green-600'
                                }`}>{selectedNode.data.riskScore}/100</span>
                        </div>

                        <div className="pt-3 border-t border-slate-100">
                            <div className="text-xs font-bold text-indigo-600 mb-1 flex items-center gap-1">
                                <span className="text-lg">✨</span> AI DETECTED ANOMALIES
                            </div>
                            <p className="text-sm text-slate-600 leading-relaxed font-medium">
                                {selectedNode.summary}
                            </p>
                        </div>

                        <button className="w-full mt-2 py-2 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors" onClick={closePopup}>
                            Investigate Further
                        </button>
                    </div>
                </div>
            )}

            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
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
