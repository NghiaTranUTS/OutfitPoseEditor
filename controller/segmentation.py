from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
import os


# Initialize processor and model for segmentation
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

def get_class_masks(pred_seg, num_classes=18):
    """Extract individual binary masks for each class."""
    masks = {}
    for class_id in range(num_classes):
        # Create a binary mask for the given class ID
        masks[class_id] = (pred_seg == class_id).numpy().astype(np.uint8) * 255  # Binary mask scaled to 255
    return masks

def save_mask(mask, class_id, output_dir):
    """Save individual mask for a given class."""
    mask_img = Image.fromarray(mask).convert("L")
    mask_filename = f"mask_class_{class_id}.png"
    mask_path = os.path.join(output_dir, mask_filename)
    mask_img.save(mask_path)
    return mask_path
