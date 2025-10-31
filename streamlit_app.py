
import streamlit as st
import requests
import pandas as pd
from fuzzywuzzy import fuzz

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="Bank Document Validator", layout="centered")
st.title("Bank Document Validator")

st.write("Upload a bank cheque or statement image/PDF and enter manual details to validate.")

# File upload
uploaded_file = st.file_uploader("Upload PDF/Image", type=["pdf", "jpg", "jpeg", "png"])

# Manual inputs
acc_name = st.text_input("Account Holder Name")
acc_number = st.text_input("Account Number")
ifsc = st.text_input("IFSC Code")

def parse_table(raw_text, use_fuzzy=True):
    """Convert GPT table text to DataFrame and fix status with case-insensitive/fuzzy matching"""
    rows = []
    for line in raw_text.splitlines():
        if "|" in line and not line.lower().startswith("field"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 4:
                rows.append(parts)
    df = pd.DataFrame(rows, columns=["Field", "Given", "Provided", "Status"])

    # Case-insensitive + optional fuzzy match
    def fix_status(row):
        given = row["Given"].lower()
        provided = row["Provided"].lower()
        if given == provided:
            return "Match"
        elif use_fuzzy and fuzz.ratio(given, provided) > 85:
            return "Near Match"
        return row["Status"]  # Keep original if mismatch or not found

    df["Status"] = df.apply(fix_status, axis=1)
    return df

def highlight_status(val):
    if val.lower() == "match":
        return "background-color: lightgreen"
    elif val.lower() == "near match":
        return "background-color: #fff2cc"  # light yellow
    elif val.lower() == "mismatch":
        return "background-color: #ff9999"
    elif val.lower() == "not found":
        return "background-color: #ffd966"  # darker yellow
    else:
        return ""

if uploaded_file and st.button("Analyze"):
    with st.spinner("Processing document..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        data = {"acc_name": acc_name, "acc_number": acc_number, "ifsc": ifsc}
        try:
            response = requests.post(API_URL, files=files, data=data, timeout=120)
            if response.status_code == 200:
                raw_text = response.text

                # Parse table with case-insensitive/fuzzy status
                df = parse_table(raw_text)
                st.subheader("Validated Results")
                st.table(df.style.applymap(highlight_status, subset=["Status"]))

                # Show final summary
                summary_lines = [line for line in raw_text.splitlines() if "summary" in line.lower()]
                if summary_lines:
                    st.markdown(f"**{summary_lines[-1]}**")
                else:
                    st.markdown("**Final Summary: Not provided**")
            else:
                st.error(f"Server error: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
 