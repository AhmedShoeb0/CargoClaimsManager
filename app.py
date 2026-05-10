import streamlit as st
from App_Pages.login import login_page
from App_Pages.insurance_claim import insurance_claim_page
from App_Pages.reports import reports_page
from App_Pages.insurance_claim_mail import insurance_claim_page_mail
from App_Pages.reports_mail import reports_page_mail
from App_Pages.logs import logs_page
import base64
import os
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Cargo Claims Manager",
    layout="wide",
    page_icon="✈️"
)



# -------------------------
# Global CSS (Header)
# -------------------------
st.markdown(
    """
    <style>
    .top-header {
        background-color: #003A8F;
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        border-radius: 0 0 8px 8px;
        margin-bottom: 20px;
    }
    .top-header img {
        height: 42px;
    }
    .top-header .title {
        font-size: 22px;
        font-weight: 600;
    }
    .top-header .user {
        font-size: 14px;
        opacity: 0.95;
    }
    .stAppDeployButton {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Initialize session state
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------
# Header renderer
# -------------------------
def render_header():
    first = st.session_state.get("first_name", "")
    last = st.session_state.get("last_name", "")
    full_name = f"{first} {last}".strip()

    st.markdown(
        f"""
        <div class="top-header">
            <div style="display:flex;align-items:center;gap:15px">
                <div class="title"></div>
            </div>
            <div class="user">Welcome, <b>{full_name}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# App routing
# -------------------------
if not st.session_state.logged_in:
    login_page()
    
else:
    render_header()

    # -------------------------
    # Sidebar Navigation
    # -------------------------
    st.sidebar.title("Navigation")

    pages = ["New Claim", "Claim Reports", "New Mail Claim", "Mail Claim Reports"]

    # Admin-only page
    if st.session_state.get("perm_id") == 1:
        pages.append("Administration")

    pages.append("Logout")

    page = st.sidebar.radio(
        "Go to",
        pages
    )

    # -------------------------
    # Page Routing
    # -------------------------
    if page == "New Claim":
        insurance_claim_page()

    elif page == "Claim Reports":
        reports_page()

    elif page == "New Mail Claim":
        insurance_claim_page_mail()

    elif page == "Mail Claim Reports":
        reports_page_mail()

    elif page == "Administration":
        logs_page()

    elif page == "Logout":
        for key in [
            "logged_in",
            "code",
            "first_name",
            "last_name",
            "perm_id"
        ]:
            st.session_state.pop(key, None)

        st.rerun()

components.html(
        """
        <script>
        const doc = window.parent.document;
        
        doc.addEventListener('keydown', function(e) {
            // 1. Navigate through ALL interactive elements with '-'
            if (e.key === '-') {
                e.preventDefault(); 
                // Broaden the selector to include all common form elements
                const focusable = Array.from(doc.querySelectorAll('input, button, select, textarea'));
                
                // Filter out hidden elements (Streamlit sometimes has hidden inputs)
                const visibleElements = focusable.filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' && style.visibility !== 'hidden' && el.type !== 'hidden';
                });

                const index = visibleElements.indexOf(doc.activeElement);
                
                if (index > -1 && index < visibleElements.length - 1) {
                    visibleElements[index + 1].focus();
                } else {
                    // Loop back to the very first visible element
                    if (visibleElements.length > 0) visibleElements[0].focus();
                }
            }

            // 2. Trigger "Log" button with 'Enter'
            if (e.key === 'Enter') {
                const loginBtn = Array.from(doc.querySelectorAll('button')).find(
                    el => el.innerText.includes('Log') || el.innerText.includes('Login')
                );
                if (loginBtn) {
                    loginBtn.click();
                }
            }
        });
        </script>
        """,
        height=0,
    )
