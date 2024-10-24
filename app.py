from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler
from controller.segmentation import Segmentation  # Importing Segmentation class
from controller.inpainting import Inpainting  # Importing Inpainting class
import threading
import time
import shutil
from datetime import datetime, timedelta

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


def delete_old_folders():
    """Background thread to delete folders older than one day."""
    while True:
        now = datetime.now()
        for subfolder in os.listdir(BASE_UPLOAD_FOLDER):
            subfolder_path = os.path.join(BASE_UPLOAD_FOLDER, subfolder)
            if os.path.isdir(subfolder_path):
                folder_creation_time = datetime.fromtimestamp(os.path.getctime(subfolder_path))
                if now - folder_creation_time > timedelta(days=1):
                    try:
                        shutil.rmtree(subfolder_path)
                        print(f"Deleted old folder: {subfolder_path}")
                    except Exception as e:
                        error_logger.error(f"Error deleting folder {subfolder_path}: {str(e)}")
        time.sleep(3600)


cleanup_thread = threading.Thread(target=delete_old_folders, daemon=True)
cleanup_thread.start()


@app.route('/')
def index():
    return render_template('service.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'img/logo1.png', mimetype='image/vnd.microsoft.icon')

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
            original_filename = "original_image.png"
            upload_directory = create_upload_directory()
            original_image_path = os.path.join(upload_directory, original_filename)

            # Convert to PNG and save
            with Image.open(file) as img:
                # Convert the image to a format that ensures channel consistency
                if img.mode != 'RGB':
                    img = img.convert('RGB')  # Ensure the image is in RGB format
                img.save(original_image_path, format="PNG")

            # Initialize the Segmentation object
            segmentation = Segmentation()

            # Perform segmentation before resizing
            original_image, pred_seg = segmentation.segment_image(original_image_path)
            masks = segmentation.get_class_masks(pred_seg)

            # Crop, pad, and resize the original image
            resized_image = segmentation.crop_pad_square(original_image, masks[0])
            resized_image_path = os.path.join(upload_directory, "resized_image.png")
            resized_image.save(resized_image_path)

            # Perform segmentation again on the resized image
            resized_image, resized_pred_seg = segmentation.segment_image(resized_image_path)
            resized_masks = segmentation.get_class_masks(resized_pred_seg)

            # Save the masks and prepare the response
            segment_masks = {}
            for class_id, mask in resized_masks.items():
                mask_path = segmentation.save_mask(mask, class_id, upload_directory)
                segment_masks[class_id] = mask_path

            return jsonify({
                'status': 'success',
                'message': 'Image uploaded, resized, and segmented successfully.',
                'upload_id': os.path.basename(upload_directory),
                'base_image_path': resized_image_path.replace("\\", "/"),
                'segmented_masks': segment_masks
            })

        return jsonify({'status': 'error', 'message': 'Unsupported file format. Please upload PNG, JPG, or JPEG'}), 400

    except Exception as e:
        error_logger.error(f"Error during upload: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred during upload.'}), 500


@app.route('/transform', methods=['POST'])
def transform():
    try:
        # Log/Print the entire incoming request JSON for debugging
        data = request.get_json()  # Get the JSON payload
        print(f"Received JSON: {data}")  # Log to console

        # Extract parameters from the JSON request
        upload_id = data.get('upload_id')
        transformations = data.get('transformations')
        print(f"upload_id: {upload_id}")
        print(f"transformations: {transformations}")

        # Assuming 'segment' is one of the keys in transformations (e.g., {4: {Change Style: "T-shirt"}})
        if transformations:
            for segment, transformation_details in transformations.items():
                print(f"Segment: {segment}, Transformation Details: {transformation_details}")

                # Combine all transformations into a single prompt
                prompt_parts = []
                for key, value in transformation_details.items():
                    prompt_parts.append(f"{key} to {value}")

                # Join all parts into a single prompt string
                prompt = ", ".join(prompt_parts)
                print(f"Prompt: {prompt}")

        # Validate inputs
        if not upload_id:
            return jsonify({'status': 'error', 'message': 'Upload ID is missing.'}), 400
        if not transformations:
            return jsonify({'status': 'error', 'message': 'Transformations are missing.'}), 400

        # Construct the image path
        image_path = os.path.join(BASE_UPLOAD_FOLDER, upload_id, "resized_image.png")
        print(f"Image path: {image_path}")

        # Initialize the Inpainting object
        inpainting = Inpainting()

        # Assuming we're only working with the first transformation (for simplicity)
        target_class_id = int(segment)  # Convert segment to int
        negative_prompt = None  # Assuming no negative prompt in this example

        # Perform inpainting
        original_image, mask_image, edited_image = inpainting.perform_inpainting(
            image_path=image_path,
            target_class_id=target_class_id,
            prompt=prompt,
            negative_prompt=negative_prompt
        )

        # Save the edited image
        edited_image_path = os.path.join(BASE_UPLOAD_FOLDER, upload_id, "edited_image.png")
        edited_image.save(edited_image_path)

        return jsonify({
            'status': 'success',
            'message': 'Transformation applied successfully.',
            'transformed_image_url': edited_image_path.replace("\\", "/")
        })

    except Exception as e:
        error_logger.error(f"Error during transformation: {str(e)}")
        return jsonify({'status': 'error', 'message': f'An error occurred during transformation: {str(e)}'}), 500


if __name__ == "__main__":
    app.run(debug=True)
