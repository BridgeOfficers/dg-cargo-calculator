import streamlit as st
from pypdf import PdfReader
import re

# Konfiguracja jasnego, profesjonalnego interfejsu (Luminous / Bright & Expensive)
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
st.write("Wersja Premium. Żadnego logowania. Wgraj manifest DFDS (PDF), a system automatycznie zsumuje wagi netto.")

uploaded_file = st.file_uploader("Przeciągnij plik PDF tutaj", type="pdf")

if uploaded_file is not None:
    totals = {}
    total_cargo = 0.0
    
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    # 1. Szukamy, czy w linii jest podana klasa DG
                    class_match = re.search(r'\b(1\.4S|1\.4G|2\.1|2\.2|2\.3|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b', line)
                    
                    # 2. Szukamy wyłącznie liczb w formacie wagi (zawsze dwa miejsca po przecinku)
                    weights = re.findall(r'\b\d+\.\d{2}\b', line)
                    
                    # 3. Jeśli mamy klasę i przynajmniej dwie wagi (Net Wt. oraz Gross Wt.)
                    if class_match and len(weights) >= 2:
                        dg_class = class_match.group(1)
                        # W manifestach DFDS pierwsza waga z dwoma miejscami po przecinku to zawsze Net Wt.
                        net_wt = float(weights[0]) 
                        
                        if dg_class in totals:
                            totals[dg_class] += net_wt
                        else:
                            totals[dg_class] = net_wt
                            
                        total_cargo += net_wt

        if totals:
            st.success("Analiza zakończona sukcesem!")
            st.subheader("Podsumowanie wag według klas:")
            for dg_class in sorted(totals.keys()):
                st.write(f"**Klasa {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
        else:
            st.warning("Nie znalazłem żadnych wag w tym pliku. Skrypt działa, ale PDF nie posiada warstwy tekstowej z wagami w standardowym formacie.")
            
    except Exception as e:
        st.error(f"Błąd systemu: {e}")
