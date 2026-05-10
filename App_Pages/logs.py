import streamlit as st
import pandas as pd
from datetime import datetime
from Core.DB_Connection import get_connection
from Core.functions import insert_log

def logs_page():
    # 🔐 ADMIN ONLY
    if st.session_state.get("perm_id") != 1:
        st.error("Access denied")
        st.stop()

    engine = get_connection()

    # ==============================
    # LOGS SECTION
    # ==============================
    st.subheader("📜 User Logs")

    logs_query = """
        SELECT
            log_action AS 'Action Performed',
            log_datetime AS 'Action Date & Time',
            insurance_num AS 'Affected Insurance Number',
            user_name AS 'Performed By',
            user_code AS 'User Code'
        FROM User_Logs
        ORDER BY log_datetime DESC
    """

    logs_df = pd.read_sql(logs_query, engine)

    st.dataframe(logs_df, width="stretch", hide_index=True)

    st.divider()

    st.subheader("User Management")

    engine = get_connection()

    # VIEW USERS (TOP SECTION)
    st.markdown("Existing Users")

    try:
        query = """
            SELECT 
                a.Code,
                a.FirstName, 
                a.LastName, 
                p.permName, 
                a.Active,
                a.creationBy As 'Modified By',
			    a.creationDate As 'Modifying  date'
            FROM Accounts a
            LEFT JOIN Permission p ON p.permID = a.permID
            ORDER BY Code
        """
        df_users = pd.read_sql(query, engine)
        st.dataframe(df_users, width="stretch", hide_index=True)
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return

    st.divider()

    # LOAD PERMISSIONS (TEXT + ID)
    perm_query = "SELECT permID, permName FROM Permission ORDER BY permName"
    perm_df = pd.read_sql(perm_query, engine)

    # Map name -> ID
    perm_dict = dict(zip(perm_df["permName"], perm_df["permID"]))

    # MANAGE USER
    st.subheader("Manage User")

    user_code = st.text_input("User Code")

    first_name_default = ""
    last_name_default = ""
    active_default = True
    selected_perm_name = list(perm_dict.keys())[0]
    user_exists = False

    # ==============================
    # LOAD USER IF EXISTS
    # ==============================
    if user_code.strip():

        load_query = """
            SELECT Code, FirstName, LastName, permID, Active
            FROM Accounts
            WHERE Code = ?
        """

        df_user = pd.read_sql(load_query, engine, params=(user_code,))

        if not df_user.empty:
            user_exists = True
            selected_user = df_user.iloc[0]

            first_name_default = selected_user["FirstName"]
            last_name_default = selected_user["LastName"]
            active_default = bool(selected_user["Active"])

            # Find permission name from ID
            for name, pid in perm_dict.items():
                if pid == selected_user["permID"]:
                    selected_perm_name = name
                    break

            st.success("User loaded")
        else:
            st.warning("User not found → New user will be created")

    # FORM 
    co1, co2 = st.columns(2)
    with co1:
        first_name = st.text_input("First Name", value=first_name_default)
        password = st.text_input("Password", type="password")
        active = st.checkbox("Active", value=active_default)
    with co2:
        last_name = st.text_input("Last Name", value=last_name_default)

        selected_perm_name = st.selectbox(
            "Permission",
            options=list(perm_dict.keys()),
            index=list(perm_dict.keys()).index(selected_perm_name)
        )

        perm_id = perm_dict[selected_perm_name]



    col1, col2 = st.columns(2)

    # SAVE (INSERT OR UPDATE)
    with col1:
        if st.button("Save", type="primary"):

            if not user_code.strip():
                st.error("User Code is required")
                st.stop()

            try:
                with engine.begin() as conn:

                    if user_exists:
                        # UPDATE
                        if password.strip():
                            conn.exec_driver_sql("""
                                UPDATE Accounts
                                SET FirstName = ?,
                                    LastName = ?,
                                    pass = ?,
                                    permID = ?,
                                    Active = ?,
                                    creationDate =?,
                                    creationBy = ?
                                WHERE Code = ?
                            """, (first_name, last_name, password, perm_id, int(active), datetime.now(), 
                                 st.session_state.get("code"), user_code))
                        else:
                            conn.exec_driver_sql("""
                                UPDATE Accounts
                                SET FirstName = ?,
                                    LastName = ?,
                                    permID = ?,
                                    Active = ?,
                                    creationDate =?,
                                    creationBy = ?
                                WHERE Code = ?
                            """, (first_name, last_name, perm_id, int(active), datetime.now(), 
                                  st.session_state.get("code"), user_code))

                        st.success("✅ User updated successfully")
                        insert_log(action="User " + user_code +" Updated")

                    else:
                        # INSERT (WITH creationDate & creationBy)
                        if not password.strip():
                            st.error("Password required for new user")
                            st.stop()

                        conn.exec_driver_sql("""
                            INSERT INTO Accounts
                            (Code, FirstName, LastName, pass, permID, Active, creationDate, creationBy)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_code,
                            first_name,
                            last_name,
                            password,
                            perm_id,
                            int(active),
                            datetime.now(),
                            st.session_state.get("code")
                        ))

                        st.success("✅ User created successfully")
                        insert_log(action="New User " + user_code +" Added")

                st.rerun()

            except Exception as e:
                st.error(f"Operation failed: {e}")
