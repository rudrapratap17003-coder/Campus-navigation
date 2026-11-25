"""Authentication Page - User Sign In, Student Registration, and Initial Administrator Setup."""

from __future__ import annotations

import streamlit as st

from database.db_manager import SecurityLockoutError
from modules.ui_theme import (
    ACCENT_GREEN,
    PRIMARY_GREEN,
    WHITE,
    apply_custom_theme,
    get_app_services,
    get_current_user,
    login_user,
    logout_user,
    render_kpi_card,
)

apply_custom_theme()
services = get_app_services()
db_manager = services["db_manager"]

current_user = get_current_user()

if current_user:
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">👤 Account Profile & Session Management</div>
            <div class="hero-subtitle">
                Authenticated session with active role privileges and administrative routing access.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        role = current_user.get("role", "Student")
        role_badges = {
            "Administrator": '<span class="badge" style="background:rgba(139,92,246,0.2);color:#A78BFA;border:1px solid rgba(139,92,246,0.4);">🛡️ Administrator</span>',
            "Field Staff": '<span class="badge" style="background:rgba(217,119,6,0.2);color:#FBBF24;border:1px solid rgba(217,119,6,0.4);">🛠️ Field Staff</span>',
            "Student": '<span class="badge" style="background:rgba(22,163,106,0.2);color:#35D99A;border:1px solid rgba(53,217,154,0.4);">🎓 Campus User</span>',
        }
        role_badge = role_badges.get(role, f'<span class="badge">{role}</span>')

        st.markdown(
            f"""
            <div class="ui-card">
                <div class="ui-card-title">Identity Credentials</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC; margin-bottom: 2px;">{current_user['full_name']}</div>
                <div style="font-size: 0.85rem; color: #9CAFA5; margin-bottom: 16px;">User ID: <code>{current_user['user_id']}</code></div>
                <div style="display: grid; grid-template-columns: 140px 1fr; gap: 10px; font-size: 0.9rem; border-top: 1px solid rgba(53,217,154,0.12); padding-top: 14px;">
                    <div style="color: #9CAFA5;">Username:</div>
                    <div><b style="color: #F8FAFC;">@{current_user['username']}</b></div>
                    <div style="color: #9CAFA5;">Assigned Role:</div>
                    <div>{role_badge}</div>
                    <div style="color: #9CAFA5;">Account Status:</div>
                    <div><b style="color: #35D99A;">{current_user['account_status']}</b></div>
                    <div style="color: #9CAFA5;">Provisioned:</div>
                    <div style="color: #F8FAFC;">{current_user.get('created_at', 'N/A')[:19].replace('T', ' ')} UTC</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="ui-card">
                <div class="ui-card-title">Session Security Guidelines</div>
                <p style="font-size: 0.85rem; color: #9CAFA5; line-height: 1.5; margin-top: 6px;">
                    Operational barrier verification, route blocking, and user administration are cryptographically gated by your assigned role.
                    Always sign out when using shared campus lab terminals.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Terminate Session & Sign Out", type="primary", width="stretch"):
            logout_user()
            st.info("You have been signed out.")
            st.rerun()

else:
    has_admin = db_manager.has_admin_user()

    if not has_admin:
        st.markdown(
            """
            <div class="hero-banner">
                <div class="hero-title">🛡️ Initial System Setup Required</div>
                <div class="hero-subtitle">
                    No active Administrator account was detected in the database.
                    Please initialize the primary Administrator account below to establish system governance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        center_col1, center_col2, center_col3 = st.columns([1, 2, 1])
        with center_col2:
            st.markdown(
                """
                <div class="ui-card">
                    <div class="ui-card-title">Bootstrap Wizard</div>
                    <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 12px;">Create Lead Administrator Account</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("admin_bootstrap_form"):
                full_name = st.text_input("Administrator Full Name:", placeholder="e.g. Lead Facilities Manager")
                username = st.text_input("Administrator Username:", placeholder="e.g. admin")
                password = st.text_input("Master Password (min 8 chars):", type="password", placeholder="••••••••")
                confirm_pwd = st.text_input("Confirm Master Password:", type="password", placeholder="••••••••")

                submitted = st.form_submit_button("Initialize Administrator Account", type="primary", width="stretch")

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
        st.markdown(
            """
            <div class="hero-banner" style="text-align: center;">
                <div style="font-size: 2.4rem; margin-bottom: 8px;">🔐</div>
                <div class="hero-title">Accessible Campus Navigator</div>
                <div class="hero-subtitle" style="margin: 0 auto;">
                    Secure identity and role-based access control. Sign in to submit barrier reports,
                    verify field obstacles, or access administrative governance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        center_col1, center_col2, center_col3 = st.columns([1, 2, 1])
        with center_col2:
            tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

            with tab_login:
                with st.form("login_form"):
                    st.markdown("<div style='font-size: 0.95rem; font-weight: 700; margin-bottom: 12px; color: #F8FAFC;'>Authenticate to Your Session</div>", unsafe_allow_html=True)
                    username = st.text_input("Username:", placeholder="Enter your username")
                    password = st.text_input("Password:", type="password", placeholder="Enter your password")
                    submitted = st.form_submit_button("Sign In to Portal", type="primary", width="stretch")

                    if submitted:
                        if not username.strip() or not password:
                            st.error("Please enter both username and password.")
                        else:
                            try:
                                authenticated = db_manager.authenticate_user(username.strip(), password)
                                if not authenticated:
                                    st.error("Invalid username or password. Please check your credentials.")
                                elif authenticated.get("account_status") != "Active":
                                    st.error("Your account has been deactivated. Please contact an Administrator.")
                                else:
                                    login_user(authenticated)
                                    st.success(f"Welcome back, {authenticated['full_name']}!")
                                    st.rerun()
                            except SecurityLockoutError as lock_exc:
                                st.error(f"⛔ {lock_exc}")

            with tab_register:
                st.markdown(
                    """
                    <div style="font-size: 0.82rem; color: #9CAFA5; margin-bottom: 12px; line-height: 1.45;">
                        Self-registration provisions a <b>Student / Campus User</b> account with permission to browse maps,
                        calculate accessible routes, and file obstacle reports.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("student_registration_form"):
                    reg_name = st.text_input("Full Name:", placeholder="e.g. Alex Johnson")
                    reg_username = st.text_input("Desired Username:", placeholder="e.g. alex_j")
                    reg_password = st.text_input("Password (min 8 chars, letters & numbers):", type="password")
                    reg_confirm = st.text_input("Confirm Password:", type="password")

                    reg_submitted = st.form_submit_button("Create Campus Account", type="primary", width="stretch")

                    if reg_submitted:
                        if not reg_name.strip() or not reg_username.strip():
                            st.error("Please fill in all required fields.")
                        elif len(reg_password) < 8:
                            st.error("Password must be at least 8 characters long.")
                        elif not any(c.isdigit() for c in reg_password) or not any(c.isalpha() for c in reg_password):
                            st.error("Password must contain at least one letter and one number.")
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
