from flask import Flask, request, render_template, send_file
import os
import whisper
from gtts import gTTS
from googletrans import Translator
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

model = whisper.load_model("base")
translator = Translator()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["video"]
        target_lang = request.form["language"]
        filename = str(uuid.uuid4())
        video_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp4")
        audio_path = os.path.join(UPLOAD_FOLDER, f"{filename}.mp3")
        tts_path = os.path.join(UPLOAD_FOLDER, f"{filename}_tts.mp3")
        output_path = os.path.join(OUTPUT_FOLDER, f"{filename}_dubbed.mp4")

        file.save(video_path)

        subprocess.call(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"])
        result = model.transcribe(audio_path)
        original_text = result["text"]

        translated = translator.translate(original_text, dest=target_lang).text
        tts = gTTS(translated, lang=target_lang)
        tts.save(tts_path)

        subprocess.call(["ffmpeg", "-i", video_path, "-i", tts_path, "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", output_path, "-y"])
        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
