import streamlit as st

import pdfplumber

import pandas as pd

import re

import io

st.set_page_config(page_title="Teejay Data Extractor", page_icon="📄")

st.title("📄 Teejay Data Extractor")


# --------------------------------------------------------

# FUNCTION TO EXTRACT ALL ROWS WITH DATE FIX

# --------------------------------------------------------

def extract_rows(pdf_file):

    with pdfplumber.open(pdf_file) as pdf:

        lines = []

        for p in pdf.pages:

            text = p.extract_text()

            if text:

                for line in text.split("\n"):

                    lines.append(line)

    rows = []

    current = None

    # Patterns

    qty_po_mat_pattern = re.compile(

        r"(?P<qty>\d+\.\d+)\s+(?P<po>\d{10})\s+(?P<cm>\d{10})"

    )

    date_pattern = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

    for line in lines:

        # ==== 1️⃣ Detect start of a new row (QTY + PO + CUSTMAT) ====

        m = qty_po_mat_pattern.search(line)

        if m:

            # Store previous row if present

            if current:

                rows.append(current)

            # Start a new row

            current = {

                "Quantity in": m.group("qty"),

                "PO Number": m.group("po"),

                "Customer Material": m.group("cm"),

                "DEL date ex mill": ""

            }

            continue

        # ==== 2️⃣ Detect delivery date in later lines ====

        if current:

            d = date_pattern.search(line)

            if d:

                current["DEL date ex mill"] = d.group()

                rows.append(current)

                current = None     # reset – row finished

                continue

    # ==== 3️⃣ Append final row if incomplete ====

    if current:

        rows.append(current)

    return pd.DataFrame(rows)


# --------------------------------------------------------

# STREAMLIT UI

# --------------------------------------------------------

uploaded = st.file_uploader("Upload PI PDFs", accept_multiple_files=True, type="pdf")

if st.button("Extract Teejay Data"):

    if not uploaded:

        st.warning("Please upload at least one PDF.")

        st.stop()

    final = pd.DataFrame()

    for pdf in uploaded:

        df = extract_rows(pdf)

        df["Source File"] = pdf.name

        final = pd.concat([final, df], ignore_index=True)

    if final.empty:

        st.error("No rows detected. Check PDF format.")

        st.stop()

    st.success("Extraction complete! Download your file.")

    # Excel output

    out = io.BytesIO()

    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:

        final.to_excel(writer, sheet_name="Teejay Data", index=False)

    out.seek(0)

    st.download_button(

        "⬇️ Download Teejay_Data.xlsx",

        data=out,

        file_name="Teejay_Data.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    st.dataframe(final)
 
