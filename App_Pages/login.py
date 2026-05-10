import streamlit as st
import pandas as pd
from Core.DB_Connection import get_connection

def login_page():
    st.title("🔐 Login")

    cols = st.columns([1, 2, 1])
    with cols[1]:
        code = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.write("")

        if st.button("Login", type="primary"):
            if not code or not password:
                st.warning("Please enter username and password")
                return

            try:
                engine = get_connection()

                query = """
                    SELECT
                        Code,
                        FirstName,
                        LastName,
                        permID,
                        Active
                    FROM Accounts
                    WHERE Code = ?
                      AND pass = ?
                """

                df = pd.read_sql(
                    query,
                    engine,
                    params=(code, password)
                )

                if df.empty:
                    st.error("❌ Invalid username or password")
                    return

                user = df.iloc[0]

                # Check if user is active
                if not user["Active"]:
                    st.error("🚫 This account is deactivated. Please contact the administrator.")
                    return

                # -------------------------
                # Save login session
                # -------------------------
                st.session_state.logged_in = True
                st.session_state.code = user["Code"]
                st.session_state.first_name = user["FirstName"]
                st.session_state.last_name = user["LastName"]
                st.session_state.perm_id = user["permID"]

                st.success("✅ Login successful")
                st.rerun()

            except Exception as e:
                st.error(f"Database error: {e}")
