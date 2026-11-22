# Accessible Campus Navigator — Map UX Before & After Comparison
**Project:** Accessible Campus Navigator — JAIN Global Campus & FET  
**Milestone:** Map UX, Visual Clarity and Performance Enhancement  
**Reference Inspection:** Phase 16 / Phase 28 Baseline vs Modernized Cartography  
**Date:** 2026-11-22  

---

## 1. Overview

This document provides a comparative before-and-after analysis of the mapping and navigation interfaces in Accessible Campus Navigator. The goal was to evolve the application from a raw graph-topological visualization into a modern, architectural, intuitive campus navigation product tailored for students, visitors, wheelchair users, and university administrators.

---

## 2. 3D Campus Digital Twin (`/3d_campus_map`)

| Dimension | Before Enhancement | After Enhancement |
| :--- | :--- | :--- |
| **Top HUD Toolbar** | **Scattered 20-Button Cluster:** Buttons for 5 camera presets, 3 domains, 7 floor modes, and animation toggles spread across 4 separate rows, obscuring the upper canvas and confusing users. | **Streamlined 4-Group Toolbar:** Compact, responsive toolbar categorized into **Area** (All Campus, Outdoor, FET Building), **Floor** (All, 💥 Exploded, G, 1F, 2F, 3F, 4F), **Camera** (Default, Top, Front, 🔄 Rotate, Reset), and **Display** (🏷️ Labels, ⏯️ Route, 🏢 Cutaway). |
| **Default Camera Framing** | **Distant Oblique View (Distance > 140m):** Default camera positioned at `(75, 65, 80)` looking at origin, making the FET building appear tiny and lost in the distance on initial load. | **Intuitive 45° Isometric Framing:** Camera set at `(55, 46, 62)` with controls target at `(0, 8, 0)`, perfectly centering the 5-floor FET complex and its front avenue on first screen view. |
| **Lighting Rig & Shadows** | **Dark, High-Contrast Lighting:** Single directional sunlight with harsh black shadows; building facades and interior rooms appeared muddy and dark green. | **Dual-Hemisphere Studio Lighting:** `THREE.HemisphereLight(0xD1FAE5, 0x061E14, 0.95)` with boosted sun keylight (1.35) and ambient fill (0.65), providing crisp architectural contrast and soft ground shadows. |
| **Building Glass Transparency** | **Dense Tinted Glass (Opacity 0.45):** Opaque facade obstructed interior corridor and room visibility during normal inspection. | **Crystal Clear Cutaway:** Default curtain wall opacity reduced to 0.28, dropping to 0.08 in Cutaway Mode (`🏢 Cutaway`), revealing interior furniture, labs, elevators, and stairways with clarity. |
| **3D Room & Facility Labels** | **Visual Clutter & Total Overlap:** All 79 campus locations created persistent billboard sprites simultaneously. Labels overlapped into unreadable text clouds, especially at oblique camera angles. | **Smart Level of Detail (LOD) & Anti-Overlap:** Dynamic distance LOD (>120m shows landmarks only; 65–120m shows major gates/elevators; <65m shows individual rooms). Screen-space density culling suppresses labels closer than 38px. Origin, Destination, and Selected rooms are pinned with priority badges. |
| **Desktop Column Balance** | **Narrow 3D Viewport (`[2.3, 1.0]`):** 3D canvas occupied only ~65% of screen width, cramping spatial exploration. | **Wide 3D Viewport (`[2.8, 1.2]`):** 3D canvas expanded to ~72% of desktop width, maximizing visual immersion while retaining a structured control console. |
| **Quick Destination Selection** | **Manual Long Dropdown Search:** Users had to scroll through 79 options or type exact location strings. | **1-Click Suggestion Pills:** Prominent pills for high-frequency destinations (**HPC Lab**, **Library**, **Dean Office**, **Robotics Lab**) instantly set the target. |
| **Facility Inspector Interactivity** | **Read-Only Information Drawer:** Inspector card showed room metadata but required manual dropdown selection to navigate to it. | **Actionable Navigation Drawer:** Added 1-click **"🚩 Set as Start"**, **"🎯 Set as Dest"**, and **"🗺️ Switch to 2D Floor Plan"** buttons. |

---

## 3. 2D Campus Architectural Map (`/campus_map`)

| Dimension | Before Enhancement | After Enhancement |
| :--- | :--- | :--- |
| **Supported Campus Datasets** | **Hardcoded 15-Node Benchmark Map:** Only displayed the abstract 15-node dataset (`LOC_01` to `LOC_15`). The full 79-location JAIN Global Campus was completely absent from 2D mapping. | **Dual-Mode Campus Selector:** Instant toggle between **JAIN Global Campus & FET Building (79 Locations across 6 Levels)** and the **Schematic Benchmark Model (15 Locations)**. |
| **Floor Plan Levels** | **Limited to Floors 0 and 1:** Only Ground Floor and First Floor supported via basic radio buttons. | **Full 6-Level Navigation:** Complete support for **Outdoor Grounds (-1)**, **Ground Floor (0)**, **First Floor (1)**, **Second Floor (2)**, **Third Floor (3)**, and **Fourth Floor (4)**, plus **All Campus & Floors** combined view. |
| **Architectural Spatial Context** | **Abstract Scatter Points on Dark Grid:** Nodes floating in space with no walls, wings, corridors, or building boundaries. First-time students had no mental model of the building shape. | **Architectural Zone Overlays:** Clear Plotly vector shapes delineating the **Central Octagonal Rotunda & Atrium**, **South Entrance Foyer**, **West Academic Wing**, **East Academic Wing**, and **North Seminar Wing** for FET floors, plus **Sports Complex**, **Quad**, and **Hostels** for outdoor grounds. |
| **Node Symbols & Identification** | **Uniform Plain Dots:** All nodes rendered as identical circles with small text IDs (`LOC_01`), requiring hovering to discover facility types. | **Intuitive Categorical Symbols:** Category-specific emoji badges (🚪 Entrances, 🛗 Elevators, 🪜 Stairwells, 🔬 Research Labs, 📚 Libraries, 🚻 Restrooms, 🥪 Dining, ⚽ Sports Arena, 🏛️ Administration, 🅿️ Parking). |
| **Pathway Distinctions** | **Basic Edge Lines:** Simple lines connecting coordinates without distinct visual hierarchy for accessibility. | **Clear Accessibility Hierarchy:** Solid Emerald for Accessible Ramps (`#35D99A`, 3.8px), Solid Green for Accessible Corridors (`#16A36A`), Cyan for Elevator Shafts (`#60A5FA`, 4.2px), Dotted Amber for Stairs (`#F5B942`), and Dashed Red for Verified Obstacles (`#F87171`). |
| **Search & Discovery** | **No Search Functionality:** Users had to know node IDs and select them from raw selectboxes. | **Live Destination Search:** Integrated keyword search with instant suggestion pills, matching departments, abbreviations, room names, and aliases. |
| **Cross-Navigation Integration** | **Isolated Page Experience:** No direct links between 2D floor plans and the 3D digital twin. | **1-Click 2D ⇄ 3D Synchronization:** Direct toolbar buttons and inspector links allowing seamless switching between 2D architectural blueprints and 3D WebGL orbit views. |

---

## 4. Visual Contrast & Accessibility Summary

All modifications strictly adhere to the university-approved dark-green accessible palette:
- **Canvas Base Background:** `#07130F` (Dark Forest Green)
- **Secondary Surfaces & Panels:** `#0D1F18`
- **UI Cards & Containers:** `#122820`
- **Primary Action Accent:** `#16A36A`
- **High-Visibility Accent & Highlights:** `#35D99A`
- **Mint Text & Accents:** `#A7F3D0`
- **Primary Headings & Text:** `#F8FAFC`
- **Secondary Metadata Text:** `#9CAFA5`
- **Accessibility Alerts & Blockages:** `#F5B942` (Stairs/Warnings), `#F87171` (Blocked Hazards), `#60A5FA` (Elevators)

The resulting user interface balances architectural aesthetics with accessibility compliance, offering an intuitive, professional wayfinding experience for students, faculty, and visitors.
