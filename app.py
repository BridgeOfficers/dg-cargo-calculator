import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import re

st.set_page_config(page_title="DG Cargo Calculator | Vision", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #050510; }
    h1, h2, h3 { color: #0033A0; } /* Royal Blue */
    .stButton>button { background-color: #0033A0; color: white; border-radius: 4px; }
    .stAlert { background-color: #F0F8FF; color: #0033A0; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("DG Cargo Weight Calculator (OCR) 🌊")
st.write("Optical Character Recognition active. Upload scanned DFDS Stowage Plan.")

uploaded_file = st.file_uploader("Drag and drop scanned PDF here", type="pdf")

if uploaded_file is not None:
    st.info("Initializing OCR vision engine... This will take 10-20 seconds per page.")
    
    totals = {}
    total_cargo = 0.0
    raw_text = ""
    
    try:
        # Przekształcenie płaskiego PDF w mapę bitową (obrazy)
        images = convert_from_bytes(uploaded_file.read())
        
        for img in images:
            # Silnik optyczny Tesseract czyta tekst ze zdjęcia
            text = pytesseract.image_to_string(img)
            raw_text += text + "\n"
            
            lines = text.split('\n')
            for line in lines:
                # Szukamy klasy DG na odczytanym obrazie
                match = re.search(r'\b(1\.4S|1\.4G|2\.1|2\.2|2\.3|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b', line)
                
                if match:
                    dg_class = match.group(1)
                    # Wyciągamy liczby, akceptując kropki i przecinki (błędy OCR)
                    nums = re.findall(r'\d+[\.,]\d{1,3}', line)
                    
                    if len(nums) >= 2:
                        net_wt = float(nums[-2].replace(',', '.'))
                    elif len(nums) == 1:
                        net_wt = float(nums[0].replace(',', '.'))
                    else:
                        continue
                        
                    if dg_class in totals:
                        totals[dg_class] += net_wt
                    else:
                        totals[dg_class] = net_wt
                        
                    total_cargo += net_wt

        if totals:
            st.success("Vision Analysis completed successfully!")
            st.subheader("Weight summary by class:")
            for dg_class in sorted(totals.keys()):
                st.write(f"**Class {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
            
            with st.expander("CHECK RAW OCR TEXT"):
                st.text_area("Machine Vision Output:", raw_text, height=300)
        else:
            st.warning("OCR could not format the cargo data. Check the raw vision text below.")
            st.text_area("RAW OCR TEXT (Copy this for diagnostics):", raw_text, height=400)

    except Exception as e:
        st.error(f"Critical System Error: {e}")
