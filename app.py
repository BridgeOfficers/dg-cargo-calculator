import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="DG Cargo Calculator", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #050510; }
    h1, h2, h3 { color: #0033A0; } /* Royal Blue */
    .stButton>button { background-color: #0033A0; color: white; border-radius: 4px; }
    .stAlert { background-color: #F0F8FF; color: #0033A0; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("DG Cargo Weight Calculator 🌊")
st.write("Upload the DFDS Stowage Plan (PDF) to automatically calculate net weights.")

uploaded_file = st.file_uploader("Drag and drop PDF file here", type="pdf")

if uploaded_file is not None:
    st.info("Scanning document... Diagnostic Mode active.")
    
    totals = {}
    total_cargo = 0.0
    raw_text = ""
    
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # Wczytywanie z dużą tolerancją na przesunięcia
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text:
                    raw_text += text + "\n---PAGE BREAK---\n"
                    lines = text.split('\n')
                    for line in lines:
                        # Szukamy klasy
                        match = re.search(r'\b(1\.4S|1\.4G|2\.1|2\.2|2\.3|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b', line)
                        
                        if match:
                            dg_class = match.group(1)
                            # Wyciągamy wszystkie liczby zmiennoprzecinkowe z tej samej linii
                            nums = re.findall(r'\d+\.\d{1,3}', line)
                            
                            if len(nums) >= 2:
                                net_wt = float(nums[-2]) # Przedostatnia liczba to zazwyczaj Net Wt
                            elif len(nums) == 1:
                                net_wt = float(nums[0])
                            else:
                                continue
                                
                            if dg_class in totals:
                                totals[dg_class] += net_wt
                            else:
                                totals[dg_class] = net_wt
                                
                            total_cargo += net_wt

        if totals:
            st.success("Analysis completed successfully!")
            st.subheader("Weight summary by class:")
            for dg_class in sorted(totals.keys()):
                st.write(f"**Class {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
        else:
            st.warning("No cargo data found. Check the raw text below to see what the machine reads.")
            st.text_area("RAW PDF TEXT (Skopiuj ten tekst):", raw_text, height=300)

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
