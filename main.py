from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run(debug=True)