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

@app.route("/breastcancer")
def breastcancer():
    return render_template('breastcancer.html')

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/test")
def test():
    return render_template("onlinetest.html")

#handling lung cancer
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
    return "<h1>recording</h1>"

@app.route("/disease_info_page")
def disease_info_page():
    return"hell yeah"

if __name__ == "__main__":
    app.run(debug=True)