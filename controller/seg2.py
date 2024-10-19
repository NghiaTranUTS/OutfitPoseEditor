from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import os

# Check PyTorch version
print("PyTorch version:", torch.__version__)

# Initialize the processor and model for segmentation
processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")

def segment_image(image_path):
    """Segment the uploaded image and return the original image and the segmentation mask."""
    # Load the image
    image = Image.open(image_path)

    # Prepare the image and run model inference
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits.cpu()

    # Upsample the logits to match the original image's size
    upsampled_logits = nn.functional.interpolate(
        logits, size=image.size[::-1], mode="bilinear", align_corners=False
    )
    # Predicted segmentation class for each pixel
    pred_seg = upsampled_logits.argmax(dim=1)[0]

    return image, pred_seg

def get_class_masks(pred_seg, num_classes=20):
    """Extract individual binary masks for each class."""
    masks = {}
    for class_id in range(num_classes):
        # Create a binary mask for the given class ID
        masks[class_id] = (pred_seg == class_id).numpy().astype(np.uint8) * 255  # Binary mask scaled to 255
    return masks

def create_mask_overlay(original_image, pred_seg):
    """Create a combined mask overlay for all segments based on the segmentation results."""
    # Define a color map for visualization (adjust number of colors as per your use case)
    color_map = plt.get_cmap("tab20", 20)
    segment_image = color_map(pred_seg.numpy() / 20)  # Scale to [0, 1] range for color mapping
    segment_image = (segment_image[:, :, :3] * 255).astype(np.uint8)  # Convert to uint8 format

    # Create a transparent overlay from the color map
    overlay = Image.fromarray(segment_image, 'RGB')
    overlay = overlay.convert("RGBA")

    # Combine original image with overlay
    original_image = original_image.convert("RGBA")
    combined = Image.alpha_composite(original_image, overlay)

    return combined

def save_segmented_image(image_path, output_path):
    """Segment the image, create an overlay, and save the combined output."""
    original_image, pred_seg = segment_image(image_path)
    mask_overlay = create_mask_overlay(original_image, pred_seg)

    # Save the output image with the mask overlay
    mask_overlay.save(output_path)

def save_individual_masks(image_path, output_dir, num_classes=20):
    """Save individual masks for each segment class."""
    _, pred_seg = segment_image(image_path)
    masks = get_class_masks(pred_seg, num_classes=num_classes)

    # Save each mask as an individual image
    for class_id, mask in masks.items():
        mask_img = Image.fromarray(mask).convert("L")  # Convert to grayscale image
        mask_img.save(f"{output_dir}/mask_class_{class_id}.png")

if __name__ == "__main__":
    # Example usage
    input_image_path = r"C:\Users\whale\Games\CoCo\segment\beret.jpeg"  # Change to your input image path
    output_image_path = r"C:\Users\whale\Games\CoCo\segment\segmented_image.png"  # Change to your desired output path
    output_masks_dir = r"C:\Users\whale\Games\CoCo\segment\masks"  # Directory to save individual masks
    os.makedirs(output_masks_dir, exist_ok=True)
    # Save combined mask overlay image
    save_segmented_image(input_image_path, output_image_path)

    # Save individual masks for each segment class
    save_individual_masks(input_image_path, output_masks_dir)
