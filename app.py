from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set up message logging
message_logger = logging.getLogger('messageLogger')
message_logger.setLevel(logging.INFO)
message_handler = RotatingFileHandler('contact_messages.log', maxBytes=2000, backupCount=10)  # Rotate after 2KB
message_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
message_logger.addHandler(message_handler)

# Set up error logging
error_logger = logging.getLogger('errorLogger')
error_logger.setLevel(logging.ERROR)
error_handler = RotatingFileHandler('error.log', maxBytes=5000, backupCount=5)  # Rotate after 5KB
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Required for flashing messages

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


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message_content = request.form['message']

        # Log the contact message to the message log
        message_logger.info(f"Message from {name} ({email}): {message_content}")

        return jsonify({'status': 'success', 'message': 'Thank you for your message! We will get back to you soon.'})

    except Exception as e:
        # Log the error to the error log
        error_logger.error(f"Error occurred while processing contact form: {str(e)}")
        return jsonify({'status': 'error', 'message': 'There was an error processing your message.'}), 500


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
