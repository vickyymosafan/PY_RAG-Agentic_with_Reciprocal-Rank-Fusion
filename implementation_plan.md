# IMPLEMENATION PLAN - RAG AGENTIC UI (v3: High-Fidelity Technical)

## Goal

Transform the "messy" flat design into a polished, structured, "Agentic Control Panel" aesthetic.
Key keywords: Precision, Grid, HUD, Monospace, Data-Dense.
**Constraint**: NO GRADIENTS.

## User Feedback Analysis

- "Masih acak-acakan" -> Needs better alignment, consistent spacing, and visual structure.
- "Extension of Figma Experience" -> Needs pixel-perfect details.

## Design System: "SYSTEM CONSTRUCT"

### 1. Colors (Solid & High Contrast)

- **Background**: `#050505` (Almost Pure Black)
- **Panel BG**: `#0a0a0a` (Darker than before to pop the borders)
- **Borders**: `#333333` (Subtle) vs `#ffffff` (Active/Highlight)
- **Accent**: `#7c3aed` (Agentic Purple) - Used sparingly for "Status: Online" or "Active Input".

### 2. Typography

- **Headings**: `Inter`, Weight 700, Uppercase, Tracking +1px.
- **Data/Labels**: `JetBrains Mono`, Uppercase, Small sizes (10-12px).
- **Body**: `Inter`, High readability.

### 3. Structural Elements (The "Figma" Touch)

- **Corner Markers**: Decorative SVG angles on cards.
- **Header Lines**: Top borders with cutouts or labels.
- **Grid Background**: A purely CSS grid background (solid lines) to unify alignment.

## Changes

### `style.css`

- Add `grid-bg` class.
- Create `.tech-card` class with corner accents (using `::before`/`::after`).
- Define `.status-badge` to look like a technical readout.
- Fix Chat Bubble alignment to be more "message log" style.

### `index.html`

- Wrap Hero in a "System Status" container.
- Convert Feature Cards to "Modules".
- Redesign Pipeline to be a "Process Diagram" with labeled nodes.

### `chat.html`

- Make the chat window look like a dedicated app window / CRT terminal (clean version).

## Step-by-Step

1.  **Refine CSS Variables & Base**: establish the grid and typography.
2.  **Component Design**: Build the `.tech-card` frame.
3.  **Page Layouts**: Apply to Home, Upload, Chat.
4.  **Micro-Interactions**: Add hover states that light up borders (solid color).
