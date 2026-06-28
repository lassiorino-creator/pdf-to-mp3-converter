import asyncio
import streamlit as st
import edge_tts
from pypdf import PdfReader
import os

st.set_page_config(page_title="PDF to MP3 Converter", layout="centered")
st.title("Convertitore PDF in Audio (Voci Microsoft Edge)")
st.write("Carica il tuo file PDF per scaricare l'intero audiolibro in MP3.")

opzioni_voci = {
    "Elsa (Voce Femminile Naturale)": "it-IT-ElsaNeural",
    "Diego (Voce Maschile Naturale)": "it-IT-DiegoNeural",
    "Isabella (Alternativa Femminile)": "it-IT-IsabellaNeural"
}
scelta_utente = st.selectbox("Scegli la voce che preferisci:", list(opzioni_voci.keys()))
voce_selezionata = opzioni_voci[scelta_utente]

uploaded_file = st.file_uploader("Trascina o seleziona il file PDF qui", type=["pdf"])

if uploaded_file is not None:
    st.info("Estrazione del testo dal PDF in corso...")
    
    try:
        reader = PdfReader(uploaded_file)
        testo_completo = ""
        
        for pagina in reader.pages:
            testo_pagina = pagina.extract_text()
            if testo_pagina:
                testo_completo += testo_pagina + " "
        
        if len(testo_completo.strip()) == 0:
            st.error("Non è stato possibile estrarre testo dal PDF. Assicurati che non sia una semplice scansione di immagini.")
        else:
            st.success(f"Testo estratto con successo! Totale caratteri: {len(testo_completo)}")
            
            if st.button("Avvia Conversione in MP3"):
                nome_file_audio = "audiolibro_generato.mp3"
                
                with st.spinner("Generazione del file MP3..."):
                    # Questo risolve il bug del freeze con Python 3.13
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    communicate = edge_tts.Communicate(testo_completo, voce_selezionata)
                    loop.run_until_complete(communicate.save(nome_file_audio))
                    loop.close()
                
                if os.path.exists(nome_file_audio):
                    st.success("Audio generato con successo!")
                    with open(nome_file_audio, "rb") as file:
                        st.download_button(
                            label="📥 SCARICA IL FILE MP3",
                            data=file,
                            file_name="il_tuo_audiolibro.mp3",
                            mime="audio/mp3"
                        )
    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")