"""Accessible Campus Navigator - Main Application Entrypoint.

This is the primary launcher for the Streamlit multi-page application.
"""

import streamlit as st


def main() -> None:
    """Initialize and run the main Accessible Campus Navigator app."""
    st.set_page_config(
        page_title="Accessible Campus Navigator",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🧭 Accessible Campus Navigator")
    st.write(
        "Welcome to the Accessible Campus Navigator! Use the navigation sidebar "
        "to explore campus maps, plan accessible routes, report obstacles, and view analytics."
    )


if __name__ == "__main__":
    main()
