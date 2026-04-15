import streamlit as st

from services.auth import register_user, sidebar_login
from services.ui_helpers import inject_custom_css

sidebar_login()
inject_custom_css()

st.title("Create Account")
st.caption("Register as a new claim user")

with st.form("register_page_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Register", use_container_width=True)

if submitted:
    if password != confirm_password:
        st.error("Passwords do not match.")
    else:
        ok, message = register_user(full_name, email, password, role="user")
        if ok:
            st.success(message)
            st.info("Go to the sidebar and log in with your new account.")
        else:
            st.error(message)