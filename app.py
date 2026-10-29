from datetime import datetime
import io
import pandas as pd
import streamlit as st

from database import get_connection, authenticate_user, create_user, get_next_receipt_number, init_db
from receipt_template import generate_receipt_html

# Page Configuration
st.set_page_config(
    page_title="District Administration - Jan Sunwai",
    page_icon="🏛️",
    layout="wide",
)

# Initialize DB and default users
init_db()

# Session State Initialization for Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown(
            """
            <div style="background-color: #1b365d; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2>🏛️ Jan Sunwai Portal</h2>
                <p>District Administration Login</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("🔒 Secure Login", use_container_width=True)
            
            if submit_login:
                user = authenticate_user(username_input, password_input)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.role = user[1]
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
        
        st.info("💡 **Default Login Note:** Set via your secure environment/secrets.")
    
    st.stop()

# ==========================================
# MAIN APP (Post-Login)
# ==========================================
st.markdown(
    """
    <style>
        .stApp { background-color: #fafafa; }
        .main-header {
            background-color: #1b365d; color: white; padding: 15px;
            text-align: center; font-size: 20px; font-weight: bold;
            border-radius: 5px; margin-bottom: 15px;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            height: 45px; white-space: pre-wrap; background-color: #ffffff;
            border-radius: 5px 5px 0 0; padding: 10px 20px; font-weight: bold;
        }
        .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar User Info, Logout & Admin Options
with st.sidebar:
    st.write(f"👤 Logged in as: **{st.session_state.username}**")
    st.write(f"🔑 Role: **{st.session_state.role.capitalize()}**")
    st.markdown("---")
    
    # Admin-only user registration tool
    if st.session_state.role == "admin":
        with st.expander("🛠️ Admin: Create New User"):
            with st.form("new_user_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                new_role = st.selectbox("Role", ["operator", "admin"])
                create_btn = st.form_submit_button("Create User", use_container_width=True)
                
                if create_btn:
                    if not new_username.strip() or not new_password.strip():
                        st.error("Please fill in both fields.")
                    else:
                        success, msg = create_user(new_username, new_password, new_role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
        st.markdown("---")

    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

st.markdown('<div class="main-header">कार्यालय कलेक्टर - जन आवेदन (Jan Sunwai)</div>', unsafe_allow_html=True)

tab_register, tab_records = st.tabs([
    "📝 New Grievance Registration",
    "📊 View & Export Records"
])

# ==========================================
# TAB 1: NEW GRIEVANCE REGISTRATION
# ==========================================
with tab_register:
    today_str = datetime.now().strftime("%d/%m/%Y")

    def reset_form():
        auto_receipt = get_next_receipt_number(today_str)
        st.session_state.form_data = {
            "receipt_no": auto_receipt,
            "receipt_date": today_str,
            "applicant_name": "",
            "applicant_address": "",
            "subject": "",
            "marked_office": "",
            "details": "",
        }
        st.session_state.show_receipt = False

    if "form_data" not in st.session_state:
        reset_form()

    def fill_mock_data():
        mock_date = "16/06/2026"
        auto_receipt = get_next_receipt_number(mock_date)
        st.session_state.form_data = {
            "receipt_no": auto_receipt,
            "receipt_date": mock_date,
            "applicant_name": "कल्ला जाटव पुत्र हरजीत जाटव ७७७२०१८७५७",
            "applicant_address": "दुबाबली तहसील विजयपुर",
            "subject": "प्रार्थी का प्रधानमंत्री आवास योजना में अभी तक नाम नही जोडने बावत",
            "marked_office": "CEO JP Vijaipur - CEO JP Vijaipur",
            "details": "प्रार्थी का प्रधानमंत्री आवास योजना में अभी तक नाम नहीं जोड़ा गया है।",
        }

    _, form_col, _ = st.columns([1, 2, 1])

    with form_col:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("⚡ Load Mock Data", on_click=fill_mock_data, use_container_width=True)
        with col_btn2:
            st.button("🔄 Reset Form", on_click=reset_form, use_container_width=True)

        with st.form("grievance_form"):
            fd = st.session_state.form_data
            receipt_date = st.text_input("Receipt Date (DD/MM/YYYY)", value=fd["receipt_date"])
            current_auto_receipt = get_next_receipt_number(receipt_date)

            applicant_name = st.text_input("Applicant Name & Mobile *", value=fd["applicant_name"])
            applicant_address = st.text_input("Applicant Address *", value=fd["applicant_address"])
            subject = st.text_input("Subject *", value=fd["subject"])
            marked_office = st.text_input("Marked Office *", value=fd["marked_office"])
            details = st.text_area("Details / Grievance Description", value=fd["details"])

            submitted = st.form_submit_button("Save to Database & Prepare Receipt", use_container_width=True)

        if submitted:
            if not applicant_name.strip() or not applicant_address.strip() or not subject.strip() or not marked_office.strip():
                st.error("⚠️ Please fill out all mandatory fields!")
            else:
                try:
                    conn = get_connection()
                    with conn.session as s:
                        s.execute(
                            text("""
                                INSERT INTO grievances (receipt_no, receipt_date, print_datetime, applicant_name, applicant_address, subject, marked_office, details)
                                VALUES (:receipt_no, :receipt_date, :print_datetime, :applicant_name, :applicant_address, :subject, :marked_office, :details)
                            """),
                            {
                                "receipt_no": current_auto_receipt,
                                "receipt_date": receipt_date,
                                "print_datetime": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "applicant_name": applicant_name,
                                "applicant_address": applicant_address,
                                "subject": subject,
                                "marked_office": marked_office,
                                "details": details,
                            },
                        )
                        s.commit()
                    st.success(f"Grievance #{current_auto_receipt} saved to Neon DB!")
                    st.session_state.show_receipt = True
                    st.session_state.latest_saved_receipt = {
                        "receipt_no": current_auto_receipt,
                        "receipt_date": receipt_date,
                        "applicant_name": applicant_name,
                        "applicant_address": applicant_address,
                        "subject": subject,
                        "marked_office": marked_office,
                        "details": details,
                    }
                except Exception as e:
                    st.error(f"Database Error: {e}")

    if st.session_state.get("show_receipt", False):
        saved_data = st.session_state.get("latest_saved_receipt", fd)
        st.markdown("---")
        st.subheader("🖨️ Receipt Preview & Print")

        component_html = generate_receipt_html(saved_data)
        st.components.v1.html(component_html, height=720, scrolling=True)

        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            if st.button("✅ Done / Start New Entry", type="primary", use_container_width=True):
                reset_form()
                st.rerun()


# ==========================================
# TAB 2: VIEW & EXPORT RECORDS
# ==========================================
with tab_records:
    st.subheader("🔍 Filter & View Grievance Records (Aavedan)")

    with st.form("filter_form"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now())
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())

        search_submitted = st.form_submit_button("🔎 Search / Filter Records", use_container_width=True)

    conn = get_connection()
    df = conn.query("SELECT * FROM grievances ORDER BY id DESC", ttl=0)

    if not df.empty:
        df["parsed_date"] = pd.to_datetime(
            df["receipt_date"], format="%d/%m/%Y", errors="coerce"
        ).dt.date
        filtered_df = df[
            (df["parsed_date"] >= start_date) & (df["parsed_date"] <= end_date)
        ].copy()
        filtered_df = filtered_df.drop(columns=["parsed_date"])

        st.markdown(f"**Total Records Found:** `{len(filtered_df)}`")

        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="Grievances")
            excel_data = excel_buffer.getvalue()

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button(
                    label="📥 Export Filtered Data to Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"jan_sunwai_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with col_exp2:
                csv_data = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Export Filtered Data to CSV",
                    data=csv_data,
                    file_name=f"jan_sunwai_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.warning("No records found for the selected date range.")
    else:
        st.info("No grievance records registered in the database yet.")