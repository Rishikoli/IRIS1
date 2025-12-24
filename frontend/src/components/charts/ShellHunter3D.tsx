
'use client';

import React, { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
// @ts-ignore
import SpriteText from 'three-spritetext';
import * as THREE from 'three';
// Dynamically import 3D force graph to avoid SSR issues
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });

interface Node {
    id: string;
    type?: string;
    risk_score?: number;
    label?: string;
    val?: number; // Size
    color?: string;
}

interface Edge {
    source: string;
    target: string;
    relationship?: string;
    weight?: number;
    is_suspicious?: boolean;
}

interface ShellHunter3DProps {
    data: {
        nodes: any[];
        edges: any[];
    };
    cycles: string[][]; // List of cycles e.g. [['A','B','C','A'], ...]
}

const ShellHunter3D = ({ data, cycles }: ShellHunter3DProps) => {
    const fgRef = useRef<any>(null); // Explicitly typed as any or null
    const [graphData, setGraphData] = useState<{ nodes: Node[], links: any[] }>({ nodes: [], links: [] });

    // Process data for 3D visualization
    useEffect(() => {
        if (!data || !data.nodes) return;

        // Transform Nodes
        const nodes = data.nodes.map(n => ({
            id: n.id,
            type: n.data?.type || 'unknown',
            risk_score: n.data?.risk_score || 0,
            label: n.data?.label || n.id,
            // Color logic: Companies=Blue, Shells=Red/Pink, Others=Grey
            color: (n.data?.type === 'shell' || n.data?.risk_score > 80) ? '#ff0055'
                : (n.data?.type === 'company') ? '#4db8ff'
                    : '#a0a0a0',
            // Size logic: Central company bigger
            val: (n.data?.type === 'company') ? 20 : 5
        }));

        // Transform Edges
        // Identify which edges are part of a 'cycle' to make them GLOW
        const cycleEdges = new Set<string>();
        if (cycles) {
            cycles.forEach(cycle => {
                for (let i = 0; i < cycle.length - 1; i++) {
                    const u = cycle[i];
                    const v = cycle[i + 1];
                    cycleEdges.add(`${u}-${v}`);
                    cycleEdges.add(`${v}-${u}`); // undirected check
                }
            });
        }

        const links = data.edges.map(e => {
            const isCycleEdge = cycleEdges.has(`${e.source}-${e.target}`);
            return {
                source: e.source,
                target: e.target,
                relationship: e.label,
                color: isCycleEdge ? '#ff0000' : (e.data?.is_suspicious ? '#ff9900' : '#404040'),
                width: isCycleEdge ? 3 : 1,
                particles: isCycleEdge ? 4 : 0, // Particle effect for Shell Loops!
                particleSpeed: 0.02,
                particleSize: 4
            };
        });

        setGraphData({ nodes, links });
    }, [data, cycles]);

    // console.log("ShellHunter3D Mounting...", { nodeCount: data?.nodes?.length, cycleCount: cycles?.length });

    return (
        <div className="relative w-full h-[600px] bg-black rounded-3xl overflow-hidden border border-gray-800 shadow-2xl">
            {/* HUD Overlay */}
            <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <h3 className="text-white font-mono text-lg font-bold flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    SHELL HUNTER 3D
                </h3>
                <div className="text-gray-400 text-xs font-mono mt-1">
                    CYCLES DETECTED: <span className="text-red-400 font-bold">{cycles ? cycles.length : 0}</span>
                </div>
            </div>

            <div className="absolute bottom-4 right-4 z-10 pointer-events-none text-right">
                <div className="text-gray-500 text-tiny font-mono">WASD to Move | Click to Focus</div>
            </div>

            {/* 3D Graph */}
            <ForceGraph3D
                ref={fgRef}
                graphData={graphData}
                backgroundColor="#050505"
                nodeLabel="label"
                nodeRelSize={6}
                linkDirectionalParticles="particles"
                linkDirectionalParticleSpeed="particleSpeed"
                linkDirectionalParticleWidth="particleSize"
                linkColor="color"
                linkWidth="width"
                nodeResolution={16}
                enableNodeDrag={false}
                onNodeClick={(node: any) => {
                    // Aim at node on click
                    const distance = 40;
                    const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
                    if (fgRef.current) {
                        fgRef.current.cameraPosition(
                            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
                            node, // lookAt ({ x, y, z })
                            3000  // ms transition duration
                        );
                    }
                }}
                nodeThreeObject={(node: any) => {
                    const group = new THREE.Group();

                    // Sphere
                    const sphereGeometry = new THREE.SphereGeometry(node.val);
                    const sphereMaterial = new THREE.MeshLambertMaterial({
                        color: node.color,
                        transparent: true,
                        opacity: 0.9
                    });
                    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                    group.add(sphere);

                    // Text Label
                    const sprite = new SpriteText(node.label);
                    sprite.color = node.color === '#ff0055' ? '#ff99aa' : 'white';
                    sprite.textHeight = 8;
                    sprite.position.y = node.val + 4; // Position above sphere
                    group.add(sprite);

                    return group;
                }}
                nodeThreeObjectExtend={false} // We are building the whole object manually
                cooldownTicks={100}
                onEngineStop={() => fgRef.current.zoomToFit(400)}
            />
        </div>
    );
};

export default ShellHunter3D;
