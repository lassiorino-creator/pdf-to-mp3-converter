import asyncio
import os
import re
from flask import Flask, render_template, request, send_file, flash, redirect
from pypdf import PdfReader
import edge_tts

app = Flask(__name__)
app.secret_key = "supersecretkey"

# L'ambiente Serverless di Vercel permette la scrittura solo dentro /tmp
UPLOAD_FOLDER = "/tmp"

async def generate_audio_async(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.([^\s])', r'. \1', text)
    return text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Nessun file selezionato")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("Nessun file selezionato")
            return redirect(request.url)
        
        if file and file.filename.lower().endswith(".pdf"):
            try:
                reader = PdfReader(file)
                testo_completo = ""
                for page in reader.pages:
                    text_page = page.extract_text()
                    if text_page:
                        testo_completo += text_page + " "
                
                testo_pulito = clean_text(testo_completo)
                
                if not testo_pulito:
                    flash("Impossibile estrarre testo dal PDF. Controlla che non sia un'immagine.")
                    return redirect(request.url)
                
                voice = request.form.get("voice", "it-IT-ElsaNeural")
                output_filename = "audiolibro.mp3"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_audio_async(testo_pulito, voice, output_path))
                loop.close()
                
                if os.path.exists(output_path):
                    return send_file(output_path, as_attachment=True, download_name="il_tuo_audiolibro.mp3", mimetype="audio/mp3")
                else:
                    flash("Errore nella generazione del file audio.")
            except Exception as e:
                flash(f"Si è verificato un errore: {str(e)}")
                return redirect(request.url)
                
    return render_template("index.html")
