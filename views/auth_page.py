"""Login and registration page."""

import streamlit as st

from services import auth


def render_auth_page() -> None:
    st.markdown("### Sign in to manage your club, teams, and players")

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            st.markdown("### Welcome back")
            login_id = st.text_input("Username or Email", placeholder="Enter username or email")
            login_password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

            if submitted:
                user, error = auth.authenticate_user(login_id, login_password)
                if error:
                    st.error(error)
                else:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.current_page = "🏟️ Club Management"
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            st.markdown("### Create your account")
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    user, error = auth.register_user(username, email, password)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["id"]
                        st.session_state.username = user["username"]
                        st.session_state.current_page = "🏟️ Club Management"
                        st.success("Account created! Redirecting to Club Management...")
                        st.rerun()
