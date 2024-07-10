import sounddevice
import soundfile
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from newsapi import NewsApiClient

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

@app.route("/")
def about():
    return render_template('index.html')

@app.route("/news")
def news():
    # Create a NewsApiClient object
    newsapi = NewsApiClient(api_key='your_news_api_key')

    # Get top headlines
    top_headlines = newsapi.get_top_headlines(
                                          category='health',
                                          language='en',
                                          country='in')

    # Extract articles
    articles = top_headlines['articles']

    length = len(articles)
    return render_template('news.html', articles=articles, len=length)

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

@app.route("/breastcancer")
def breastcancer():
    return render_template('breastcancer.html')

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/test")
def test():
    return render_template("test.html")

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
    return render_template('lungcancer.html')

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
    samplerate = 48000
    recording = sounddevice.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sounddevice.wait()

    # Save the recorded audio data to a file
    soundfile.write(file_path, recording, samplerate)

    return 'OK'

@app.route("/reaction")
def reaction():
    return render_template("reaction.html")

@app.route("/num_seq")
def num_seq():
    return render_template("numsequence.html")

@app.route("/verbal")
def verbal():
    return render_template("verbal.html")

@app.route("/skn_info")
def skn_info():
    return render_template("skn_info.html")

@app.route("/breast_cancer_info")
def breastcancerinfo():
    return render_template("breastcancerinfo.html")

if __name__ == "__main__":
    app.run(debug=True)
