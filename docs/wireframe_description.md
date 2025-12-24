# IRIS Wireframe & UX Description

This document outlines the structure, layout, and visual flow for the *Investigative Risk Intelligence System (IRIS)* to guide wireframing and design.

## 1. Visual Language & Aesthetics (The "Premium" Feel)
*   **Theme**: Cyber-Forensic / Institutional Dark Mode.
*   **Palette**: Deep Slate Blue (`#1e293b`), Neon Accent Purple (`#7B68EE`), Success Green (`#4ade80`), Alert Red (`#ef4444`).
*   **Style**: Glassmorphism (translucent cards), Neumorphism (soft 3D buttons), and smooth D3.js transitions.
*   **Typography**: Clean, monospace for data (e.g., `Cascadia Code`), Sans-Serif for headers (e.g., `Inter`).

---

## 2. Key Screen: Mission Control (Dashboard)
**Goal**: Immediate situational awareness. "God-Mode" for the auditor.

### Layout Structure (Grid System)
*   **Top Bar (Header)**:
    *   Logo (Top-Left): "IRIS" with an eye icon.
    *   **Global Search Bar** (Center): Large, prominent input "Enter Company Symbol (e.g., RELIANCE)".
    *   Status/Notification Bell (Top-Right): "System Operational" indicator.
*   **Sidebar (Navigation)**:
    *   Icons for: *Home, detailed Forensics, Reports, Settings*.
    *   Collapsible to maximize screen real estate for graphs.

### Widgets (The "Bento Box" Layout)
1.  **Risk Score Card (Hero Widget)**:
    *   Large circular gauge showing the Risk Score (0-100).
    *   Color-coded text: "Critical Risk" or "Safe".
2.  **Market Sentiment Pulse**:
    *   A live sparkline chart showing Sentiment (News) vs. Price.
    *   Badges for "Bearish" or "Bullish".
3.  **Recent Alerts List**:
    *   Cards showing: "Shell Company Detected", "M-Score Spike".
4.  **Network Graph Mini-View**:
    *   A smaller, interactive preview of the connection graph.

---

## 3. Key Screen: Forensic Analysis (The Workspace)
**Goal**: Deep-dive investigation. This is where the user spends 90% of their time.

### Sections (Tabs)
*   **Tab 1: RPT Network (The "God-Mode" View)**
    *   **Center Stage**: Full-screen interactive force-directed graph.
    *   **Sidebar Control**: Filters for "Show Shell Companies Only", "Highlight Circular Loops".
    *   **Interaction**: Hovering over a node displays a tooltip with `Role: Director`, `Risk: 95%`.
*   **Tab 2: Financial Metrics (The "Auditor" View)**
    *   **Split View**:
        *   Left: **Beneish M-Score** Gauge (Manipulation detector).
        *   Right: **Altman Z-Score** Gauge (Bankruptcy predictor).
    *   **Context**: Below each gauge, a list of "Red Flags" (e.g., "DSRI Index > 1.2").
*   **Tab 3: Vertical/Horizontal Analysis**
    *   **Layout**: Stacked Bar Charts representing the Income Statement structure.
    *   **Tooltip**: "Cost of Revenue is 60% of Total Revenue (Industry Avg: 45%)".

---

## 4. Key Screen: Report Generation (The Output)
**Goal**: Instant gratification & compliance.

### Modal / Overlay UI
*   **Click Trigger**: A floating "Generate Report" FAB (Floating Action Button) in the bottom-right.
*   **The Modal**:
    *   **Options**: Checkboxes for "Include Graph", "Include Sentiment", "Full Transaction History".
    *   **Format Toggle**: PDF / Excel.
    *   **Action**: Large "Download Audit Report" button.
*   **Loading State**: A cool animation saying "Agents Compilation Findings..." (gives a sense of AI work).

---

## 5. Interaction Flow Example
1.  **User Enters Symbol**: Typer "TCS" in the Global Search.
2.  **Transition**: The Dashboard fades out; the **Forensic Analysis** workspace slides in.
3.  **Agents Activate**: Small status indicators in the corner flicker: "Agent 2: Crunching Numbers...", "Agent 6: Scanning News...".
4.  **Discovery**: User sees a red node in the graph. Clicks it.
5.  **Drill Down**: A side panel opens showing "Entity Details: Shell Co detected."
6.  **Action**: User clicks "Export Report". PDF downloads instantly.
