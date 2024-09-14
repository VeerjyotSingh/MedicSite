import sounddevice as sd
import soundfile as sf
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from newsapi import NewsApiClient
import requests
import threading
import librosa
import numpy as np
from io import BytesIO
from tensorflow import keras

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect("contact.db", check_same_thread=False)
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Meddit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        content TEXT NOT NULL
    )
''')
conn.commit()

trained_model = keras.models.load_model("create_audio_classification_model.h5")
@app.route("/")
def about():
    return render_template('index.html')

@app.route("/news")
def news():
    try:
        newsapi = NewsApiClient(api_key="a7c40948db6d454aa8ee3f7d5754234b")
        top_headlines = newsapi.get_top_headlines(
            category='health',
            language='en',
            country='in')

        # Extract articles
        articles = top_headlines.get('articles', [])
        length = len(articles)
        # Render the template with articles
        return render_template('news.html', articles=articles, len=length)

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('news.html')

@app.route("/meddit", methods=['GET', 'POST'])
def meddit():
    if request.method == 'POST':
        author = request.form['author']
        content = request.form['content']
        # Insert data into database
        cursor.execute('INSERT INTO Meddit (author, content) VALUES (?, ?)', (author, content))
        conn.commit()
        return redirect(url_for('meddit'))

    # Retrieve data from database
    cursor.execute('SELECT * FROM Meddit')
    posts = cursor.fetchall()

    return render_template('meddit.html', posts=posts)

@app.route("/locator")
def locator():
    return render_template('locator.html')

@app.route("/skincancer")
def skincancer():
    return render_template('skincancer.html')

@app.route("/contact")
def contact():
    return render_template("contact/contact.html")

@app.route("/test")
def test():
    return render_template("onlinetest/onlinetest.html")

# Handling lung cancer recording
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['USER_INFO_FILE'] = 'user_info.txt'

# Mapping each step to its corresponding recording duration
RECORDING_DURATIONS = {
    'Breathing Deep': 11,
    'Breathing Shallow': 8,
    'Cough Heavy': 5,
    'Cough Shallow': 5,
    'Vowel A': 8,
    'Vowel E': 8,
    'Vowel O': 8,
    'Counting Fast': 5,
    'Normal': 10
}

@app.route("/lungcancer")
def lungcancer():
    return render_template('lungcancer/lungcancer.html')


# Capture user info and redirect to recording page
@app.route('/record', methods=['POST'])
def record():
    user_info = {
        'name': request.form['name'],
        'age': request.form['age'],
        'place': request.form['place'],
        'smoking': request.form['smoking'],
        'previous_disease': request.form['previous_disease'],
        'phone': request.form['phone'],
        'email': request.form['email']
    }

    # You can process user_info here or just pass it to the result page
    return redirect(url_for('record_page'))


# Render the recording page
@app.route('/record_page')
def record_page():
    return render_template('lungcancer/record3.html', recording_durations=RECORDING_DURATIONS)


# Record audio and process it without saving to disk
@app.route('/record_audio', methods=['POST'])
def record_audio():
    audio_step = request.form['audio_step']

    # Get the corresponding recording duration for the selected step
    duration = RECORDING_DURATIONS.get(audio_step, 5)  # Default to 5 seconds if not found
    samplerate = 48000

    try:
        # Record audio in memory
        recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        # Save to in-memory buffer (BytesIO)
        audio_buffer = BytesIO()
        sf.write(audio_buffer, recording, samplerate, format='WAV')
        audio_buffer.seek(0)
        prediction = predict_respiratory_disease(trained_model, audio_buffer)
        return render_template('lungcancer/result.html', prediction=prediction)

    except Exception as e:
        print(f"Error during recording or prediction: {str(e)}")
        return render_template('lungcancer/error.html', message="An error occurred during audio processing.")


@app.route("/reaction")
def reaction():
    return render_template("onlinetest/reaction.html")

@app.route("/num_seq")
def num_seq():
    return render_template("onlinetest/numsequence.html")

@app.route("/verbal")
def verbal():
    return render_template("onlinetest/verbal.html")

@app.route("/skn_info")
def skn_info():
    return render_template("skn_info.html")

@app.route("/disease_info_page")
def disease_info_page():
    return render_template("lungcancer/lungcancer_info.html")


def start_gradio():
    os.system('python chatbot.py')

@app.route('/chat')
def chat():
    gradio_url = "http://127.0.0.1:7860"
    return render_template('chat.html', gradio_url=gradio_url)


def extract_audio_features(audio_signal, sr):
    try:
        # Extract audio features using librosa (e.g., chroma_stft, rmse, spectral_centroid)
        chroma_stft = librosa.feature.chroma_stft(y=audio_signal, sr=sr)
        rmse = librosa.feature.rms(y=audio_signal)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_signal, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_signal, sr=sr)

        # Combine features into a single feature array
        features = np.hstack([chroma_stft.mean(axis=1), rmse.mean(), spectral_centroid.mean(), spectral_bandwidth.mean()])
        return features

    except Exception as e:
        print(f"Error extracting features from audio signal: {str(e)}")


def predict_respiratory_disease(trained_model, file):
    try:
        # Load audio from the in-memory file
        data, samplerate = sf.read(file)

        # Extract features from the audio signal
        audio_features = extract_audio_features(data, samplerate)

        if audio_features is not None:
            # Reshape the features to match the model's expected input shape
            audio_features_reshaped = audio_features.reshape(1, -1)

            # Use the trained model to make a prediction
            prediction = trained_model.predict(audio_features_reshaped)

            # Return the prediction for rendering on the result page
            return {
                'no_disease_prob': prediction[0][0] * 100,
                'disease_prob': prediction[0][1] * 100
            }

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return {
            error:"Error Occured"
        }



if __name__ == "__main__":
    # Start Gradio server in a separate thread
    gradio_thread = threading.Thread(target=start_gradio)
    gradio_thread.start()

    # Start Flask server
    app.run(debug=True, use_reloader=False)