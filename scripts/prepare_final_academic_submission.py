"""
Accessible Campus Navigator - Final Academic Submission Package Assembler
Student: Rudra Pratap | USN: 25BTRCL214 | JAIN University
Assembles and organizes all academic deliverables into FINAL_ACADEMIC_SUBMISSION/
"""

import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMISSION_DIR = os.path.join(ROOT_DIR, "FINAL_ACADEMIC_SUBMISSION")

FOLDERS = [
    "01_PROJECT_REPORT",
    "02_PRESENTATION",
    "03_DEMONSTRATION",
    "04_VIVA_PREPARATION",
    "05_VALIDATION"
]

def main():
    print(f"Creating FINAL_ACADEMIC_SUBMISSION package in: {SUBMISSION_DIR}")
    for folder in FOLDERS:
        os.makedirs(os.path.join(SUBMISSION_DIR, folder), exist_ok=True)
        
    # 01_PROJECT_REPORT
    report_files = [
        "Accessible_Campus_Navigator_Final_Project_Report.docx",
        "Accessible_Campus_Navigator_Final_Project_Report.pdf",
        "PROJECT_REPORT_CONTENT_AUDIT.md"
    ]
    for rf in report_files:
        src = os.path.join(ROOT_DIR, rf)
        if os.path.exists(src):
            dst = os.path.join(SUBMISSION_DIR, "01_PROJECT_REPORT", rf)
            shutil.copy2(src, dst)
            print(f"Copied {rf} -> 01_PROJECT_REPORT ({os.path.getsize(dst):,} bytes)")

    # 02_PRESENTATION
    pres_files = [
        "Accessible_Campus_Navigator_Final_Presentation.pptx",
        "ACCESSIBLE_CAMPUS_NAVIGATOR_SLIDE_EXPLANATIONS.md"
    ]
    for pf in pres_files:
        src = os.path.join(ROOT_DIR, pf)
        if os.path.exists(src):
            dst = os.path.join(SUBMISSION_DIR, "02_PRESENTATION", pf)
            shutil.copy2(src, dst)
            print(f"Copied {pf} -> 02_PRESENTATION ({os.path.getsize(dst):,} bytes)")

    # 03_DEMONSTRATION
    demo_files = [
        "ACCESSIBLE_CAMPUS_NAVIGATOR_FINAL_DEMO_GUIDE.md",
        "ACCESSIBLE_CAMPUS_NAVIGATOR_7_MIN_DEMO_SCRIPT.md"
    ]
    for df in demo_files:
        src = os.path.join(ROOT_DIR, df)
        if os.path.exists(src):
            dst = os.path.join(SUBMISSION_DIR, "03_DEMONSTRATION", df)
            shutil.copy2(src, dst)
            print(f"Copied {df} -> 03_DEMONSTRATION ({os.path.getsize(dst):,} bytes)")
            
    # Copy DEMONSTRATION_SCREENSHOTS directory
    src_shots = os.path.join(ROOT_DIR, "DEMONSTRATION_SCREENSHOTS")
    dst_shots = os.path.join(SUBMISSION_DIR, "03_DEMONSTRATION", "DEMONSTRATION_SCREENSHOTS")
    if os.path.exists(src_shots):
        if os.path.exists(dst_shots):
            shutil.rmtree(dst_shots)
        shutil.copytree(src_shots, dst_shots)
        print(f"Copied DEMONSTRATION_SCREENSHOTS/ -> 03_DEMONSTRATION ({len(os.listdir(dst_shots))} files)")

    # Copy PROJECT_ARCHITECTURE_DIAGRAMS directory
    src_diags = os.path.join(ROOT_DIR, "PROJECT_ARCHITECTURE_DIAGRAMS")
    dst_diags = os.path.join(SUBMISSION_DIR, "03_DEMONSTRATION", "PROJECT_ARCHITECTURE_DIAGRAMS")
    if os.path.exists(src_diags):
        if os.path.exists(dst_diags):
            shutil.rmtree(dst_diags)
        shutil.copytree(src_diags, dst_diags)
        print(f"Copied PROJECT_ARCHITECTURE_DIAGRAMS/ -> 03_DEMONSTRATION ({len(os.listdir(dst_diags))} files)")

    # 04_VIVA_PREPARATION
    viva_files = [
        "ACCESSIBLE_CAMPUS_NAVIGATOR_COMPLETE_VIVA_GUIDE.md",
        "ACCESSIBLE_CAMPUS_NAVIGATOR_VIVA_PREPARATION.md"
    ]
    for vf in viva_files:
        src = os.path.join(ROOT_DIR, vf)
        if os.path.exists(src):
            dst = os.path.join(SUBMISSION_DIR, "04_VIVA_PREPARATION", vf)
            shutil.copy2(src, dst)
            print(f"Copied {vf} -> 04_VIVA_PREPARATION ({os.path.getsize(dst):,} bytes)")

    # 05_VALIDATION
    val_files = [
        "ACCESSIBLE_CAMPUS_NAVIGATOR_FINAL_VALIDATION_REPORT.md",
        "FINAL_PROJECT_OVERVIEW.md"
    ]
    for vf in val_files:
        src = os.path.join(ROOT_DIR, vf)
        if os.path.exists(src):
            dst = os.path.join(SUBMISSION_DIR, "05_VALIDATION", vf)
            shutil.copy2(src, dst)
            print(f"Copied {vf} -> 05_VALIDATION ({os.path.getsize(dst):,} bytes)")

if __name__ == "__main__":
    main()
