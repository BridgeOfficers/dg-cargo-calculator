import streamlit as st
import fitz  # PyMuPDF
import re

# Konfiguracja środowiska Premium (Luminous, Bright & Expensive)
st.set_page_config(page_title="DG Cargo Calculator | Ultimate", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #050510; }
    h1, h2, h3 { color: #0033A0; } /* Royal Blue */
    .stButton>button { background-color: #0033A0; color: white; border-radius: 4px; }
    .stAlert { background-color: #F0F8FF; color: #0033A0; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("DG Cargo Weight Calculator 🌊")
st.write("Silnik PyMuPDF. Precyzyjna ekstrakcja danych operacyjnych z manifestów DFDS.")

uploaded_file = st.file_uploader("Przeciągnij plik PDF tutaj", type="pdf")

if uploaded_file is not None:
    totals = {}
    total_cargo = 0.0
    raw_text_dump = ""
    
    try:
        # Wczytywanie pliku przez potężny silnik PyMuPDF bezpośrednio z pamięci
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        for page in doc:
            # Wymuszenie sortowania fizycznego (łączy rozstrzelone tabele w logiczne rzędy)
            text = page.get_text("text", sort=True)
            if text:
                raw_text_dump += text + "\n---PAGE BREAK---\n"
                lines = text.split('\n')
                
                for line in lines:
                    # 1. Brutalne przeszukanie wiersza w poszukiwaniu klasy DG
                    class_match = re.search(r'\b(1\.4S|1\.4G|2\.1|2\.2|2\.3|3|4\.1|4\.2|4\.3|5\.1|5\.2|6\.1|6\.2|7|8|9)\b', line)
                    
                    # 2. Wyciągnięcie z tego samego wiersza liczb zmiennoprzecinkowych (format wag DFDS)
                    weights = re.findall(r'\b\d+\.\d{2}\b', line)
                    
                    # 3. Akceptacja wiersza tylko wtedy, gdy system widzi klasę i przynajmniej dwie wagi 
                    if class_match and len(weights) >= 2:
                        dg_class = class_match.group(1)
                        # System DFDS wyrzuca Net Wt jako pierwszą z wartości wagowych
                        net_wt = float(weights[0]) 
                        
                        if dg_class in totals:
                            totals[dg_class] += net_wt
                        else:
                            totals[dg_class] = net_wt
                            
                        total_cargo += net_wt

        if totals:
            st.success("Analiza zakończona z pełną precyzją.")
            st.subheader("Podsumowanie wag według klas:")
            for dg_class in sorted(totals.keys()):
                st.write(f"**Klasa {dg_class}**: {totals[dg_class]:.2f} kg")
            
            st.markdown("---")
            st.subheader(f"**Total weight of total dg cargo:** {total_cargo:.2f} kg")
        else:
            st.warning("Silnik PyMuPDF odczytał plik, ale tabele nie złożyły się w standardowe wiersze. Rozwiń panel diagnostyczny poniżej.")
            
        with st.expander("DIAGNOSTYKA SYSTEMU (RAW TEXT)"):
            st.text_area("Czysty zrzut pamięci z rdzenia PyMuPDF:", raw_text_dump, height=300)

    except Exception as e:
        st.error(f"Krytyczny błąd systemu: {e}")
