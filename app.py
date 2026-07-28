import streamlit as st
import pdfplumber
import pandas as pd
import re

# Clean, professional interface configuration
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
    st.info("Scanning document... This will take a few seconds.")
    
    totals = {}
    total_cargo = 0.0
    
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # x_tolerance and y_tolerance handle skewed or slightly misaligned text in tables
                text = page.extract_text(x_tolerance=2, y_tolerance=3)
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        # Searching for DG class and weights
                        match = re.search(r'\b(1\.4S|2\.1|2\.2|3|4\.1|4\.2|5\.1|5\.2|6\.1|8|9)\b.*\s+(\d+\.\d{2})\s+(\d+\.\d{2})\s+', line)
                        
                        if match:
                            dg_class = match.group(1)
                            net_wt = float(match.group(2))
                            
                            if dg_class in totals:
                                totals[dg_class] += net_wt
                            else:
                                totals[dg_class] = net_wt
                                
                            total_cargo += net_wt

        st.success("Analysis completed successfully!")
        
        st.subheader("Weight summary by class:")
        if totals:
            for dg_class in sorted(totals.keys()):
                st.write(f"**Class {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
        else:
            st.warning("No cargo data found in the standard format. Please ensure this is the correct document or that the scan quality is clear.")

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
