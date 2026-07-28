import streamlit as st
import pdfplumber
import pandas as pd
import re

# Konfiguracja jasnego, profesjonalnego interfejsu
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
st.write("Wgraj manifest DFDS Stowage Plan (PDF), aby automatycznie zsumować wagi netto.")

uploaded_file = st.file_uploader("Przeciągnij plik PDF tutaj", type="pdf")

if uploaded_file is not None:
    st.info("Skanowanie dokumentu... To potrwa kilka sekund.")
    
    totals = {}
    total_cargo = 0.0
    
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Rozdzielamy tekst na linie
                    lines = text.split('\n')
                    for line in lines:
                        # Szukamy linii, które wyglądają jak wpis ładunku
                        # Typowy format: [Class] ... [Net Wt] [Gross Wt]
                        # Szukamy wzorca, w którym mamy klasę (np. 3, 2.1, 8, 9, 5.2, 4.1) oraz wagi.
                        match = re.search(r'\b(1\.4S|2\.1|2\.2|3|4\.1|4\.2|5\.1|5\.2|6\.1|8|9)\b.*\s+(\d+\.\d{2})\s+(\d+\.\d{2})\s+', line)
                        
                        if match:
                            dg_class = match.group(1)
                            net_wt = float(match.group(2))
                            
                            if dg_class in totals:
                                totals[dg_class] += net_wt
                            else:
                                totals[dg_class] = net_wt
                                
                            total_cargo += net_wt

        st.success("Analiza zakończona sukcesem!")
        
        st.subheader("Podsumowanie wag według klas:")
        if totals:
            for dg_class in sorted(totals.keys()):
                st.write(f"**Klasa {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
        else:
            st.warning("Nie znaleziono danych o ładunkach w standardowym formacie. Upewnij się, że to właściwy dokument.")

    except Exception as e:
        st.error(f"Wystąpił błąd podczas czytania pliku: {e}")
