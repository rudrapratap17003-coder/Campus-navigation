"""Authentication Page - User Sign In, Student Registration, and Initial Administrator Setup."""

from __future__ import annotations

import streamlit as st

from modules.ui_theme import (
    apply_custom_theme,
    get_app_services,
    get_current_user,
    login_user,
    logout_user,
)

apply_custom_theme()
services = get_app_services()
db_manager = services["db_manager"]

st.title("🔐 Access & Authentication")
st.write(
    "Secure identity management for Accessible Campus Navigator. Log in to report obstacles, "
    "or manage verification and administrative operations."
)

current_user = get_current_user()

if current_user:
    st.success(f"You are currently signed in as **{current_user['full_name']}** (@{current_user['username']}).")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"""
            <div class="ui-card">
                <div class="ui-card-title">Active Account Profile</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{current_user['full_name']}</div>
                <div style="font-size: 0.85rem; color: #4a5568; margin-bottom: 12px;">User ID: <code>{current_user['user_id']}</code></div>
                <table style="width: 100%; font-size: 0.9rem; line-height: 1.8;">
                    <tr><td style="color: #6c757d; width: 140px;">Username:</td><td><b>@{current_user['username']}</b></td></tr>
                    <tr><td style="color: #6c757d;">Assigned Role:</td><td><span style="background: #e2ece6; color: #1b4332; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{current_user['role']}</span></td></tr>
                    <tr><td style="color: #6c757d;">Account Status:</td><td><b style="color: green;">{current_user['account_status']}</b></td></tr>
                    <tr><td style="color: #6c757d;">Registered:</td><td>{current_user.get('created_at', 'N/A')[:19].replace('T', ' ')} UTC</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="ui-card">
                <div class="ui-card-title">Session Security</div>
                <p style="font-size: 0.82rem; color: #6c757d;">
                    All sensitive obstacle actions are verified against your assigned role.
                    Always sign out when using shared workstations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Sign Out of Session", type="primary", use_container_width=True):
            logout_user()
            st.info("You have been signed out.")
            st.rerun()

else:
    has_admin = db_manager.has_admin_user()

    if not has_admin:
        st.warning(
            "⚠️ **Initial System Setup Required**: No active Administrator account exists in the database. "
            "Please create the primary Administrator account now to initialize system governance."
        )

        with st.form("admin_bootstrap_form"):
            st.subheader("🛡️ Initialize Primary Administrator")
            full_name = st.text_input("Administrator Full Name:", placeholder="e.g. Lead Facilities Manager")
            username = st.text_input("Administrator Username:", placeholder="e.g. admin")
            password = st.text_input("Master Password:", type="password", placeholder="Min 8 characters")
            confirm_pwd = st.text_input("Confirm Master Password:", type="password")

            submitted = st.form_submit_button("Initialize Administrator Account", type="primary")

            if submitted:
                if not full_name.strip() or not username.strip():
                    st.error("Please enter a full name and username.")
                elif len(password) < 8:
                    st.error("Master password must be at least 8 characters long.")
                elif password != confirm_pwd:
                    st.error("Passwords do not match.")
                else:
                    try:
                        admin_user = db_manager.create_user(
                            full_name=full_name.strip(),
                            username=username.strip(),
                            password=password,
                            role="Administrator",
                            account_status="Active",
                        )
                        login_user(admin_user)
                        st.success("Primary Administrator account initialized successfully! You are now logged in.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Initialization failed: {exc}")

    else:
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register New Account"])

        with tab_login:
            st.subheader("Sign In with Your Credentials")
            with st.form("login_form"):
                username = st.text_input("Username:", placeholder="Enter your username")
                password = st.text_input("Password:", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", type="primary")

                if submitted:
                    if not username.strip() or not password:
                        st.error("Please enter both username and password.")
                    else:
                        authenticated = db_manager.authenticate_user(username.strip(), password)
                        if not authenticated:
                            st.error("Invalid username or password. Please check your credentials.")
                        elif authenticated.get("account_status") != "Active":
                            st.error("Your account has been deactivated. Please contact an Administrator.")
                        else:
                            login_user(authenticated)
                            st.success(f"Welcome back, {authenticated['full_name']}!")
                            st.rerun()

        with tab_register:
            st.subheader("Student / Campus User Registration")
            st.info(
                "Self-registration provisions a **Student / Campus User** account with permission to "
                "browse maps, plan accessible routes, and file obstacle reports. Elevated roles (Field Staff, "
                "Administrator) must be assigned by an Administrator."
            )

            with st.form("student_registration_form"):
                reg_name = st.text_input("Full Name:", placeholder="e.g. Alex Johnson")
                reg_username = st.text_input("Desired Username:", placeholder="e.g. alex_j")
                reg_password = st.text_input("Password (min 6 characters):", type="password")
                reg_confirm = st.text_input("Confirm Password:", type="password")

                reg_submitted = st.form_submit_button("Create Campus Account", type="primary")

                if reg_submitted:
                    if not reg_name.strip() or not reg_username.strip():
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            new_user = db_manager.create_user(
                                full_name=reg_name.strip(),
                                username=reg_username.strip(),
                                password=reg_password,
                                role="Student",
                                account_status="Active",
                            )
                            login_user(new_user)
                            st.success("Account created successfully! You are now logged in.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Registration failed: {exc}")
