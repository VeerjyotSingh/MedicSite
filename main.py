from flask import Flask, render_template, request
import pygame
app = Flask(__name__)

@app.route("/")
def about():
    return render_template('index.html')

@app.route("/news")
def news():
    return render_template('news.html')

@app.route("/meddit")
def meddit():
    return render_template('meddit.html')

@app.route("/locator")
def locator():
    return render_template('locator.html')

@app.route("/skincancer")
def skincancer():
    return render_template('skincancer.html')

@app.route("/lungcancer")
def lungcancer():
    return render_template('lungcancer.html')

@app.route("/breastcancer")
def breastcancer():
    return render_template('breastcancer.html')

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio_file' not in request.files:
        return "No audio file uploaded", 400
    else:
        audio_file = request.files['audio_file']
        return "Audio uploaded successfully!", 200

if __name__ == "__main__":
    app.run(debug=True)