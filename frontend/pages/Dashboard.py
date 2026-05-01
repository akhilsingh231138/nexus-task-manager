import os
import streamlit as st
import requests
import pandas as pd

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

if not st.session_state.get("token"):
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("🗄️ PATIENT RECORDS DATABASE")
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search_name = st.text_input("Search by Patient Name")
    with c2:
        filter_risk = st.selectbox("Filter Risk", ["All", "HIGH RISK", "NOMINAL"])
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        execute_search = st.button("EXECUTE QUERY", use_container_width=True)

if execute_search or "patient_data" not in st.session_state:
    params = {}
    if search_name:
        params["name"] = search_name
    if filter_risk != "All":
        params["risk"] = filter_risk
    res = requests.get(f"{API_URL}/patients", headers=headers, params=params)
    if res.status_code == 200:
        st.session_state["patient_data"] = res.json()

data = st.session_state.get("patient_data", [])
if not data:
    st.info("No records found.")
else:
    df = pd.DataFrame(data)
    m1, m2, m3 = st.columns(3)
    m1.metric("TOTAL RECORDS", len(df))
    m2.metric("HIGH RISK", len(df[df['risk_level'] == 'HIGH RISK']))
    m3.metric("NOMINAL", len(df[df['risk_level'] == 'NOMINAL']))
    st.dataframe(df[['record_id', 'timestamp', 'patient_name', 'age', 'risk_level', 'recorded_by']], use_container_width=True, hide_index=True)