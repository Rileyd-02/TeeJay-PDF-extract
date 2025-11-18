import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="Stretchline Data Extractor", page_icon="📄")
st.title("📄 Stretchline Data Extractor")
st.write("Automatically extract Quantity, PO Number, Customer Material and EX Mill Delivery Date from Teejay PIs.")


# --------------------------------------------------------

# FUNCTION TO EXTRACT ROWS FROM A SINGLE PDF

# --------------------------------------------------------

def extract_rows_from_pdf(pdf_file):

    all_text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                all_text += page_text + "\n"

    # Clean text

    all_text = all_text.replace(",", "")  # Remove commas in numbers to simplify

    # Regex that matches the exact structure in your highlighted screenshot

    pattern = re.compile(

        r"(?P<qty>\d+\.\d+)\s+"

        r"(?P<po>\d{10})\s+"

        r"(?P<custmat>\d{10}).*?\n.*?"

        r"(?P<deldate>\d{2}\.\d{2}\.\d{4})",

        re.DOTALL

    )

    rows = []

    for match in pattern.finditer(all_text):

        rows.append({

            "Quantity in": match.group("qty"),

            "PO Number": match.group("po"),

            "Customer Material": match.group("custmat"),

            "DEL date ex mill": match.group("deldate")

        })

    return pd.DataFrame(rows)


# --------------------------------------------------------

# STREAMLIT UI

# --------------------------------------------------------

uploaded_files = st.file_uploader(

    "Upload Teejay PI PDFs",

    type="pdf",

    accept_multiple_files=True

)

if st.button("Extract Stretchline Data"):

    if not uploaded_files:

        st.warning("Please upload at least one PDF.")

        st.stop()

    final_df = pd.DataFrame()

    for pdf in uploaded_files:

        df = extract_rows_from_pdf(pdf)

        df["Source File"] = pdf.name

        final_df = pd.concat([final_df, df], ignore_index=True)

    if final_df.empty:

        st.error("❌ No valid data found. Check if the PI matches the same format.")

        st.stop()

    st.success("✅ Extraction complete! Download your Stretchline Data file.")

    # Excel output

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        final_df.to_excel(writer, sheet_name="Stretchline Data", index=False)

    output.seek(0)

    st.download_button(

        label="⬇️ Download Stretchline_Data.xlsx",

        data=output,

        file_name="teejay_Data.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    st.dataframe(final_df)
 
