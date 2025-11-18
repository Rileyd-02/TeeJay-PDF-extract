import streamlit as st
import pdfplumber
import pandas as pd
import re
import io
st.set_page_config(page_title="Teejay Data Extractor", page_icon="📄")
st.title("📄 Teejay Data Extractor")
st.write("Upload PIs in the SAME FORMAT as samples. The tool extracts:")
st.write("- PO Number\n- Customer Material\n- Delivery Date (Ex Mill)\n- Quantity In")
# ---------- Extraction Function ----------
def extract_from_pdf(pdf_file):
   text = ""
   with pdfplumber.open(pdf_file) as pdf:
       for page in pdf.pages:
           text += page.extract_text() + "\n"
   # Regex patterns based on provided sample PDFs
   pattern = re.compile(
       r"(\d+\.\d+)\s+(?P<PO>\d{10})\s+(?P<CustomerMat>\d{10})"
       r".*?\n(?P<DelDate>\d{2}\.\d{2}\.\d{4})\s+(?P<UnitPrice>\d+\.\d+)\s+(?P<Total>\d+\.\d+)",
       re.DOTALL
   )
   records = []
   quantities = re.findall(r"\n(\d+\.\d+)\s+\d{10}\s+\d{10}", text)
   for match, qty in zip(pattern.finditer(text), quantities):
       records.append({
           "PO NO": match.group("PO"),
           "Customer Material": match.group("CustomerMat"),
           "DEL date ex mill": match.group("DelDate"),
           "Quantity in": qty
       })
   return pd.DataFrame(records)

# ---------- Streamlit UI ----------
uploaded_files = st.file_uploader("Upload PI PDFs", type="pdf", accept_multiple_files=True)
if st.button("Extract Stretchline Data"):
   if not uploaded_files:
       st.warning("Please upload at least one PDF.")
       st.stop()
   final_df = pd.DataFrame()
   for pdf_file in uploaded_files:
       df = extract_from_pdf(pdf_file)
       df["Source File"] = pdf_file.name
       final_df = pd.concat([final_df, df], ignore_index=True)
   if final_df.empty:
       st.error("No valid records found. Check file format.")
       st.stop()
   st.success("Extraction complete! Download your Stretchline Data file.")
   # Output Excel
   output = io.BytesIO()
   with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
       final_df.to_excel(writer, index=False, sheet_name="Stretchline Data")
   output.seek(0)
   st.download_button(
       label="⬇️ Download Stretchline_Data.xlsx",
       data=output,
       file_name="Stretchline_Data.xlsx",
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
   )
   st.dataframe(final_df)