"""
Accessible Campus Navigator - Demonstration Screenshots Preparer
Student: Rudra Pratap | USN: 25BTRCL214 | JAIN University
Copies and organizes the 15 verified genuine application screenshots into DEMONSTRATION_SCREENSHOTS/
"""

import os
import shutil
from PIL import Image

SRC_MAPPING = {
    '01_main_dashboard.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_12.png',
    '02_login_page.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_5.png',
    '03_outdoor_campus_digital_twin.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\6b8bae57-4e18-4eab-941c-493288b8aaed\browser_sandbox\screenshots\step_9.png',
    '04_five_floor_fet_building.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\6b8bae57-4e18-4eab-941c-493288b8aaed\browser_sandbox\screenshots\step_11.png',
    '05_floor_selection.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_26.png',
    '06_destination_search.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\6b8bae57-4e18-4eab-941c-493288b8aaed\browser_sandbox\screenshots\step_15.png',
    '07_route_planning.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\75e17cfe-64b3-4e6e-b53e-368e2d1f72d5\browser_sandbox\screenshots\step_101.png',
    '08_wheelchair_accessible_route.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\75e17cfe-64b3-4e6e-b53e-368e2d1f72d5\browser_sandbox\screenshots\step_107.png',
    '09_turn_by_turn_navigation.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\9d84f9ed-4076-4cdf-99fd-ffe8d7afc1e6\phase_15_wayfinding_verified.png',
    '10_obstacle_reporting.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_48.png',
    '11_dynamic_rerouting.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\75e17cfe-64b3-4e6e-b53e-368e2d1f72d5\browser_sandbox\screenshots\step_127.png',
    '12_analytics_dashboard.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_73.png',
    '13_administrative_console.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_86.png',
    '14_accessibility_settings.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_108.png',
    '15_multilingual_interface.png': r'C:\Users\rudra pratap\.gemini\antigravity\brain\7dd7802a-ea48-4129-850f-a8cac380ac6a\browser_sandbox\screenshots\step_114.png'
}

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DEMONSTRATION_SCREENSHOTS")
os.makedirs(DEST_DIR, exist_ok=True)

def main():
    print(f"Deploying 15 genuine demonstration screenshots to: {DEST_DIR}")
    for target_name, src_path in SRC_MAPPING.items():
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source screenshot missing: {src_path}")
        
        target_path = os.path.join(DEST_DIR, target_name)
        shutil.copy2(src_path, target_path)
        
        # Verify with PIL
        with Image.open(target_path) as img:
            w, h = img.size
            size_kb = os.path.getsize(target_path) / 1024.0
            print(f"✓ {target_name}: {w}x{h} px, {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
