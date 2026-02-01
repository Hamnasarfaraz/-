import streamlit as st
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Medical Diagnosis Assistant",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "diagnosis"

if "personal_done" not in st.session_state:
    st.session_state.personal_done = False

if "history" not in st.session_state:
    st.session_state.history = []

# Ensure old history entries have confidence field
for h in st.session_state.history:
    if 'confidence' not in h:
        h['confidence'] = 0  # default confidence for old entries

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Medical Assistant")

    if st.button("New Diagnosis"):
        st.session_state.page = "diagnosis"
        st.session_state.personal_done = False

    if st.button("History"):
        st.session_state.page = "history"

    st.divider()
    st.caption(
        "This AI Tool is developed by **Hamna Sarfaraz**.\n\n"
        "Note: This system provides preliminary health guidance only. "
        "Prioritize consulting a doctor for serious concerns."
    )

# ---------------- MEDICAL ANALYSIS LOGIC ----------------
def analyze(data):
    text = " ".join(data["additional"]).lower()

    condition = "General Observation"
    prescription = []
    care = []
    alert = "Monitor symptoms."
    confidence = 30  # base confidence

    # ---------------- FEVER ----------------
    if data["main_symptom"] == "Fever":
        confidence += 30
        if data["fever"] in ["Moderate", "High"]:
            condition = "Acute Febrile Illness"
            prescription = ["Paracetamol", "ORS"]
            care = ["Adequate hydration", "Rest", "Tepid sponging"]
            confidence += 15
        else:
            condition = "Mild Viral Fever"
            prescription = ["Paracetamol"]
            care = ["Rest", "Fluids"]

    # ---------------- HEADACHE ----------------
    elif data["main_symptom"] == "Headache":
        confidence += 30
        if "eye" in text or "behind" in text:
            condition = "Sinus-related Headache"
            prescription = ["Pain reliever (OTC)", "Saline nasal spray"]
            care = ["Steam inhalation", "Warm compress"]
            confidence += 20
        elif "spinning" in text or "dizziness" in text:
            condition = "Migraine or Vestibular Headache"
            prescription = ["Pain reliever (OTC)", "Anti-nausea medication"]
            care = ["Dark quiet room", "Avoid screen exposure"]
            confidence += 25
        else:
            condition = "Tension Headache"
            prescription = ["Pain reliever (OTC)"]
            care = ["Stress reduction", "Adequate sleep"]

    # ---------------- COUGH ----------------
    elif data["main_symptom"] == "Cough":
        confidence += 30
        if "chest" in text or "shortness" in text:
            condition = "Lower Respiratory Tract Infection"
            prescription = ["Cough syrup", "Warm fluids"]
            care = ["Avoid cold air", "Rest"]
            confidence += 20
        else:
            condition = "Upper Respiratory Infection"
            prescription = ["Cough syrup"]
            care = ["Steam inhalation", "Hydration"]

    # ---------------- STOMACH PAIN ----------------
    elif data["main_symptom"] == "Stomach Pain":
        confidence += 30
        if "vomiting" in text or "diarrhea" in text:
            condition = "Gastroenteritis"
            prescription = ["ORS", "Antiemetic"]
            care = ["Light diet", "Avoid oily food"]
            confidence += 20
        else:
            condition = "Gastritis"
            prescription = ["Antacid"]
            care = ["Small frequent meals"]

    # ---------------- BODY PAIN ----------------
    elif data["main_symptom"] == "Body Pain":
        confidence += 30
        condition = "Musculoskeletal Pain or Viral Body Ache"
        prescription = ["Pain reliever (OTC)"]
        care = ["Rest", "Warm compress"]

    # ---------------- SORE THROAT ----------------
    elif data["main_symptom"] == "Sore Throat":
        confidence += 30
        condition = "Throat Infection / Pharyngitis"
        prescription = ["Lozenges", "Warm salt water gargle"]
        care = ["Hydration", "Rest"]
        if "fever" in text:
            confidence += 15

    # ---------------- NAUSEA ----------------
    elif data["main_symptom"] == "Nausea":
        confidence += 30
        condition = "Gastrointestinal Upset"
        prescription = ["Antiemetic"]
        care = ["Light diet", "Hydration"]
        if "vomiting" in text:
            confidence += 15

    # ---------------- RASH ----------------
    elif data["main_symptom"] == "Rash":
        confidence += 30
        condition = "Skin Allergy / Infection"
        prescription = ["Antihistamines"]
        care = ["Avoid allergens", "Keep skin clean"]
        if "itching" in text:
            confidence += 10

    # ---------------- DIZZINESS ----------------
    elif data["main_symptom"] == "Dizziness":
        confidence += 30
        condition = "Vertigo / Low Blood Pressure"
        prescription = ["Hydration", "Rest"]
        care = ["Avoid sudden movements", "Sit if dizzy"]
        if "spinning" in text:
            confidence += 15

    # ---------------- ESCALATION RULES ----------------
    if data["duration"] == "More than 5 days":
        alert = "Doctor consultation is strongly advised."
        confidence += 15

    if data["pain_level"] in ["Moderate", "Severe"]:
        confidence += 10

    if data["condition"] != "None":
        alert = "Consult a doctor due to existing medical condition."
        confidence += 10

    confidence = min(confidence, 95)

    return condition, prescription, care, alert, confidence

# ---------------- HISTORY PAGE ----------------
if st.session_state.page == "history":
    st.title("Diagnosis History")

    if not st.session_state.history:
        st.info("No previous diagnoses found.")
    else:
        # Simple text format
        for h in reversed(st.session_state.history):
            conf = h.get('confidence', 0)
            st.markdown(f"""
            **Date:** {h['time']}  
            **Name:** {h['name']}  
            **Main Symptom:** {h['symptom']}  
            **Diagnosis:** {h['condition']}  
            **Confidence:** {conf}%
            """)
            st.divider()

# ---------------- DIAGNOSIS PAGE ----------------
else:
    st.title("Medical Pre-Diagnosis System")
    st.caption("This system provides preliminary medical guidance only.")

    # ---------- FORM 1 ----------
    with st.form("personal_form"):
        st.subheader("Personal Information")

        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])

        submit_personal = st.form_submit_button("Proceed")

    if submit_personal:
        st.session_state.personal_done = True
        st.session_state.user = {"name": name}

    # ---------- FORM 2 ----------
    if st.session_state.personal_done:
        with st.form("medical_form"):
            st.subheader("Medical Details")

            col1, col2 = st.columns(2)

            with col1:
                main_symptoms_list = [
                    "Fever", "Cough", "Headache", "Stomach Pain", "Body Pain",
                    "Sore Throat", "Nausea", "Fatigue", "Back Pain",
                    "Shortness of Breath", "Rash", "Dizziness"
                ]
                main_symptom = st.selectbox("Main Symptom", main_symptoms_list)

                duration = st.selectbox(
                    "Symptom Duration",
                    ["1–2 days", "3–5 days", "More than 5 days"]
                )

                fever_level = st.selectbox(
                    "Fever Level",
                    ["None", "Mild", "Moderate", "High"]
                )

            with col2:
                pain_level = st.selectbox(
                    "Pain Level",
                    ["Mild", "Moderate", "Severe"]
                )

                existing_condition = st.selectbox(
                    "Existing Medical Condition",
                    ["None", "Diabetes", "Blood Pressure", "Asthma"]
                )

            additional_symptoms_list = [
                "Fatigue", "Vomiting", "Diarrhea", "Chest Pain", "Runny Nose",
                "Loss of Appetite", "Sweating", "Shortness of Breath", "Rash",
                "Dizziness", "Blurred Vision", "Sore Throat", "Muscle Weakness",
                "Joint Pain", "Nausea"
            ]
            additional_symptoms = st.multiselect("Additional Symptoms", additional_symptoms_list)

            manual_symptoms = st.text_area("Other symptoms (optional)")

            submit_medical = st.form_submit_button("Analyze")

        if submit_medical:
            input_data = {
                "main_symptom": main_symptom,
                "duration": duration,
                "fever": fever_level,
                "pain_level": pain_level,
                "additional": additional_symptoms + [manual_symptoms],
                "condition": existing_condition
            }

            condition, meds, care, alert, confidence = analyze(input_data)

            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "name": st.session_state.user["name"],
                "symptom": main_symptom,
                "condition": condition,
                "confidence": confidence
            })

            st.divider()
            st.subheader("Diagnosis Result")

            st.success(condition)
            st.metric("Confidence Score", f"{confidence}%")

            st.markdown("**Prescription**")
            for m in meds:
                st.write("-", m)

            st.markdown("**Care Guidelines**")
            for c in care:
                st.write("-", c)

            st.warning(alert)
