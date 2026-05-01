import os
import streamlit as st
import requests
import datetime

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

if not st.session_state.get("token"):
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.markdown("## ❤️ Hypertension Risk Assessment")
patient_name = st.text_input("Patient Full Name *", placeholder="Enter patient name here...")

with st.container(border=True):
    st.markdown("**Biometrics & Lifestyle**")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
    with c2:
        bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=22.50, format="%.2f")
    with c3:
        sleep = st.number_input("Sleep", min_value=0.0, max_value=24.0, value=7.00, format="%.2f")
    with c4:
        salt = st.number_input("Salt", min_value=0.0, max_value=30.0, value=5.00, format="%.2f")
    with c5:
        stress = st.number_input("Stress", min_value=0, max_value=10, value=5)

    st.markdown("<br>**Medical History**", unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        bp_history = st.selectbox("BP History", ["Normal", "Elevated", "High"])
    with m2:
        medication = st.selectbox("Medication", ["nan", "None", "Active Prescriptions"])
    with m3:
        family_history = st.selectbox("Family History", ["No", "Yes"])
    with m4:
        exercise = st.selectbox("Exercise", ["Low", "Moderate", "High"])
    with m5:
        smoking = st.selectbox("Smoking", ["Non-Smoker", "Former Smoker", "Active Smoker"])
        
    notes = st.text_area("Clinical Notes (Optional)")
    run_diagnostic = st.button("RUN & SAVE DIAGNOSTIC", use_container_width=True)

if run_diagnostic:
    if not patient_name.strip():
        st.error("⚠️ Patient Full Name required.")
    else:
        map_family = {"No": 0, "Yes": 1}
        map_smoke = {"Non-Smoker": 0, "Former Smoker": 1, "Active Smoker": 2}
        map_bp = {"Normal": 0, "Elevated": 1, "High": 2}
        map_med = {"nan": 0, "None": 0, "Active Prescriptions": 1}
        map_exercise = {"Low": 0, "Moderate": 1, "High": 2}

        features = [
            float(age), float(salt), float(stress), float(sleep), float(bmi),
            float(map_family[family_history]), float(map_smoke[smoking]),
            float(map_bp[bp_history]), float(map_med[medication]), float(map_exercise[exercise])
        ]

        with st.spinner("Analyzing & Saving..."):
            res = requests.post(f"{API_URL}/ml/predict", json={"features": features}, headers=headers)
            if res.status_code == 200:
                result = res.json()
                if "error" in result:
                    st.error(result['error'])
                else:
                    pred = result["prediction"]
                    risk_label = "HIGH RISK" if pred == 1 else "NOMINAL"
                    payload = {
                        "patient_name": patient_name,
                        "age": float(age),
                        "bmi": float(bmi),
                        "risk_level": risk_label,
                        "details": notes,
                        "recorded_by": st.session_state.get("email", "System User")
                    }
                    save_res = requests.post(f"{API_URL}/patients", json=payload, headers=headers)
                    if save_res.status_code == 200:
                        if pred == 1:
                            st.error(f"### ⚠️ DIAGNOSTIC: HIGH RISK DETECTED\nRecord Saved.")
                        else:
                            st.success(f"### ✅ DIAGNOSTIC: NOMINAL\nRecord Saved.")
                    else:
                        st.error("Failed to save to database.")
            else:
                st.error("Backend communication failed.")