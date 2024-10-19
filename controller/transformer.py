from PIL import Image
import os
import torch
from diffusers import AutoPipelineForInpainting

# Load the model once to avoid reloading on every request
model = AutoPipelineForInpainting.from_pretrained(
    "kandinsky-community/kandinsky-2-2-decoder-inpaint",
    torch_dtype=torch.float16
)

def transform_image(upload_id, segment, prompt, base_upload_folder):
    upload_directory = os.path.join(base_upload_folder, upload_id)

    if not os.path.exists(upload_directory):
        return {'status': 'error', 'message': 'Invalid upload ID.'}

    # Load original image
    original_image_path = os.path.join(upload_directory, f'original_image.png')
    original_image = Image.open(original_image_path)

    # Set up the transformation parameters
    transformation_params = {
        'segment': segment,
        'prompt': prompt,
        'image': original_image  # This would be replaced with the actual mask to apply
    }

    # Process the image using the model (example)
    transformed_image = model(**transformation_params).images[0]

    # Save the transformed image
    transformed_filename = f'transformed_{segment}.png'
    transformed_image_path = os.path.join(upload_directory, transformed_filename)
    transformed_image.save(transformed_image_path)

    transformed_image_url = os.path.join(base_upload_folder, upload_id, transformed_filename)

    return {
        'status': 'success',
        'message': 'Transformation applied successfully.',
        'transformed_image_url': transformed_image_url
    }
