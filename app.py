from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import cv2
import pytesseract
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///handwriting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key for session management
db = SQLAlchemy(app)

# Define Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('categories', lazy=True))

    def __repr__(self):
        return f"<Category {self.name}>"
    
# Define Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('notes', lazy=True))

    def __repr__(self):
        return f"<Note {self.title}>"

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
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
        elif 'add_text' in request.form:
            return redirect(url_for('add_text'))
        elif 'upload_file' in request.form:
            return redirect(url_for('upload_file'))
        # elif 'text' in request.form:
        #     text = request.form['text']
        #     # Render the result page with the entered text
        #     return redirect(url_for('result', text=text))
        elif 'show all' in request.form:
            return redirect(url_for('all_texts'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    # Render the main page with the upload form and drawing space
    return render_template('main.html', user=user, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user.password == password:
            session['user_id'] = user.id
            # login successful, redirect to main page
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
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
                session['user_id'] = new_user.id
                # Redirect to login page after successful sign up
                return redirect(url_for('index'))
            except SQLAlchemyError as e:
                # Handle db errors
                error = 'An error occurred while signing up'
                return render_template('signup.html', error=error)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    categories = Category.query.filter_by(user_id=session['user_id']).all()

    # Add a new category option if no category has been added yet.
    if len(categories) == 0:
        category = Category(name='Show all')
        db.session.add(category)
        db.session.commit()

    return render_template('main.html', user=user, categories=categories)

@app.route('/category/<int:category_id>')
def category_notes(category_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    category = Category.query.get(category_id)
    if category and category.user_id == session['user_id']:
        notes = category.notes
        return render_template('notes.html', user=user, category=category, notes=notes)
    else:
        error = 'Category not found'
        return render_template('main.html', error=error)

@app.route('/note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    note = Note.query.get(note_id)
    if note and note.category.user_id == session['user_id']:
        return render_template('note.html', note=note)
    else:
        error = 'Note not found'
        return render_template('main.html', error=error)
    
@app.route('/create_category', methods=['POST'])
def create_category():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    category_name = request.form['category_name']
    category = Category(name=category_name, user_id=session['user_id'])
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('main'))

@app.route('/create_note', methods=['POST'])
def create_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    category_id = request.form['category_id']
    note_title = request.form['note_title']
    note_content = request.form['note_content']
    note = Note(title=note_title, content=note_content, category_id=category_id)
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('category_notes', category_id=category_id))

@app.route('/result')
def result():
    text = request.args.get('text', '')
    return render_template('result.html', text=text)

@app.route('/all_texts')
def all_texts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    all_notes = []

    for category in user.categories:
        all_notes.extend(category.notes)

    return render_template('all_texts.html', user=user, categories=categories, all_notes=all_notes)

@app.route('/show_all_texts')
def show_all_texts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    all_notes = []

    for category in user.categories:
        all_notes.extend(category.notes)
        notes = category.notes
    
    return render_template('all_texts.html', notes=notes, all_notes=all_notes)

@app.route('/add_text', methods=['POST'])
def add_text():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category_id = request.form['category_id']
        note_title = 'Untitled'
        note_content = request.form['text']
        note = Note(title=note_title, content=note_content, category_id=category_id)
        db.session.add(note)
        db.session.commit()

        return redirect(url_for('all_texts'))

    categories = Category.query.filter_by(user_id=session['user_id']).all()
    return render_template('add_text.html', categories=categories)


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file.filename != '':
            image_path = 'uploaded_image.png'
            file.save(image_path)
            text = image_to_text(image_path)
            category_id = request.form['category_id']
            note_title = request.form['image_title']
            note_content = text
            note = Note(title=note_title, content=note_content, category_id=category_id)
            db.session.add(note)
            db.session.commit()

            return redirect(url_for('all_texts'))

    categories = Category.query.filter_by(user_id=session['user_id']).all()
    return render_template('upload_file.html', categories=categories)

@app.route('/remove_text', methods=['POST'])
def remove_text():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    category_id = request.form['category_id']
    note_id = request.form['note_id']
    note = Note.query.get(note_id)
    if note and note.category.user_id == session['user_id'] and str(note.category_id) == category_id:
        db.session.delete(note)
        db.session.commit()

    return redirect(url_for('category_notes', category_id=category_id))

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

@app.route('/add_text_from_image', methods=['POST'])
def add_text_from_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    image_file = request.files['image_file']
    image_title = request.form['image_title']
    category_id = request.form['category_id']

    # Create the 'uploads' directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Save the uploaded image file
    image_path = os.path.join('uploads', image_file.filename)
    image_file.save(image_path)

    # Process the image and extract text using the image_to_text helper function
    text = image_to_text(image_path)

    # Create a new note with the extracted text and image title
    note = Note(title=image_title, content=text, category_id=category_id)
    db.session.add(note)
    db.session.commit()

    return redirect(url_for('category_notes', category_id=category_id))

if __name__ == '__main__':
    app.run(debug=True)