"""Administrative Management Console - User Governance, Role Assignment, Obstacle Queue, and Audit Log."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services, get_current_user

apply_custom_theme()
services = get_app_services()

db_manager = services["db_manager"]
obs_manager = services["obstacle_manager"]
cmap = services["campus_map"]

st.title("🛡️ Administrative Management Console")
st.write(
    "Central governance panel for campus user accounts, operational permissions, "
    "hazard verification queues, and system audit logs."
)

current_user = get_current_user()

# Defensive access check: Only active Administrators may view or operate this page
if not current_user or current_user.get("role") != "Administrator":
    st.error("⛔ **Access Denied**: You must be signed in with an active **Administrator** account to access this console.")
    st.stop()

if current_user.get("account_status") != "Active":
    st.error("⛔ **Access Denied**: Your Administrator account is currently inactive. Please contact system support.")
    st.stop()

# Aggregate statistics directly from database
user_stats = db_manager.get_user_statistics()
obs_stats = obs_manager.get_obstacle_statistics()

# --- TOP METRIC ROW ---
st.subheader("📊 System Governance Overview")
u_col1, u_col2, u_col3, u_col4, u_col5 = st.columns(5)
with u_col1:
    st.metric("Total Registered Users", user_stats["total_users"])
with u_col2:
    st.metric("Active Accounts", user_stats["active_users"])
with u_col3:
    st.metric("Campus Users (Students)", user_stats["role_counts"].get("Student", 0))
with u_col4:
    st.metric("Field Staff", user_stats["role_counts"].get("Field Staff", 0))
with u_col5:
    st.metric("Administrators", user_stats["role_counts"].get("Administrator", 0))

o_col1, o_col2, o_col3, o_col4 = st.columns(4)
with o_col1:
    st.metric("Pending Reports", obs_stats["status_counts"].get("Pending", 0))
with o_col2:
    st.metric("Verified Active Obstacles", obs_stats["active_obstacles_count"])
with o_col3:
    st.metric("Resolved Obstacles", obs_stats["status_counts"].get("Resolved", 0))
with o_col4:
    st.metric("Rejected Reports", obs_stats["status_counts"].get("Rejected", 0))

st.markdown("---")

tab_users, tab_queue, tab_audit = st.tabs([
    "👥 User Management & Roles",
    "⚠️ Obstacle Verification Queue",
    "📜 Administrative Audit Trail",
])

# =============================================================================
# TAB 1: USER MANAGEMENT
# =============================================================================
with tab_users:
    st.subheader("👥 Registered User Directory")
    all_users = db_manager.get_all_users()

    if not all_users:
        st.info("No registered users found in the database.")
    else:
        user_rows = []
        for u in all_users:
            user_rows.append({
                "User ID": u["user_id"],
                "Full Name": u["full_name"],
                "Username": f"@{u['username']}",
                "Role": u["role"],
                "Account Status": u["account_status"],
                "Registered (UTC)": u.get("created_at", "")[:19].replace("T", " "),
                "Updated (UTC)": u.get("updated_at", "")[:19].replace("T", " "),
            })
        df_users = pd.DataFrame(user_rows)
        st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.markdown("### 🔧 Modify User Role or Account Status")
    with st.expander("Update Existing Account Permissions", expanded=False):
        user_options = {
            f"{u['full_name']} (@{u['username']}) - Current: {u['role']} [{u['account_status']}]": u["user_id"]
            for u in all_users
        }
        selected_label = st.selectbox("Select Account to Manage:", options=list(user_options.keys()))
        selected_user_id = user_options[selected_label]
        target_account = db_manager.get_user_by_id(selected_user_id)

        if target_account:
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                new_role = st.selectbox(
                    "Assign Role:",
                    options=list(db_manager.ALLOWED_ROLES),
                    index=list(db_manager.ALLOWED_ROLES).index(target_account["role"]),
                    key="sel_new_role",
                )
            with m_col2:
                new_status = st.selectbox(
                    "Set Account Status:",
                    options=list(db_manager.ALLOWED_USER_STATUSES),
                    index=list(db_manager.ALLOWED_USER_STATUSES).index(target_account["account_status"]),
                    key="sel_new_status",
                )

            if st.button("Apply Permission Updates", type="primary"):
                try:
                    role_changed = False
                    status_changed = False

                    if new_role != target_account["role"]:
                        db_manager.update_user_role(selected_user_id, new_role, actor_user=current_user)
                        role_changed = True

                    if new_status != target_account["account_status"]:
                        db_manager.update_user_status(selected_user_id, new_status, actor_user=current_user)
                        status_changed = True

                    if role_changed or status_changed:
                        st.success(f"Permissions updated successfully for @{target_account['username']}!")
                        st.rerun()
                    else:
                        st.info("No modifications were made (selected role and status match current values).")
                except Exception as ex:
                    st.error(f"Failed to update user: {ex}")

    st.markdown("### ➕ Provision Elevated Staff or Administrator Account")
    with st.expander("Register New Staff / Admin Member", expanded=False):
        with st.form("create_staff_form"):
            prov_name = st.text_input("Full Name:", placeholder="e.g. Campus Officer")
            prov_username = st.text_input("Username:", placeholder="e.g. officer_1")
            prov_role = st.selectbox("Assign Role:", options=["Field Staff", "Administrator", "Student"])
            prov_password = st.text_input("Temporary Password (min 8 chars, letters & numbers):", type="password")

            if st.form_submit_button("Provision Account", type="primary"):
                if not prov_name.strip() or not prov_username.strip():
                    st.error("Please provide both full name and username.")
                elif len(prov_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif not any(c.isdigit() for c in prov_password) or not any(c.isalpha() for c in prov_password):
                    st.error("Password must contain at least one letter and one number.")
                else:
                    try:
                        new_acc = db_manager.create_user(
                            full_name=prov_name.strip(),
                            username=prov_username.strip(),
                            password=prov_password,
                            role=prov_role,
                            account_status="Active",
                            actor_user=current_user,
                        )
                        st.success(f"Account for @{new_acc['username']} created successfully with role **{prov_role}**!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Failed to provision account: {ex}")

# =============================================================================
# TAB 2: OBSTACLE QUEUE
# =============================================================================
with tab_queue:
    st.subheader("⚠️ Pending Obstacle Verification Queue")
    pending_reports = obs_manager.get_reports_by_status("Pending")

    if not pending_reports:
        st.success("✅ The verification queue is clear! No pending obstacle reports require review.")
    else:
        st.info(f"There are **{len(pending_reports)}** pending reports awaiting verification or rejection.")

        for r in pending_reports:
            with st.container():
                st.markdown(
                    f"""
                    <div class="ui-card" style="border-left: 5px solid #d97706;">
                        <div class="ui-card-title">Pending Report #{r['report_id']}</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #1b4332;">{r['obstacle_category']} - Severity: {r['severity']}</div>
                        <div style="font-size: 0.85rem; color: #4a5568; margin-top: 4px;">{r['description']}</div>
                        <div style="font-size: 0.78rem; color: #718096; margin-top: 6px;">
                            Reported by: <b>{r['reporter_name']}</b> | Filed: {str(r['reported_at'])[:19].replace('T', ' ')} UTC
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                q_col1, q_col2 = st.columns([1, 2])
                with q_col1:
                    if st.button(f"✅ Verify & Block Route", key=f"verify_{r['report_id']}", type="primary"):
                        try:
                            obs_manager.verify_report(r["report_id"], actor_user=current_user)
                            st.success(f"Report {r['report_id']} verified. Graph operational state updated.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Failed to verify report: {ex}")

                with q_col2:
                    with st.popover(f"❌ Reject Report #{r['report_id']}"):
                        rej_reason = st.text_input("Rejection Reason:", key=f"rej_reason_{r['report_id']}", placeholder="e.g. Unsubstantiated or duplicate")
                        if st.button("Confirm Rejection", key=f"confirm_rej_{r['report_id']}"):
                            try:
                                obs_manager.reject_report(r["report_id"], rejection_reason=rej_reason, actor_user=current_user)
                                st.info(f"Report {r['report_id']} marked as Rejected.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to reject report: {ex}")

# =============================================================================
# TAB 3: AUDIT TRAIL
# =============================================================================
with tab_audit:
    st.subheader("📜 Administrative & Operational Audit Trail")
    st.write("Immutable chronological record of administrative actions, user role modifications, and obstacle verifications.")

    audit_logs = db_manager.get_audit_logs(limit=100)
    if not audit_logs:
        st.info("No administrative audit entries have been recorded yet.")
    else:
        audit_rows = []
        for a in audit_logs:
            audit_rows.append({
                "Audit ID": a["audit_id"],
                "Timestamp (UTC)": str(a["timestamp"])[:19].replace("T", " "),
                "Actor User ID": a["actor_user_id"],
                "Action": a["action"],
                "Target Type": a["target_type"],
                "Target ID": a["target_id"],
                "Previous State": a["previous_status"] or "-",
                "Resulting State": a["new_status"] or "-",
                "Notes": a["notes"] or "",
            })
        df_audit = pd.DataFrame(audit_rows)
        st.dataframe(df_audit, use_container_width=True, hide_index=True)
