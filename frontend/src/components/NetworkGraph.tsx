import React, { useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType,
    ConnectionLineType,
    ReactFlowProvider,
    useReactFlow,
    ReactFlowInstance
} from 'reactflow';
import 'reactflow/dist/style.css';

interface NetworkGraphProps {
    data: {
        nodes: any[];
        edges: any[];
    };
    isLoading?: boolean;
}

const nodeTypes = {
    // We can define custom node types here if needed
};

function NetworkGraphContent({ data, isLoading = false }: NetworkGraphProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const { fitView } = useReactFlow();

    React.useEffect(() => {
        if (data && data.nodes && data.edges) {
            // Map backend nodes to React Flow nodes
            const mappedNodes: Node[] = data.nodes.map((node: any) => ({
                id: node.id,
                type: 'default', // Using default for simplicity, can be 'custom'
                data: {
                    label: (
                        <div className="text-center">
                            <div className="font-bold text-sm">{node.data.label}</div>
                            <div className="text-xs text-gray-500">{node.data.position}</div>
                            {node.data.risk_score > 50 && (
                                <div className="text-xs text-red-500 font-bold mt-1">Risk: {node.data.risk_score}</div>
                            )}
                        </div>
                    )
                },
                position: node.position,
                style: {
                    background: node.data.type === 'company' ? '#eff6ff' :
                        node.data.type === 'shell' ? '#fef2f2' : '#ffffff',
                    border: node.data.type === 'company' ? '2px solid #3b82f6' :
                        node.data.type === 'shell' ? '2px solid #ef4444' : '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '10px',
                    width: 150,
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }
            }));

            // Map backend edges to React Flow edges
            const mappedEdges: Edge[] = data.edges.map((edge: any) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                label: edge.label,
                animated: true,
                style: edge.style,
                labelStyle: { fill: edge.data.is_suspicious ? '#ef4444' : '#64748b', fontWeight: 700 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: edge.style.stroke,
                },
            }));

            setNodes(mappedNodes);
            setEdges(mappedEdges);

            // Force fit view after render
            setTimeout(() => {
                fitView({ padding: 0.2 });
            }, 100);
        }
    }, [data, setNodes, setEdges, fitView]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[500px] bg-gray-50 rounded-3xl border border-gray-200">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-4 text-gray-500">Building forensic network...</span>
            </div>
        );
    }

    if (!data || !data.nodes || data.nodes.length === 0) {
        return (
            <div className="flex items-center justify-center h-[500px] bg-gray-50 rounded-3xl border border-gray-200">
                <div className="text-center text-gray-500">
                    <p className="text-xl mb-2">🕸️</p>
                    <p>No network data available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-[600px] w-full bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                attributionPosition="bottom-right"
            >
                <Background color="#f1f5f9" gap={16} />
                <Controls />
            </ReactFlow>
        </div>
    );
}

export default function NetworkGraph(props: NetworkGraphProps) {
    return (
        <ReactFlowProvider>
            <NetworkGraphContent {...props} />
        </ReactFlowProvider>
    );
}
