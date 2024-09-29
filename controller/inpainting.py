import torch
from diffusers import AutoPipelineForInpainting
from PIL import Image
import numpy as np
from segmentation import segment_image, generate_mask_for_class  # Importing the necessary function from segmentation.py

def perform_inpainting(image_path, target_class_id, prompt, negative_prompt):
    """ Perform segmentation, generate a mask, and apply inpainting based on the provided prompt. """
    # Load the original image
    original_image = Image.open(image_path).convert("RGB")

    # Segment the image and get predictions
    _, pred_seg = segment_image(image_path)

    # Generate mask for the selected class ID
    mask_image = generate_mask_for_class(pred_seg, target_class_id)

    # Load the inpainting pipeline
    pipeline = AutoPipelineForInpainting.from_pretrained(
        "kandinsky-community/kandinsky-2-2-decoder-inpaint",
        torch_dtype=torch.float16
    )
    pipeline.enable_model_cpu_offload()
    
    # Perform inpainting
    edited_image = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=original_image,
        mask_image=mask_image
    ).images[0]

    return original_image, mask_image, edited_image

def generate_mask_for_class(pred_seg, target_class_id):
    """ Generate a mask for the selected class from the segmentation output. """
    # Generate a boolean mask where target class pixels are True
    mask = (pred_seg == target_class_id).numpy()
    # Convert boolean mask to uint8 mask where target class pixels are 255 (white), others are 0 (black)
    return Image.fromarray((mask * 255).astype(np.uint8), 'L')

if __name__ == "__main__":
    image_path = "path/to/image.jpg"  # Change to the path of the image
    target_class_id = 6  # Change as needed
    prompt = "Change shirt to jacket"  # Example prompt
    negative_prompt = "Minimalistic"  # Example negative prompt

    original_image, mask_image, edited_image = perform_inpainting(image_path, target_class_id, prompt, negative_prompt)

    # Save the results
    original_image.save("original_image.jpg")
    mask_image.save("mask_image.png")
    edited_image.save("edited_image.jpg")
