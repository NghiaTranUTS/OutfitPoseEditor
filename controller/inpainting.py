import torch
from diffusers import AutoPipelineForInpainting
from PIL import Image
import numpy as np
from controller.segmentation import Segmentation  # Assuming segmentation is part of the controller


class Inpainting:
    def __init__(self, model_name="kandinsky-community/kandinsky-2-2-decoder-inpaint", torch_dtype=torch.float16):
        """Initialize the inpainting pipeline."""
        self.pipeline = AutoPipelineForInpainting.from_pretrained(
            model_name,
            torch_dtype=torch_dtype
        )
        self.pipeline.enable_model_cpu_offload()
        self.segmentation = Segmentation()

    def perform_inpainting(self, image_path, target_class_id, prompt, negative_prompt=None):
        """Perform inpainting based on the provided prompt and class segmentation."""
        # Load the original image
        original_image = Image.open(image_path).convert("RGB")

        # Segment the image
        _, pred_seg = self.segmentation.segment_image(image_path)

        # Generate the mask for the selected class
        mask_image = self.generate_mask_for_class(pred_seg, target_class_id)

        # Perform inpainting using the inpainting model
        edited_image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=original_image,
            mask_image=mask_image
        ).images[0]

        return original_image, mask_image, edited_image

    def generate_mask_for_class(self, pred_seg, target_class_id):
        """Generate a mask for the selected class."""
        mask = (pred_seg == target_class_id).numpy()  # Boolean mask where the target class is True
        mask_image = Image.fromarray((mask * 255).astype(np.uint8), 'L')  # Convert to uint8 and return mask
        return mask_image
