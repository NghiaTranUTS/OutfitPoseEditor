from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('service.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


def authenticate(username, password):
    pass


@app.route('/perform_login', methods=['POST'])
def perform_login():
    username = request.form['username']
    password = request.form['password']
    # Here you should add authentication logic
    if authenticate(username, password):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login', error="Invalid credentials"))


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    prompt = request.form['prompt']

    # Simulate the transformation process
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # Simulate a transformation and return a new image URL (replace this with AI logic)
    transformed_image_url = UPLOAD_FOLDER + file.filename  # Just returning the uploaded image for now

    # Return JSON response to AJAX
    return jsonify({"image_url": transformed_image_url})


if __name__ == "__main__":
    app.run(debug=True)
