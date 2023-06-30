from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cv2
import pytesseract
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///handwriting.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the request contains an uploaded file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Save the uploaded file
                image_path = 'uploaded_image.png'
                file.save(image_path)
                # Process the image and extract text
                text = image_to_text(image_path)
                # Render the result page with the extracted text
                return render_template('result.html', text=text)
        elif 'text' in request.form:
            text = request.form['text']
            # Render the result page with the entered text
            return redirect(url_for('result', text=request.form['text']))
    # Render the main page with the upload form and drawing space
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user.password == password:
            # login successful, redirect to main page
            return redirect(url_for('main'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nickname = request.form['nickname']
        user = User.query.filter_by(username=username).first()
        if user:
            error = 'Username already exists'
            return render_template('signup.html', error=error)
        else:
            # Create a new User
            new_user = User(username=username, password=password, nickname=nickname)
            try:
                # Add new_user to the db
                db.session.add(new_user)
                db.session.commit()
                # Redirect to login page after successful sign up
                return redirect(url_for('login'))
            except SQLAlchemyError as e:
                # Handle db errors
                error = 'An error occurred while signing up'
                return render_template('signup.html', error=error)
    return render_template('signup.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/result')
def result():
    text = request.args.get('text', '')
    return render_template('result.html', text=text)

def get_user(username):
    user = User.query.filter_by(username=username).first()
    return user

def image_to_text(image_path):
    # Load the image using OpenCV
    img = cv2.imread(image_path)
    # check if the given img exists and can be loaded properly
    if img is None:
        return "Failed to load the image. Please check the file path."

    # Preprocess the image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding technique
    block_size = 7  # size of the neighborhood for threshold calculation
    C = 19  # constant subtracted from the mean
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, C)

    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(img)

    # Return the extracted text
    return text

if __name__ == '__main__':
    app.run(debug=True)