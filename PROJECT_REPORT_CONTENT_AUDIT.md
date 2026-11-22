# Project Report Content Audit & Compliance Verification

**Project Title:** Accessible Campus Navigator  
**Student Name:** Rudra Pratap  
**USN:** 25BTRCL214  
**Department:** Artificial Intelligence and Machine Learning (Section D)  
**School:** School of Computer Science and Engineering  
**Faculty:** Faculty of Engineering and Technology  
**University:** JAIN (Deemed-to-be University)  
**Deliverables Audited:**
- `Accessible_Campus_Navigator_Final_Project_Report.docx` (52.8 KB)
- `Accessible_Campus_Navigator_Final_Project_Report.pdf` (7.2 KB)

---

## 1. Compliance Checklist & Chapter Audit

| Chapter / Section | Required Content | Status | Verification Notes |
| :--- | :--- | :---: | :--- |
| **Cover Page** | Student details, USN, university, faculty, department, title | **COMPLIANT** | Exact details: Rudra Pratap, 25BTRCL214, JAIN University, B.Tech AIML (Sec D). |
| **Declaration** | Formal academic declaration by Rudra Pratap | **COMPLIANT** | Declared with signature placeholder and academic affiliation. |
| **Acknowledgement** | Grateful recognition of university and faculty guidance | **COMPLIANT** | Formal recognition of academic guidance and facilities teams. |
| **Abstract** | Problem context, 3D twin, algorithms, invariants, results | **COMPLIANT** | Summarizes 79 nodes, 106 pathways, 5 floors, and 190 automated tests. |
| **Table of Contents** | Complete listing of chapters, sections, and appendices | **COMPLIANT** | Formatted with dot leaders and aligned page references. |
| **Chapter 1: Introduction** | Background, problem overview, motivation, objectives, scope | **COMPLIANT** | Contextualized to JAIN Global Campus (300 acres) on Kanakapura Road. |
| **Chapter 2: Problem Definition** | Multi-floor hurdles, 2D map limits, physical barriers | **COMPLIANT** | Explains commercial map limitations and disability accessibility risks. |
| **Chapter 3: Proposed System** | System overview, stakeholder personas, FRs, NFRs | **COMPLIANT** | Formulates 6 Functional Requirements and 4 Non-Functional Requirements. |
| **Chapter 4: Architecture** | 3-tier architecture, module descriptions, data flow | **COMPLIANT** | Presentation (Streamlit/Three.js), Logic (RouteFinder/A11y), Data (SQLite WAL). |
| **Chapter 5: Digital Twin** | Outdoor 300-acre map, 5-floor FET, zero-shear proof | **COMPLIANT** | Elevator shaft invariant at $(-6.0, 18.0)$ mathematically asserted across 5 floors. |
| **Chapter 6: Algorithms** | Graph representation, Dijkstra, BFS, complexity, wheelchair | **COMPLIANT** | Formulates $O((V+E)\log V)$ Dijkstra, $O(V+E)$ BFS, and stair exclusion. |
| **Chapter 7: Navigation & Obstacles**| FSM session states, vector cross-products, 4-stage lifecycle | **COMPLIANT** | Documents 8 FSM states and staff verification barrier lifecycle. |
| **Chapter 8: UI & Accessibility** | Dark green glassmorphism, i18n (en, kn, hi), WCAG AAA | **COMPLIANT** | Explains color palette (#07130F, #16A36A), high contrast, and reduced motion. |
| **Chapter 9: Database & Security** | SQLite WAL, PBKDF2 (600,000 iter), brute-force lockout, RBAC | **COMPLIANT** | Documents 15-min lockout, parameterised SQL, and sole-admin protection. |
| **Chapter 10: Analytics** | Dual datasets (79-node vs 15-node), 4 Plotly charts | **COMPLIANT** | Analyzes 83% step-free ratio, floor distributions, and resolution times. |
| **Chapter 11: Testing & Results** | Unit, integration, security, deployment test results | **COMPLIANT** | Cites exact 190 tests passed in 32.1s (0 failures, 0 errors, 0 skipped). No 100% coverage claim. |
| **Chapter 12: Deployment** | Dockerfile (appuser UID 10001), Compose volumes, Nginx | **COMPLIANT** | Documents non-root user security, WebSocket streaming, and deploy scripts. |
| **Chapter 13: Limitations & Future**| Schematic coordinates, heuristic scores, future BLE beacons | **COMPLIANT** | Transparently outlines illustrative layout and future indoor IoT positioning. |
| **Chapter 14: Conclusion** | Summary of engineering achievements and universal impact | **COMPLIANT** | Concludes with platform readiness and academic defense defense. |
| **References** | IEEE style formal citations | **COMPLIANT** | 10 academic and technical citations (Dijkstra, Cormen, WCAG, OWASP). |

---

## 2. Formatting & Typography Quality Verification

- **Primary Typeface:** Times New Roman / Clean Serif across document body.
- **Body Font Size:** 12 pt with 1.3 to 1.5 line spacing.
- **Headings Hierarchy:** Chapter Titles (18–20 pt bold), Section Headings (14 pt bold), Sub-headings (12 pt bold).
- **Paragraph Alignment:** Fully justified margins on left (1.25") and right (1.0") for book binding standards.
- **Color Consistency:** Dark forest green headers (`#0D1F18`, `#16A36A`) aligning with the project's visual identity.
