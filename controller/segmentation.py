from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image, ImageOps
import numpy as np
import torch.nn as nn
import os


class Segmentation:
    def __init__(self, model_name="mattmdjaga/segformer_b2_clothes", num_classes=18):
        self.processor = SegformerImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForSemanticSegmentation.from_pretrained(model_name)
        self.num_classes = num_classes

    def segment_image(self, image_path):
        """Segment the uploaded image and return the original image and the segmentation mask."""
        image = Image.open(image_path)

        # Prepare the image and run model inference
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits.cpu()

        # Upsample the logits to match the original image's size
        upsampled_logits = nn.functional.interpolate(
            logits, size=image.size[::-1], mode="bilinear", align_corners=False
        )
        pred_seg = upsampled_logits.argmax(dim=1)[0]  # Predicted segmentation class for each pixel

        return image, pred_seg

    def get_class_masks(self, pred_seg):
        """Extract individual binary masks for each class."""
        masks = {}
        for class_id in range(self.num_classes):
            # Create a binary mask for the given class ID
            masks[class_id] = (pred_seg == class_id).numpy().astype(np.uint8) * 255  # Binary mask scaled to 255
        return masks

    def save_mask(self, mask, class_id, output_dir):
        """Save individual mask for a given class."""
        mask_img = Image.fromarray(mask).convert("L")
        mask_filename = f"mask_class_{class_id}.png"
        mask_path = os.path.join(output_dir, mask_filename)
        mask_img.save(mask_path)
        return mask_path

    def crop_pad_square(self, image, mask):
        """Crop the image with the buffered bounding box, adjust the crop-square, and pad to a square size."""
        non_zero_coords = np.argwhere(mask > 0)

        # Get the top-left and bottom-right corners of the bounding box
        top_left = non_zero_coords.min(axis=0)
        bottom_right = non_zero_coords.max(axis=0)

        # Calculate the width and height of the bounding box
        bbox_width = bottom_right[1] - top_left[1]
        bbox_height = bottom_right[0] - top_left[0]

        # Add a 10% buffer (5% on each side)
        buffer_width = int(bbox_width * 0.1 / 2)
        buffer_height = int(bbox_height * 0.1 / 2)

        # Create the buffered bounding box
        buffered_top_left = (top_left[0] - buffer_height, top_left[1] - buffer_width)
        buffered_bottom_right = (bottom_right[0] + buffer_height, bottom_right[1] + buffer_width)

        # Adjust crop to minimize padding (as discussed earlier)
        crop_width = buffered_bottom_right[1] - buffered_top_left[1]
        crop_height = buffered_bottom_right[0] - buffered_top_left[0]

        # Make a square
        crop_size = max(crop_width, crop_height)

        # Crop and pad the image to a square
        crop_box = (
            max(0, buffered_top_left[1]), max(0, buffered_top_left[0]),
            min(image.width, buffered_bottom_right[1]), min(image.height, buffered_bottom_right[0])
        )
        cropped_image = image.crop(crop_box)
        padded_image = ImageOps.pad(cropped_image, (crop_size, crop_size), color=(0, 0, 0))

        # Resize to 512x512
        resized_image = padded_image.resize((512, 512), Image.Resampling.LANCZOS)

        return resized_image
