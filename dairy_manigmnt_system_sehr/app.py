import streamlit as st
from datetime import datetime
from dairy_backend import DairyDB, export_pdf

st.title("🐄 Dairy Entry App")
db = DairyDB()

name = st.text_input("Customer Name")
date = st.date_input("Date", value=datetime.today()).strftime("%Y-%m-%d")
shift = st.selectbox("Shift", ["Morning", "Evening"])
mound = st.number_input("Mound", min_value=0.0, format="%.2f", value=0.0)
kg = st.number_input("Kg", min_value=0.0, format="%.2f", value=0.0)
rate = st.number_input("Rate (optional)", min_value=0.0, format="%.2f", value=0.0)

if st.button("Add Entry"):
    if not name.strip():
        st.error("Please enter a Customer Name.")
    elif mound == 0 and kg == 0:
        st.error("Please enter either Mound or Kg value.")
    else:
        db.add_record(name, date, shift, mound, kg, rate)
        st.success("Record added successfully.")

records = db.get_all_records(name)

if records:
    st.subheader(f"All Records for {name}")
    for rec in records:
        rec_id, _, date, shift, mound, kg, rate = rec
        st.write(f"📅 {date} | Shift: {shift} | Mound: {mound} | Kg: {kg} | Rate: {rate if rate else '-'} | Total: {mound * rate if rate else '-'}")
        if st.button(f"Delete Entry {rec_id}", key=f"delete_{rec_id}"):
            db.delete_record(rec_id)
            st.rerun()

    if st.button("📄 Export PDF"):
        pdf_data = export_pdf(name, records)
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name=f"{name}_dairy_report.pdf",
            mime="application/pdf"
        )
else:
    st.info("No records found for this customer.")
