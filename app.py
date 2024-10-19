from PIL import Image
from flask import Flask, render_template, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler
from controller.segmentation import segment_image, get_class_masks  # Import functions from segmentation.py

app = Flask(__name__)

# Set up message logging
message_logger = logging.getLogger('messageLogger')
message_logger.setLevel(logging.INFO)
message_handler = RotatingFileHandler('contact_messages.log', maxBytes=2000, backupCount=10)
message_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
message_logger.addHandler(message_handler)

# Set up error logging
error_logger = logging.getLogger('errorLogger')
error_logger.setLevel(logging.ERROR)
error_handler = RotatingFileHandler('error.log', maxBytes=5000, backupCount=5)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)

# Base folder configurations
BASE_UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.secret_key = 'your_secret_key'

# Ensure the base upload folder exists
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_upload_directory():
    """Generate a unique directory for each upload."""
    unique_id = uuid.uuid4().hex
    upload_directory = os.path.join(BASE_UPLOAD_FOLDER, unique_id)

    # Ensure uniqueness
    while os.path.exists(upload_directory):
        unique_id = uuid.uuid4().hex
        upload_directory = os.path.join(BASE_UPLOAD_FOLDER, unique_id)

    os.makedirs(upload_directory, exist_ok=True)
    return upload_directory


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
        error_logger.error(f"Error occurred while processing contact form: {str(e)}")
        return jsonify({'status': 'error', 'message': 'There was an error processing your message.'}), 500


@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            upload_directory = create_upload_directory()
            original_image_path = os.path.join(upload_directory, original_filename)
            file.save(original_image_path)

            # Segment the image using imported functions
            original_image, pred_seg = segment_image(original_image_path)
            masks = get_class_masks(pred_seg, num_classes=18)

            segment_masks = {}
            for class_id, mask in masks.items():
                mask_filename = f"mask_class_{class_id}.png"
                mask_path = os.path.join(upload_directory, mask_filename)  # Save masks in the correct upload directory
                mask_img = Image.fromarray(mask).convert("L")
                mask_img.save(mask_path)

                # Store the mask path relative to the base upload folder with upload_id included
                segment_masks[class_id] = os.path.join(upload_directory, mask_filename)

            return jsonify({
                'status': 'success',
                'message': 'Image uploaded and segmented successfully.',
                'upload_id': os.path.basename(upload_directory),
                'base_image_path': os.path.join(upload_directory, original_filename),  # Base image path
                'segmented_masks': segment_masks
            })

        return jsonify({'status': 'error', 'message': 'Unsupported file format. Please upload PNG, JPG, or JPEG images.'}), 400

    except Exception as e:
        error_logger.error(f"Error during upload: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred during upload.'}), 500


@app.route('/transform', methods=['POST'])
def transform():
    try:
        upload_id = request.json.get('upload_id')
        segment = request.json.get('segment')
        prompt = request.json.get('prompt')

        # Placeholder response for transformation
        transformed_image_url = f"{BASE_UPLOAD_FOLDER}{upload_id}/Beret.jpeg"  # Mock URL for transformed image

        return jsonify({
            'status': 'success',
            'message': 'Transformation would be applied successfully.',
            'transformed_image_url': transformed_image_url  # Return the mocked transformed image URL
        })

    except Exception as e:
        error_logger.error(f"Error during transformation: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred during transformation.'}), 500


if __name__ == "__main__":
    app.run(debug=True)
