"""Image processing tool for basic image operations."""

import os
import base64
from typing import Dict, Any
from .base import Tool

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageProcessingTool(Tool):
    """Tool for basic image processing operations."""

    def __init__(self):
        super().__init__(
            name="image_processing",
            description="Process images: resize, enhance, apply filters, convert formats, analyze properties"
        )

        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL/Pillow is required for ImageProcessingTool. Install with: pip install Pillow")

    def execute(self, operation: str, **kwargs) -> str:
        """Execute image processing operations."""
        try:
            if operation == "resize":
                return self._resize_image(
                    kwargs.get('input_path'),
                    kwargs.get('output_path'),
                    kwargs.get('width'),
                    kwargs.get('height')
                )
            elif operation == "enhance":
                return self._enhance_image(
                    kwargs.get('input_path'),
                    kwargs.get('output_path'),
                    kwargs.get('enhancement_type'),
                    kwargs.get('factor', 1.5)
                )
            elif operation == "filter":
                return self._apply_filter(
                    kwargs.get('input_path'),
                    kwargs.get('output_path'),
                    kwargs.get('filter_type')
                )
            elif operation == "convert":
                return self._convert_format(
                    kwargs.get('input_path'),
                    kwargs.get('output_path'),
                    kwargs.get('format')
                )
            elif operation == "analyze":
                return self._analyze_image(kwargs.get('input_path'))
            elif operation == "thumbnail":
                return self._create_thumbnail(
                    kwargs.get('input_path'),
                    kwargs.get('output_path'),
                    kwargs.get('size', 128)
                )
            else:
                return f"Error: Unknown operation '{operation}'"
        except Exception as e:
            return f"Image processing error: {str(e)}"

    def _resize_image(self, input_path: str, output_path: str, width: int, height: int) -> str:
        """Resize an image to specified dimensions."""
        if not all([input_path, output_path, width, height]):
            return "Error: input_path, output_path, width, and height are required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        with Image.open(input_path) as img:
            resized = img.resize((int(width), int(height)),
                                 Image.Resampling.LANCZOS)
            resized.save(output_path)

            return f"✅ Image resized to {width}x{height} and saved to {output_path}"

    def _enhance_image(self, input_path: str, output_path: str, enhancement_type: str, factor: float) -> str:
        """Enhance image brightness, contrast, color, or sharpness."""
        if not all([input_path, output_path, enhancement_type]):
            return "Error: input_path, output_path, and enhancement_type are required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        with Image.open(input_path) as img:
            if enhancement_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
            elif enhancement_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
            elif enhancement_type == "color":
                enhancer = ImageEnhance.Color(img)
            elif enhancement_type == "sharpness":
                enhancer = ImageEnhance.Sharpness(img)
            else:
                return f"Error: Unknown enhancement type '{enhancement_type}'"

            enhanced = enhancer.enhance(factor)
            enhanced.save(output_path)

            return f"✅ Image enhanced ({enhancement_type}, factor: {factor}) and saved to {output_path}"

    def _apply_filter(self, input_path: str, output_path: str, filter_type: str) -> str:
        """Apply filters to an image."""
        if not all([input_path, output_path, filter_type]):
            return "Error: input_path, output_path, and filter_type are required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        filter_map = {
            "blur": ImageFilter.BLUR,
            "contour": ImageFilter.CONTOUR,
            "detail": ImageFilter.DETAIL,
            "edge_enhance": ImageFilter.EDGE_ENHANCE,
            "emboss": ImageFilter.EMBOSS,
            "smooth": ImageFilter.SMOOTH,
            "sharpen": ImageFilter.SHARPEN
        }

        if filter_type not in filter_map:
            available_filters = ", ".join(filter_map.keys())
            return f"Error: Unknown filter '{filter_type}'. Available: {available_filters}"

        with Image.open(input_path) as img:
            filtered = img.filter(filter_map[filter_type])
            filtered.save(output_path)

            return f"✅ Filter '{filter_type}' applied and saved to {output_path}"

    def _convert_format(self, input_path: str, output_path: str, format: str) -> str:
        """Convert image to different format."""
        if not all([input_path, output_path, format]):
            return "Error: input_path, output_path, and format are required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        with Image.open(input_path) as img:
            # Convert to RGB if saving as JPEG
            if format.upper() == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.save(output_path, format=format.upper())

            return f"✅ Image converted to {format.upper()} and saved to {output_path}"

    def _analyze_image(self, input_path: str) -> str:
        """Analyze image properties."""
        if not input_path:
            return "Error: input_path is required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        with Image.open(input_path) as img:
            file_size = os.path.getsize(input_path)

            info = {
                "filename": os.path.basename(input_path),
                "format": img.format,
                "mode": img.mode,
                "size": f"{img.size[0]}x{img.size[1]}",
                "file_size": f"{file_size / 1024:.1f} KB"
            }

            # Get color analysis for RGB images
            if img.mode == 'RGB':
                colors = img.getcolors(maxcolors=256*256*256)
                if colors:
                    dominant_color = max(colors, key=lambda x: x[0])[1]
                    info["dominant_color"] = f"RGB{dominant_color}"

            analysis = "📊 Image Analysis:\n"
            for key, value in info.items():
                analysis += f"• {key.replace('_', ' ').title()}: {value}\n"

            return analysis

    def _create_thumbnail(self, input_path: str, output_path: str, size: int) -> str:
        """Create a thumbnail of the image."""
        if not all([input_path, output_path]):
            return "Error: input_path and output_path are required"

        if not os.path.exists(input_path):
            return f"Error: Input file not found: {input_path}"

        with Image.open(input_path) as img:
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            img.save(output_path)

            return f"✅ Thumbnail ({size}x{size}) created and saved to {output_path}"

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["resize", "enhance", "filter", "convert", "analyze", "thumbnail"],
                    "description": "Image processing operation to perform"
                },
                "input_path": {
                    "type": "string",
                    "description": "Path to the input image file"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path where the processed image will be saved"
                },
                "width": {
                    "type": "integer",
                    "description": "Width for resize operation"
                },
                "height": {
                    "type": "integer",
                    "description": "Height for resize operation"
                },
                "enhancement_type": {
                    "type": "string",
                    "enum": ["brightness", "contrast", "color", "sharpness"],
                    "description": "Type of enhancement to apply"
                },
                "factor": {
                    "type": "number",
                    "description": "Enhancement factor (1.0 = no change, >1.0 = increase, <1.0 = decrease)"
                },
                "filter_type": {
                    "type": "string",
                    "enum": ["blur", "contour", "detail", "edge_enhance", "emboss", "smooth", "sharpen"],
                    "description": "Type of filter to apply"
                },
                "format": {
                    "type": "string",
                    "enum": ["JPEG", "PNG", "BMP", "TIFF", "WEBP"],
                    "description": "Output format for conversion"
                },
                "size": {
                    "type": "integer",
                    "description": "Size for thumbnail (creates square thumbnail)"
                }
            },
            "required": ["operation", "input_path"]
        }
