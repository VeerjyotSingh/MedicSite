import sounddevice as sd
import Model
from Model import skin_classes
import soundfile as sf
from PIL import Image
from werkzeug.utils import secure_filename
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash ,g
from newsapi import NewsApiClient
from datetime import datetime
import threading
import librosa
import numpy as np
from io import BytesIO
import tensorflow as tf
import os
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MedicSite.db'
db = SQLAlchemy(app)
class Meddit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

class LungHealth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    symptoms = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    place = db.Column(db.String(100))  # New field
    smoking = db.Column(db.String(50))  # New field
    previous_disease = db.Column(db.String(500))  # New field
    phone = db.Column(db.String(20))  # New field
    email = db.Column(db.String(100))  # New field

with app.app_context():
    db.create_all()

key =os.urandom(24)
trained_model = tf.keras.models.load_model("create_audio_classification_model.h5")

api_key = os.getenv('NewsAPI')
print(os.environ)
print(f"API Key: {api_key}")
@app.route("/")
def about():
    print(f"API Key in Flask: {os.getenv('NewsAPI')}")
    return render_template('index.html')

@app.route("/news")
def news():
    api_key = os.getenv("NewsAPI")
    if not api_key:
        raise ValueError("API_KEY environment variable not set or empty.")

    try:
        # Initialize NewsApiClient with API key
        newsapi = NewsApiClient(api_key=api_key)

        # Fetch top headlines
        top_headlines = newsapi.get_top_headlines(
            category='health',
            language='en',
            country='in'
        )

        # Extract articles from the response
        articles = top_headlines.get('articles', [])
        length = len(articles)

        # Debugging: print articles to the console
        print("Fetched articles:", articles)

        # Render the template with articles and their length
        return render_template('news.html', articles=articles, length=length)

    except Exception as e:
        # Debugging: print the error to the console
        print(f"An error occurred: {e}")
        # Render the template with an empty list in case of error
        return render_template('news.html', articles=[], length=0)
@app.route("/meddit", methods=['GET', 'POST'])
def meddit():
    if request.method == 'POST':
        author = request.form['author']
        content = request.form['content']
        new_post = Meddit(author=author, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('meddit'))

    posts = Meddit.query.all()
    return render_template('meddit.html', posts=posts)


@app.route("/locator")
def locator():
    return render_template('locator.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/skincancer', methods=['GET', 'POST'])
def skincancer():
    if request.method == 'POST':
        # Check if the file part is present in the request
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']

        # If no file is selected
        if file.filename == '':
            return 'No selected file'

        # If file is allowed, save it
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                result = predict_skin_cancer(filepath)
            except Exception as e:
                print(f"Error during recording or prediction: {str(e)}")
                return render_template('SkinCancer/error.html', message="An error occurred during audio processing.")
            return render_template("SkinCancer/result.html",prediction=result)

    return render_template('SkinCancer/skincancer.html')
# Function to predict an image
def predict_skin_cancer(image_path):

    inputimg = Image.open(image_path).resize((28, 28))
    img = np.array(inputimg).reshape(-1, 28, 28, 3)
    result = Model.model.predict(img).tolist()
    max_prob = max(result[0])
    class_ind = result[0].index(max_prob)
    if (class_ind == 0):
        info = "Actinic keratosis also known as solar keratosis or senile keratosis are names given to intraepithelial keratinocyte dysplasia. As such they are a pre-malignant lesion or in situ squamous cell carcinomas and thus a malignant lesion."
    elif (class_ind == 1):
        info = "Basal cell carcinoma is a type of skin cancer. Basal cell carcinoma begins in the basal cells — a type of cell within the skin that produces new skin cells as old ones die off.Basal cell carcinoma often appears as a slightly transparent bump on the skin, though it can take other forms. Basal cell carcinoma occurs most often on areas of the skin that are exposed to the sun, such as your head and neck"
    elif (class_ind == 2):
        info = "Benign lichenoid keratosis (BLK) usually presents as a solitary lesion that occurs predominantly on the trunk and upper extremities in middle-aged women. The pathogenesis of BLK is unclear; however, it has been suggested that BLK may be associated with the inflammatory stage of regressing solar lentigo (SL)1"
    elif (class_ind == 3):
        info = "Dermatofibromas are small, noncancerous (benign) skin growths that can develop anywhere on the body but most often appear on the lower legs, upper arms or upper back. These nodules are common in adults but are rare in children. They can be pink, gray, red or brown in color and may change color over the years. They are firm and often feel like a stone under the skin. "
    elif (class_ind == 4):
        info = "A melanocytic nevus (also known as nevocytic nevus, nevus-cell nevus and commonly as a mole) is a type of melanocytic tumor that contains nevus cells. Some sources equate the term mole with ‘melanocytic nevus’, but there are also sources that equate the term mole with any nevus form."
    elif (class_ind == 5):
        info = "Pyogenic granulomas are skin growths that are small, round, and usually bloody red in color. They tend to bleed because they contain a large number of blood vessels. They’re also known as lobular capillary hemangioma or granuloma telangiectaticum."
    elif (class_ind == 6):
        info = "Melanoma, the most serious type of skin cancer, develops in the cells (melanocytes) that produce melanin — the pigment that gives your skin its color. Melanoma can also form in your eyes and, rarely, inside your body, such as in your nose or throat. The exact cause of all melanomas isn't clear, but exposure to ultraviolet (UV) radiation from sunlight or tanning lamps and beds increases your risk of developing melanoma."

    return info
@app.route("/contact")
def contact():
    return render_template("contact/contact.html")

@app.route("/test")
def test():
    return render_template("onlinetest/onlinetest.html")

# Handling lung cancer recording

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


@app.route("/lunghealth", methods=["GET", "POST"])
def lunghealth():
    return render_template('lunghealth/lunghealth.html')


# Capture user info and redirect to recording page
@app.route("/record", methods=['POST'])
def record():
    if request.method == "POST":
        try:
            # Retrieve form data using .get() to avoid KeyError
            name = request.form.get('name')
            age = request.form.get('age')
            place = request.form.get('place')
            gender = request.form.get('gender')
            symptoms = request.form.get('symptoms')
            smoking = request.form.get('smoking')
            previous_disease = request.form.get('previous_disease')
            phone = request.form.get('phone')
            email = request.form.get('email')

            # Optional: Log the received data for debugging
            print(f"Form data received: name={name}, age={age}, place={place}, gender={gender}, symptoms={symptoms}, smoking={smoking}, previous_disease={previous_disease}, phone={phone}, email={email}")

            # Create a new LungHealth record
            new_record = LungHealth(
                name=name,
                age=age,
                gender=gender,
                symptoms=symptoms,
                place=place,
                smoking=smoking,
                previous_disease=previous_disease,
                phone=phone,
                email=email
            )

            # Add the new record to the database
            db.session.add(new_record)
            db.session.commit()

            # Redirect to the record page
            return redirect(url_for('record_page'))

        except Exception as e:
            print(f"An error occurred: {e}")
            db.session.rollback()
            return render_template('lunghealth/error.html', message="An error occurred during form submission.")



# Render the recording page
@app.route('/record_page')
def record_page():
    return render_template('lunghealth/record3.html', recording_durations=RECORDING_DURATIONS)


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
        return render_template('lunghealth/result.html', prediction=prediction)

    except Exception as e:
        print(f"Error during recording or prediction: {str(e)}")
        return render_template('lunghealth/error.html', message="An error occurred during audio processing.")


@app.route("/disease_info_page")
def disease_info_page():
    return render_template("lunghealth/lunghealth_info.html")

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
    return render_template("templates/SkinCancer/skn_info.html")

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
            "error":"Error Occured"
        }



if __name__ == "__main__":
    gradio_thread = threading.Thread(target=start_gradio)
    gradio_thread.start()
    app.run(debug=True, use_reloader=False)