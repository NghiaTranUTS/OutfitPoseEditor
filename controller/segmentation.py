from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import torch.nn as nn

# Initialize the processor and model for segmentation
processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")

def segment_image(image_path):
    """Segment the uploaded image and return the original image with a mask overlay."""
    # Load the image
    image = Image.open(image_path)

    # Prepare the image and run model inference
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits.cpu()
    
    # Upsample the logits to the original image size
    upsampled_logits = nn.functional.interpolate(
        logits, size=image.size[::-1], mode="bilinear", align_corners=False
    )
    pred_seg = upsampled_logits.argmax(dim=1)[0]
    
    return image, pred_seg

def create_mask_overlay(original_image, pred_seg):
    """Create a mask overlay based on the segmentation results."""
    # Define class colors (use a color map)
    color_map = plt.get_cmap("tab20")
    segment_image = color_map(pred_seg.numpy() / 20)  # 20 is the number of classes in the color map
    segment_image = (segment_image[:, :, :3] * 255).astype(np.uint8)  # Convert to uint8 format

    # Create a transparent overlay
    overlay = Image.fromarray(segment_image, 'RGB')
    overlay = overlay.convert("RGBA")

    # Combine original image with overlay
    original_image = original_image.convert("RGBA")
    combined = Image.alpha_composite(original_image, overlay)

    return combined

def save_segmented_image(image_path, output_path):
    """Segment the image and save the output."""
    original_image, pred_seg = segment_image(image_path)
    mask_overlay = create_mask_overlay(original_image, pred_seg)

    # Save the output image with the mask overlay
    mask_overlay.save(output_path)

if __name__ == "__main__":
    # Example usage
    input_image_path = "path/to/your/image.jpg"  # Change to the path of your image
    output_image_path = "path/to/save/segmented_image.png"  # Change to your desired output path
    save_segmented_image(input_image_path, output_image_path)