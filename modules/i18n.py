"""Internationalization (i18n) and Multilingual Translation Framework.

Provides verified translations for English (en), Kannada (kn), and Hindi (hi)
for campus navigation, UI controls, turn-by-turn guidance, and accessibility notices
without modifying underlying graph identifiers or database IDs.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "kn": "ಕನ್ನಡ (Kannada)",
    "hi": "हिन्दी (Hindi)",
}

DEFAULT_LANGUAGE: str = "en"

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # General & Header
        "app_title": "Accessible Campus Navigator",
        "app_subtitle": "JAIN Global Campus & FET 5-Floor Digital Twin",
        "language_selector": "Language / ಭಾಷೆ / भाषा",
        "high_contrast": "High Contrast Mode",
        "reduced_motion": "Reduced Motion Mode",
        "campus_overview": "Campus Overview",
        
        # Navigation & Route Planner
        "origin": "Starting Point (Origin)",
        "destination": "Destination",
        "navigation_mode": "Navigation Mode",
        "standard_mode": "Standard (Pedestrian)",
        "wheelchair_mode": "Wheelchair Accessible (Step-Free)",
        "calculate_route": "Calculate Route",
        "start_navigation": "Start Navigation",
        "pause_navigation": "Pause",
        "resume_navigation": "Resume",
        "restart_navigation": "Restart",
        "stop_navigation": "End Journey",
        "route_summary": "Route Summary",
        "total_distance": "Total Distance",
        "estimated_time": "Estimated Time",
        "steps_count": "Steps",
        "floors_traversed": "Floors Traversed",
        "rerouted_notice": "Route recalculated due to active obstacle",
        "arrival_notice": "You have arrived at your destination!",
        
        # Directions & Instructions
        "dir_straight": "Continue straight for {distance:.1f} m towards {target}",
        "dir_left": "Turn left and proceed {distance:.1f} m towards {target}",
        "dir_right": "Turn right and proceed {distance:.1f} m towards {target}",
        "dir_elevator": "Take elevator from Floor {from_floor} to Floor {to_floor} ({target})",
        "dir_stairs": "Take staircase from Floor {from_floor} to Floor {to_floor} ({target})",
        "dir_arrive": "Arrive at destination: {destination}",
        "next_instruction": "Next step: {instruction}",
        
        # Saved Places & Favorites
        "saved_places": "Saved Places",
        "favourite_routes": "Favourite Routes",
        "save_this_place": "Save Destination",
        "place_saved": "Location saved to your profile",
        "remove_saved": "Remove",
        "no_saved_places": "No saved places yet.",
        "save_route": "Save Route to Favourites",
        "route_saved": "Route saved to your profile",
        
        # Feedback & Governance
        "user_feedback": "Campus Feedback & Corrections",
        "submit_feedback": "Submit Feedback",
        "feedback_type": "Feedback Category",
        "feedback_details": "Description / Details",
        "feedback_submitted": "Thank you! Feedback submitted for administrative review.",
        "admin_governance": "Administrative Governance",
        "data_confidence": "Data Reliability Confidence",
    },
    "kn": {
        # General & Header
        "app_title": "ಸುಲಭ ಪ್ರವೇಶ ಕ್ಯಾಂಪಸ್ ಮಾರ್ಗದರ್ಶಿ",
        "app_subtitle": "ಜೈನ್ ಗ್ಲೋಬಲ್ ಕ್ಯಾಂಪಸ್ ಮತ್ತು ಎಫ್‌ಇಟಿ 5 ಅಂತಸ್ತಿನ ಡಿಜಿಟಲ್ ನಕ್ಷೆ",
        "language_selector": "ಭಾಷೆ / Language",
        "high_contrast": "ಹೆಚ್ಚಿನ ಕಾಂಟ್ರಾಸ್ಟ್ ಮೋಡ್",
        "reduced_motion": "ಕಡಿಮೆ ಚಲನೆ ಮೋಡ್",
        "campus_overview": "ಕ್ಯಾಂಪಸ್ ಅವಲೋಕನ",
        
        # Navigation & Route Planner
        "origin": "ಪ್ರಾರಂಭದ ಸ್ಥಳ",
        "destination": "ಗಮ್ಯಸ್ಥಾನ",
        "navigation_mode": "ನ್ಯಾವಿಗೇಷನ್ ಮೋಡ್",
        "standard_mode": "ಸಾಮಾನ್ಯ ಪಾದಚಾರಿ ಮಾರ್ಗ",
        "wheelchair_mode": "ಗಾಲಿಕುರ್ಚಿ ಸ್ನೇಹಿ (ಮೆಟ್ಟಿಲುಗಳಿಲ್ಲದ ಮಾರ್ಗ)",
        "calculate_route": "ಮಾರ್ಗವನ್ನು ಲೆಕ್ಕಹಾಕಿ",
        "start_navigation": "ಮಾರ್ಗದರ್ಶನ ಪ್ರಾರಂಭಿಸಿ",
        "pause_navigation": "ವಿರಾಮ",
        "resume_navigation": "ಮುಂದುವರಿಸಿ",
        "restart_navigation": "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ",
        "stop_navigation": "ಪ್ರಯಾಣ ಮುಗಿಸಿ",
        "route_summary": "ಮಾರ್ಗದ ಸಾರಾಂಶ",
        "total_distance": "ಒಟ್ಟು ದೂರ",
        "estimated_time": "ಅಂದಾಜು ಸಮಯ",
        "steps_count": "ಹಂತಗಳು",
        "floors_traversed": "ಅಂತಸ್ತುಗಳು",
        "rerouted_notice": "ತಡೆಯಿರುವ ಕಾರಣ ಪರ್ಯಾಯ ಮಾರ್ಗವನ್ನು ನೀಡಲಾಗಿದೆ",
        "arrival_notice": "ನೀವು ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಲುಪಿದ್ದೀರಿ!",
        
        # Directions & Instructions
        "dir_straight": "{target} ಕಡೆಗೆ {distance:.1f} ಮೀಟರ್ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ",
        "dir_left": "ಎಡಕ್ಕೆ ತಿರುಗಿ {target} ಕಡೆಗೆ {distance:.1f} ಮೀಟರ್ ಸಾಗಿ",
        "dir_right": "ಬಲಕ್ಕೆ ತಿರುಗಿ {target} ಕಡೆಗೆ {distance:.1f} ಮೀಟರ್ ಸಾಗಿ",
        "dir_elevator": "ಅಂತಸ್ತು {from_floor} ರಿಂದ ಅಂತಸ್ತು {to_floor} ಗೆ ಲಿಫ್ಟ್ ಬಳಸಿ ({target})",
        "dir_stairs": "ಅಂತಸ್ತು {from_floor} ರಿಂದ ಅಂತಸ್ತು {to_floor} ಗೆ ಮೆಟ್ಟಿಲುಗಳನ್ನು ಬಳಸಿ ({target})",
        "dir_arrive": "ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಲುಪಿದ್ದೀರಿ: {destination}",
        "next_instruction": "ಮುಂದಿನ ಹಂತ: {instruction}",
        
        # Saved Places & Favorites
        "saved_places": "ಉಳಿಸಿದ ಸ್ಥಳಗಳು",
        "favourite_routes": "ಮೆಚ್ಚಿನ ಮಾರ್ಗಗಳು",
        "save_this_place": "ಸ್ಥಳವನ್ನು ಉಳಿಸಿ",
        "place_saved": "ಸ್ಥಳವನ್ನು ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ",
        "remove_saved": "ತೆಗೆದುಹಾಕಿ",
        "no_saved_places": "ಇನ್ನೂ ಯಾವುದೇ ಸ್ಥಳಗಳನ್ನು ಉಳಿಸಲಾಗಿಲ್ಲ.",
        "save_route": "ಮಾರ್ಗವನ್ನು ಮೆಚ್ಚಿನವುಗಳಿಗೆ ಉಳಿಸಿ",
        "route_saved": "ಮಾರ್ಗವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ",
        
        # Feedback & Governance
        "user_feedback": "ಕ್ಯಾಂಪಸ್ ಪ್ರತಿಕ್ರಿಯೆ ಮತ್ತು ತಿದ್ದುಪಡಿ",
        "submit_feedback": "ಪ್ರತಿಕ್ರಿಯೆ ಸಲ್ಲಿಸಿ",
        "feedback_type": "ವರ್ಗ",
        "feedback_details": "ವಿವರಗಳು",
        "feedback_submitted": "ಧನ್ಯವಾದಗಳು! ಪರಿಶೀಲನೆಗಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ.",
        "admin_governance": "ಆಡಳಿತಾತ್ಮಕ ನಿರ್ವಹಣೆ",
        "data_confidence": "ಡೇಟಾ ನಿಖರತೆಯ ನಂಬಿಕೆ",
    },
    "hi": {
        # General & Header
        "app_title": "सुगम्य कैंपस नेविगेटर",
        "app_subtitle": "जैन ग्लोबल कैंपस और एफईटी 5 मंजिला डिजिटल ट्विन",
        "language_selector": "भाषा / Language",
        "high_contrast": "हाई कंट्रास्ट मोड",
        "reduced_motion": "कम मोशन मोड",
        "campus_overview": "परिसर अवलोकन",
        
        # Navigation & Route Planner
        "origin": "प्रारंभिक स्थान",
        "destination": "गंतव्य स्थान",
        "navigation_mode": "नेविगेशन मोड",
        "standard_mode": "सामान्य पैदल मार्ग",
        "wheelchair_mode": "व्हीलचेयर सुलभ (सीढ़ी-रहित मार्ग)",
        "calculate_route": "मार्ग खोजें",
        "start_navigation": "नेविगेशन शुरू करें",
        "pause_navigation": "रोकें",
        "resume_navigation": "जारी रखें",
        "restart_navigation": "पुनः आरंभ करें",
        "stop_navigation": "यात्रा समाप्त करें",
        "route_summary": "मार्ग सारांश",
        "total_distance": "कुल दूरी",
        "estimated_time": "अनुमानित समय",
        "steps_count": "कदम / चरण",
        "floors_traversed": "तय की गई मंजिलें",
        "rerouted_notice": "सक्रिय बाधा के कारण नया मार्ग तैयार किया गया है",
        "arrival_notice": "आप अपने गंतव्य पर पहुंच गए हैं!",
        
        # Directions & Instructions
        "dir_straight": "{target} की ओर {distance:.1f} मीटर सीधे आगे बढ़ें",
        "dir_left": "बाएं मुड़ें और {target} की ओर {distance:.1f} मीटर बढ़ें",
        "dir_right": "दाएं मुड़ें और {target} की ओर {distance:.1f} मीटर बढ़ें",
        "dir_elevator": "मंजिल {from_floor} से मंजिल {to_floor} तक लिफ्ट का उपयोग करें ({target})",
        "dir_stairs": "मंजिल {from_floor} से मंजिल {to_floor} तक सीढ़ियों का उपयोग करें ({target})",
        "dir_arrive": "गंतव्य पर आगमन: {destination}",
        "next_instruction": "अगला कदम: {instruction}",
        
        # Saved Places & Favorites
        "saved_places": "सहेजे गए स्थान",
        "favourite_routes": "पसंदीदा मार्ग",
        "save_this_place": "यह स्थान सहेजें",
        "place_saved": "स्थान आपकी प्रोफ़ाइल में सहेज लिया गया है",
        "remove_saved": "हटाएं",
        "no_saved_places": "अभी तक कोई स्थान नहीं सहेजा गया।",
        "save_route": "मार्ग को पसंदीदा में सहेजें",
        "route_saved": "मार्ग सफलतापूर्वक सहेज लिया गया है",
        
        # Feedback & Governance
        "user_feedback": "परिसर प्रतिक्रिया एवं सुधार",
        "submit_feedback": "प्रतिक्रिया भेजें",
        "feedback_type": "श्रेणी",
        "feedback_details": "विवरण",
        "feedback_submitted": "धन्यवाद! प्रशासनिक समीक्षा हेतु प्रतिक्रिया दर्ज की गई।",
        "admin_governance": "प्रशासनिक प्रबंधन",
        "data_confidence": "डेटा विश्वसनीयता स्तर",
    },
}


def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """Retrieve translated text string for the given key and language.

    Args:
        key: String key defined in TRANSLATIONS dictionary.
        lang: Language code ('en', 'kn', 'hi'). Defaults to 'en'.
        **kwargs: Variables for template interpolation.

    Returns:
        Interpolated translated string, falling back to English if missing.
    """
    selected_lang = lang if lang in TRANSLATIONS else DEFAULT_LANGUAGE
    lang_dict = TRANSLATIONS.get(selected_lang, TRANSLATIONS["en"])

    template = lang_dict.get(key)
    if template is None:
        # Fallback to English
        template = TRANSLATIONS["en"].get(key, f"[{key}]")

    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template

    return template


def translate_instruction(step: Dict[str, Any], lang: str = "en") -> str:
    """Translate a structured navigation instruction step dict into the target language.

    Args:
        step: Navigation step dictionary with distance, target, instruction type, etc.
        lang: Target language code ('en', 'kn', 'hi').

    Returns:
        Localized natural-language direction string.
    """
    if lang == "en" or lang not in TRANSLATIONS:
        return str(step.get("instruction", ""))

    text = str(step.get("instruction", "")).lower()
    dist = float(step.get("distance", 0.0))
    target = str(step.get("target", step.get("to", "")))
    from_fl = step.get("from_floor", 0)
    to_fl = step.get("to_floor", 0)

    if "elevator" in text:
        return t("dir_elevator", lang, from_floor=from_fl, to_floor=to_fl, target=target)
    elif "stairs" in text or "staircase" in text:
        return t("dir_stairs", lang, from_floor=from_fl, to_floor=to_fl, target=target)
    elif "left" in text:
        return t("dir_left", lang, distance=dist, target=target)
    elif "right" in text:
        return t("dir_right", lang, distance=dist, target=target)
    elif "arrive" in text or "destination" in text:
        return t("dir_arrive", lang, destination=target)
    else:
        return t("dir_straight", lang, distance=dist, target=target)
