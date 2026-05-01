import os
import streamlit as st
import requests 
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="NEXUS Access", layout="centered")

def apply_cyber_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0a0a0c; color: #00ffcc; font-family: 'Courier New', monospace; }
        h1, h2, h3 { color: #00ffcc !important; text-shadow: 0 0 5px #00ffcc; }
        .stTextInput > div > div > input, .stNumberInput > div > div > input { background-color: #121212; color: #ff00ff; border: 1px solid #00ffcc; }
        .stButton > button { border: 2px solid #00ffcc; color: #00ffcc; background: transparent; width: 100%; font-weight: bold; }
        .stButton > button:hover { background-color: #00ffcc; color: #000; box-shadow: 0 0 15px #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

apply_cyber_css()

# Initialize session state for the user's "keycard"
if "token" not in st.session_state:
    st.session_state["token"] = None

if st.session_state["token"]:
    st.success("ACCESS GRANTED. Navigate using the sidebar.")
    if st.button("TERMINATE CONNECTION"):
        st.session_state["token"] = None
        st.session_state["role"] = None
        st.session_state["email"] = None
        st.rerun()
else:
    st.title("⚡ NEXUS // MEDICAL_SYSTEM")
    tab1, tab2 = st.tabs(["LOGIN", "INITIALIZE ACCOUNT"])
    
    with tab1:
        email = st.text_input("EMAIL IDENTIFIER", key="log_email")
        pwd = st.text_input("ACCESS CODES", type="password", key="log_pass")
        
        if st.button("UPLINK // LOGIN"):
            res = requests.post(f"{API_URL}/login", json={"email": email, "password": pwd})
            
            if res.status_code == 200:
                data = res.json()
                # Save the token securely in Streamlit's memory
                st.session_state["token"] = data["access_token"]
                st.session_state["role"] = data["role"]
                st.session_state["email"] = email
                st.rerun()
            else:
                st.error("ACCESS DENIED. Invalid credentials.")
                
    with tab2:
        s_name = st.text_input("DESIGNATION (NAME)")
        s_email = st.text_input("EMAIL IDENTIFIER", key="sig_email")
        s_pwd = st.text_input("ENCRYPTION KEY", type="password", key="sig_pass")
        
        if st.button("REGISTER"):
            res = requests.post(f"{API_URL}/signup", json={"name": s_name, "email": s_email, "password": s_pwd})
            
            if res.status_code == 200:
                st.success("ENTITY REGISTERED. Proceed to Login tab.")
            else:
                st.error(res.json().get("detail", "Registration Failed."))
