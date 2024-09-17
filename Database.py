from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure the database URI to point to your SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MedicSite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the Meddit model
class Meddit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Define the LungHealth model with additional columns
class LungHealth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    symptoms = db.Column(db.String(500))
    place = db.Column(db.String(100))  # Added column
    smoking = db.Column(db.String(50))  # Added column
    previous_disease = db.Column(db.String(500))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

def create_and_migrate_db():
    with app.app_context():
        # Create all tables (if they do not already exist)
        db.create_all()
        print("Database and tables created.")

def view_data():
    with app.app_context():
        # Query all data from the Meddit table
        meddit_posts = Meddit.query.all()
        print("Data from table 'Meddit':")
        if meddit_posts:
            for post in meddit_posts:
                print(f"ID: {post.id}, Author: {post.author}, Content: {post.content}")
        else:
            print("No data found in 'Meddit' table.")

        # Query all data from the LungHealth table
        lung_health_records = LungHealth.query.all()
        print("\nData from table 'LungHealth':")
        if lung_health_records:
            for record in lung_health_records:
                print(
                    f"ID: {record.id}, Name: {record.name}, Age: {record.age}, Gender: {record.gender}, Symptoms: {record.symptoms}, Place: {record.place}, Smoking: {record.smoking}, Previous Disease: {record.previous_disease}, Phone: {record.phone}, Email: {record.email}, Date: {record.date}")
        else:
            print("No data found in 'LungHealth' table.")

if __name__ == "__main__":
    create_and_migrate_db()
    view_data()
