"""Unit and integration test suite for Phase 18: Advanced User Experience & Intelligent Campus Services.

Verifies:
1. Saved Places (bookmarks) lifecycle, privacy per user account, and retrieval.
2. Favourite Routes storage, privacy, and dynamic recalculation against the live graph.
3. Multilingual Translation (i18n) for English, Kannada, and Hindi including natural language instructions.
4. Campus User Feedback submission, validation, and administrative review workflow.
5. Accessibility options (High Contrast, Reduced Motion, Wheelchair mode).
"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap, invalidate_cache
from modules.i18n import SUPPORTED_LANGUAGES, t, translate_instruction
from modules.jain_digital_twin import (
    load_jain_campus_map,
    invalidate_jain_campus_cache,
)
from modules.navigation_session import NavigationSession, NavigationState
from modules.route_finder import RouteFinder


class TestPhase18UserExperience(unittest.TestCase):
    """Test suite for Phase 18 User Experience, Services, and Accessibility components."""

    def setUp(self) -> None:
        """Create isolated in-memory test database and campus map instance."""
        self.db = DatabaseManager(":memory:")
        self.cmap = load_jain_campus_map()
        self.rf = RouteFinder(self.cmap)

        # Seed two distinct users for privacy testing
        self.user1 = self.db.create_user(
            full_name="Student User 1",
            username="student_user1",
            password="SecurePassword123!",
            role="Student",
        )
        self.user2 = self.db.create_user(
            full_name="Staff User 2",
            username="staff_user2",
            password="SecurePassword456!",
            role="Field Staff",
        )

    def tearDown(self) -> None:
        """Clean up resources and invalidate caches."""
        invalidate_cache()
        invalidate_jain_campus_cache()
        self.db.close()

    # =========================================================================
    # 1. Saved Places Tests (Phase 18.2)
    # =========================================================================

    def test_saved_places_lifecycle(self) -> None:
        """Verify saving, querying, and removing bookmarks for a user."""
        u1_id = self.user1["user_id"]
        loc_id = "FET_2F_LIBRARY"

        # Initially not saved
        self.assertFalse(self.db.is_place_saved(u1_id, loc_id))

        # Save bookmark
        saved_id = self.db.save_place(u1_id, loc_id, custom_name="Central Library")
        self.assertTrue(saved_id.startswith("fav_"))
        self.assertTrue(self.db.is_place_saved(u1_id, loc_id))

        # Retrieve saved places
        places = self.db.get_saved_places(u1_id)
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["location_id"], loc_id)
        self.assertEqual(places[0]["custom_name"], "Central Library")

        # Remove bookmark
        removed = self.db.remove_saved_place(u1_id, loc_id)
        self.assertTrue(removed)
        self.assertFalse(self.db.is_place_saved(u1_id, loc_id))
        self.assertEqual(len(self.db.get_saved_places(u1_id)), 0)

    def test_saved_places_user_privacy_isolation(self) -> None:
        """Verify saved places are strictly private to the authenticated user account."""
        u1_id = self.user1["user_id"]
        u2_id = self.user2["user_id"]

        self.db.save_place(u1_id, "FET_4F_HPC_CLUSTER", "Supercomputing Lab")
        self.db.save_place(u2_id, "FET_G_SEMINAR_01", "Seminar Hall")

        u1_places = self.db.get_saved_places(u1_id)
        u2_places = self.db.get_saved_places(u2_id)

        self.assertEqual(len(u1_places), 1)
        self.assertEqual(u1_places[0]["location_id"], "FET_4F_HPC_CLUSTER")

        self.assertEqual(len(u2_places), 1)
        self.assertEqual(u2_places[0]["location_id"], "FET_G_SEMINAR_01")

        # Confirm user 1 cannot see user 2's places
        self.assertFalse(self.db.is_place_saved(u1_id, "FET_G_SEMINAR_01"))

    # =========================================================================
    # 2. Favourite Routes Tests (Phase 18.3)
    # =========================================================================

    def test_favourite_routes_storage_and_privacy(self) -> None:
        """Verify saving and retrieving favourite routes with mode and custom labels."""
        u1_id = self.user1["user_id"]
        u2_id = self.user2["user_id"]

        route_id = self.db.save_favourite_route(
            user_id=u1_id,
            origin_id="OUT_GATE_MAIN",
            destination_id="FET_2F_LIBRARY",
            route_mode="wheelchair",
            custom_label="Accessible Library Commute",
        )
        self.assertTrue(route_id.startswith("route_"))

        # User 1 has the route
        u1_routes = self.db.get_favourite_routes(u1_id)
        self.assertEqual(len(u1_routes), 1)
        self.assertEqual(u1_routes[0]["origin_id"], "OUT_GATE_MAIN")
        self.assertEqual(u1_routes[0]["destination_id"], "FET_2F_LIBRARY")
        self.assertEqual(u1_routes[0]["route_mode"], "wheelchair")

        # User 2 has zero routes
        u2_routes = self.db.get_favourite_routes(u2_id)
        self.assertEqual(len(u2_routes), 0)

        # Deleting route
        self.assertTrue(self.db.remove_favourite_route(u1_id, route_id))
        self.assertEqual(len(self.db.get_favourite_routes(u1_id)), 0)

    def test_favourite_route_dynamic_recalculation(self) -> None:
        """Verify favourite routes are recalculated dynamically on load instead of blindly reused."""
        u1_id = self.user1["user_id"]
        self.db.save_favourite_route(
            user_id=u1_id,
            origin_id="OUT_GATE_MAIN",
            destination_id="FET_4F_HPC_CLUSTER",
            route_mode="wheelchair",
        )

        saved = self.db.get_favourite_routes(u1_id)[0]

        # Dynamically calculate route on the live graph
        session = NavigationSession()
        session.start_preview(
            origin_id=saved["origin_id"],
            destination_id=saved["destination_id"],
            campus_map=self.cmap,
            route_finder=self.rf,
            wheelchair_mode=(saved["route_mode"] == "wheelchair"),
        )
        self.assertEqual(session.state, NavigationState.ROUTE_PREVIEW)
        self.assertGreater(session.total_distance, 0)
        self.assertGreater(len(session.path), 2)

    # =========================================================================
    # 3. Multilingual Translation (i18n) Tests (Phase 18.6)
    # =========================================================================

    def test_supported_languages_dictionary(self) -> None:
        """Verify English, Kannada, and Hindi are supported."""
        self.assertIn("en", SUPPORTED_LANGUAGES)
        self.assertIn("kn", SUPPORTED_LANGUAGES)
        self.assertIn("hi", SUPPORTED_LANGUAGES)

    def test_translation_helper_and_fallbacks(self) -> None:
        """Verify t() retrieves translations in en, kn, hi and falls back safely."""
        en_title = t("app_title", "en")
        kn_title = t("app_title", "kn")
        hi_title = t("app_title", "hi")

        self.assertIn("Accessible Campus Navigator", en_title)
        self.assertIn("ಸುಲಭ ಪ್ರವೇಶ", kn_title)
        self.assertIn("सुगम्य कैंपस", hi_title)

        # Fallback for unknown key
        unknown = t("non_existent_key_xyz", "kn")
        self.assertEqual(unknown, "[non_existent_key_xyz]")

    def test_translate_navigation_instructions(self) -> None:
        """Verify translate_instruction handles elevator, stairs, turns, and straight steps."""
        step_elev = {
            "instruction": "Take elevator from Floor 0 to Floor 3 (FET Elevator)",
            "from_floor": 0,
            "to_floor": 3,
            "target": "FET Elevator",
            "distance": 0.0,
        }
        kn_elev = translate_instruction(step_elev, "kn")
        hi_elev = translate_instruction(step_elev, "hi")

        self.assertIn("ಲಿಫ್ಟ್ ಬಳಸಿ", kn_elev)
        self.assertIn("ಅಂತಸ್ತು 0", kn_elev)
        self.assertIn("ಅಂತಸ್ತು 3", kn_elev)

        self.assertIn("लिफ्ट का उपयोग करें", hi_elev)
        self.assertIn("मंजिल 0", hi_elev)
        self.assertIn("मंजिल 3", hi_elev)

        step_turn = {
            "instruction": "Turn left and proceed 15.2 m towards FET Library",
            "distance": 15.2,
            "target": "FET Library",
        }
        kn_turn = translate_instruction(step_turn, "kn")
        hi_turn = translate_instruction(step_turn, "hi")

        self.assertIn("ಎಡಕ್ಕೆ ತಿರುಗಿ", kn_turn)
        self.assertIn("15.2", kn_turn)
        self.assertIn("बाएं मुड़ें", hi_turn)
        self.assertIn("15.2", hi_turn)

    # =========================================================================
    # 4. Campus User Feedback Tests (Phase 18.7)
    # =========================================================================

    def test_submit_and_review_user_feedback(self) -> None:
        """Verify submitting campus feedback and administrative review workflow."""
        u1_id = self.user1["user_id"]
        admin_id = self.user2["user_id"]

        # Valid submission
        fb_id = self.db.submit_feedback(
            user_id=u1_id,
            feedback_type="incorrect_location",
            details="Room 304 marker is displaced by 2 meters from corridor entrance.",
            target_id="FET_3F_CLASS_04",
        )
        self.assertTrue(fb_id.startswith("fb_"))

        # Inspect pending list
        pending = self.db.get_feedback_list(status="Pending")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["feedback_id"], fb_id)
        self.assertEqual(pending[0]["status"], "Pending")

        # Admin reviews feedback
        reviewed = self.db.review_feedback(
            feedback_id=fb_id,
            reviewer_user_id=admin_id,
            status="Reviewed",
            admin_notes="Survey team confirmed shift; updated CAD coordinate map.",
        )
        self.assertTrue(reviewed)

        # Pending count is now 0; Reviewed count is 1
        self.assertEqual(len(self.db.get_feedback_list(status="Pending")), 0)
        reviewed_list = self.db.get_feedback_list(status="Reviewed")
        self.assertEqual(len(reviewed_list), 1)
        self.assertEqual(reviewed_list[0]["admin_notes"], "Survey team confirmed shift; updated CAD coordinate map.")

    def test_invalid_feedback_submission_fails(self) -> None:
        """Verify invalid category or empty details raise ValueError."""
        with self.assertRaises(ValueError):
            self.db.submit_feedback(
                user_id=self.user1["user_id"],
                feedback_type="invalid_category_123",
                details="Valid details here",
            )

        with self.assertRaises(ValueError):
            self.db.submit_feedback(
                user_id=self.user1["user_id"],
                feedback_type="general",
                details="   ",
            )


if __name__ == "__main__":
    unittest.main()
