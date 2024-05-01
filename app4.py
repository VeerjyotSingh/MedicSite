# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import soundfile
import sounddevice
import openai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['USER_INFO_FILE'] = 'user_info.txt'
app.config['OPENAI_API_KEY'] = 'k-qt9CxfHkoKGL033aDHtkT3BlbkFJjkCA18EkG8Cg60VrIRO'  # Replace with your actual OpenAI API key
app.secret_key = 'supersecretkey'

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
    'Normal': 10,
    # Add more steps as needed
}

openai.api_key = app.config['OPENAI_API_KEY']

@app.route('/')
def index():
    return render_template('index3.html')

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

    # Save user info to a text file
    with open(app.config['USER_INFO_FILE'], 'w') as file:
        for key, value in user_info.items():
            file.write(f'{key}: {value}\n')

    return redirect(url_for('record_page'))

@app.route('/record_page')
def record_page():
    return render_template('record3.html', recording_durations=RECORDING_DURATIONS)

@app.route('/record_audio', methods=['POST'])
def record_audio():
    audio_step = request.form['audio_step']

    # Create the uploads folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Set the file path for the recorded audio
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{audio_step.replace(" ", "_")}.wav')

    # Record audio using sounddevice
    duration = RECORDING_DURATIONS.get(audio_step, 5)  # Default to 5 seconds if step not found
    samplerate = 44100
    recording = sounddevice.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sounddevice.wait()

    # Save the recorded audio data to a file
    soundfile.write(file_path, recording, samplerate)

    flash('Recording saved successfully!', 'success')

    return 'OK'

@app.route('/disease_info')
def disease_info_page():
    return render_template('openai_chatbot.html')

@app.route('/openai_chat', methods=['POST'])
def openai_chat():
    user_message = request.form['user_message']
    chat_response = get_openai_response(user_message)
    return jsonify({'response': chat_response})

def get_openai_response(user_message):
    # Use OpenAI API to get a response
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
