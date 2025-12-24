
import logging
from typing import Dict, List, Any, Set
import random
import networkx as nx

logger = logging.getLogger(__name__)

class ShellHunterAgent:
    """
    Agent 2.5: Shell Company Hunter
    Specialized in detecting circular ownership, money laundering loops, and interlocking directorates.
    Uses NetworkX for graph algorithms.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        logger.info("Shell Hunter Agent Initialized")

    def analyze_network(self, main_company_symbol: str) -> Dict[str, Any]:
        """
        Main entry point.
        1. Simulates a complex "Universe" of related entities (MCA Data).
        2. Injects a hidden "Shell Ring" for forensic demonstration.
        3. Runs detection algorithms to FIND that ring.
        4. Returns the graph with forensic annotations.
        """
        logger.info(f"Shell Hunter: Analyzing network for {main_company_symbol}")
        
        # 1. Simulate the Data (Since we don't have real MCA/GST access yet)
        self._simulate_mca_universe(main_company_symbol)

        # 2. Run Forensic Algorithms
        cycles = self._detect_circular_trading()
        hidden_directors = self._detect_director_interlocking()

        # 3. Annotate the Graph for Frontend
        nodes, edges = self._format_graph_output(cycles, hidden_directors)

        return {
            "risk_score": self._calculate_network_risk(len(cycles), len(hidden_directors)),
            "detected_cycles": cycles,
            "hidden_directors": hidden_directors,
            "graph_data": {
                "nodes": nodes,
                "edges": edges
            }
        }

    def _simulate_mca_universe(self, root_node: str):
        """
        Simulates a realistic corporate network with:
        - Legitimate subsidiaries (Tree structure)
        - Vendors/Suppliers (Random links)
        - A HIDDEN SHELL RING (Circular A->B->C->A)
        """
        self.graph.clear()
        
        # --- 1. Legitimate Structure (The "Clean" Part) ---
        self.graph.add_node(root_node, type="company", category="target", risk=0)
        
        subsidiaries = [f"{root_node}_Sub_{i}" for i in range(1, 4)]
        for sub in subsidiaries:
            self.graph.add_node(sub, type="company", category="subsidiary", risk=10)
            self.graph.add_edge(root_node, sub, relation="ownership", weight=100)

        vendors = [f"Vendor_{i}" for i in range(1, 6)]
        for vendor in vendors:
            self.graph.add_node(vendor, type="company", category="vendor", risk=5)
            # Link to random sub or root
            target = random.choice([root_node] + subsidiaries)
            self.graph.add_edge(target, vendor, relation="payment", weight=random.randint(5, 50))

        # --- 2. The "Fraud Ring" (The Hidden Trap) ---
        # A specific, high-risk cycle: Root -> Shell_A -> Shell_B -> Shell_C -> Root
        # Suspicious names that sound generic but shady
        shell_a = "Vortex_Global_Holdings_LLP"
        shell_b = "Apex_Strategic_Consulting"
        shell_c = "Quantum_Capital_Ventures"
        
        # Add Shell Nodes
        self.graph.add_node(shell_a, type="shell", category="shell", risk=85, address="PO Box 442, Cayman Islands")
        self.graph.add_node(shell_b, type="shell", category="shell", risk=92, address="Suite 101, Nariman Point (Shared Office)")
        self.graph.add_node(shell_c, type="shell", category="shell", risk=88, address="Virtual Office, Cyber City")

        # Create the Cycle (Money Flow)
        # Root pays Shell A (fake invoice)
        self.graph.add_edge(root_node, shell_a, relation="payment", weight=500, label="Consulting Fees (No Invoice)")
        # Shell A pays Shell B (layering)
        self.graph.add_edge(shell_a, shell_b, relation="transfer", weight=480, label="Unsecured Loan")
        # Shell B pays Shell C (layering)
        self.graph.add_edge(shell_b, shell_c, relation="investment", weight=450, label="Convertible Debentures")
        # Shell C invests back in Root (Integration/Round Tripping)
        self.graph.add_edge(shell_c, root_node, relation="investment", weight=400, label="FDI / Round Trip")

        # --- 3. The "Interlocking Director" (The Mastermind) ---
        director = "Vikram_'The_Ghost'_Mehta"
        self.graph.add_node(director, type="person", category="director", risk=99)
        # He sits on the board of ALL 3 Shells
        self.graph.add_edge(director, shell_a, relation="director", weight=0)
        self.graph.add_edge(director, shell_b, relation="director", weight=0)
        self.graph.add_edge(director, shell_c, relation="director", weight=0)


    def _detect_circular_trading(self) -> List[List[str]]:
        """
        ALGORITHM: Uses Tarjan's Algo (via NetworkX) to find Strongly Connected Components (SCCs)
        or simple_cycles to detect money loops.
        """
        cycles = list(nx.simple_cycles(self.graph))
        # Filter for relevant cycles (length > 2 to avoid simple bilateral trade)
        suspicious_cycles = [c for c in cycles if len(c) > 2]
        
        logger.info(f"Shell Hunter: Detected {len(suspicious_cycles)} suspicious cycles: {suspicious_cycles}")
        return suspicious_cycles

    def _detect_director_interlocking(self) -> List[str]:
        """
        Finds directors who are connected to unusually high number of High Risk entities.
        """
        suspects = []
        for node in self.graph.nodes:
            if self.graph.nodes[node].get("type") == "person":
                # Count neighbors that are Shells or High Risk
                risk_neighbors = 0
                for neighbor in self.graph.neighbors(node): # This might need undirected view for 'director of'
                     # In our simulation, edge is Director -> Company usually
                    if self.graph.nodes[neighbor].get("type") == "shell":
                        risk_neighbors += 1
                
                if risk_neighbors >= 2:
                    suspects.append(node)
        
        return suspects

    def _calculate_network_risk(self, cycle_count: int, dark_director_count: int) -> float:
        """
        Calculates a 'Network Infection Score' (0-100).
        """
        base_risk = 10
        risk = base_risk + (cycle_count * 30) + (dark_director_count * 20)
        return min(100.0, risk)

    def _format_graph_output(self, cycles: List[List[str]], hidden_directors: List[str]):
        """
        Converts NetworkX graph to the JSON format expected by the 3D Graph frontend.
        Annotates nodes/edges if they are part of a detected fraud ring.
        """
        # Flatten cycles into a set of 'infected' edges/nodes for fast lookup
        cycle_edges = set()
        cycle_nodes = set()
        for cycle in cycles:
            for i in range(len(cycle)):
                u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                cycle_edges.add((u, v))
                cycle_nodes.add(u)
        
        output_nodes = []
        for n, attrs in self.graph.nodes(data=True):
            is_infected = n in cycle_nodes
            is_dark_director = n in hidden_directors
            
            node_color = "#4ade80" # Green (Safe)
            if attrs["type"] == "shell": node_color = "#ef4444" # Red
            if attrs["type"] == "person": node_color = "#f59e0b" # Orange
            
            if is_infected: node_color = "#ff0000" # BRIGHT RED for detected cycle
            if is_dark_director: node_color = "#7f1d1d" # DARK RED for mastermind
            
            output_nodes.append({
                "id": n,
                "label": n.replace("_", " "),
                "type": attrs["type"],
                "color": node_color,
                "val": 20 if is_infected else 5, # Size
                "is_shell": is_infected,
                "risk_score": attrs.get("risk", 0) # CRITICAL: Pass risk for frontend styling
            })

        output_edges = []
        for u, v, attrs in self.graph.edges(data=True):
            is_cycle_edge = (u, v) in cycle_edges
            
            output_edges.append({
                "source": u,
                "target": v,
                "label": attrs.get("label", attrs.get("relation", "")),
                "is_cycle": is_cycle_edge,
                "color": "#ff0000" if is_cycle_edge else "#94a3b8"
            })
            
        return output_nodes, output_edges
