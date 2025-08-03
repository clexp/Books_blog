# Image Processing Guide for Books Blog

## Overview

This guide covers the image processing system for your Django blog, designed to handle high-resolution book photos and backdrop images efficiently.

## Image Storage Structure

```
media/
├── book_covers/          # Book cover images
├── author_photos/        # Author profile images
├── site_images/
│   ├── backdrops/       # Original high-res backdrop images
│   ├── backdrops/processed/  # Optimized backdrop images
│   └── processed/       # General processed images
```

## Image Processing Tools

### 1. Pillow (PIL) - Primary Tool

- **Purpose**: Resizing, format conversion, basic effects
- **Best for**: Book covers, author photos, general optimization
- **Quality**: Excellent for web optimization

### 2. FFmpeg - Advanced Processing

- **Purpose**: Advanced color grading, vintage effects
- **Best for**: Backdrop images, artistic effects
- **Quality**: Professional-grade processing

## Backdrop Image Strategy

### Recommended Processing Styles

1. **Low Saturation (Recommended)**

   - Maintains color warmth
   - Doesn't compete with content
   - Professional appearance
   - Good for most use cases

2. **Sepia Tone**

   - Classic, warm appearance
   - Good for vintage/classic themes
   - Maintains visual interest

3. **Greyscale**

   - Clean, minimal appearance
   - Good for modern/minimal designs
   - May be too stark for some content

4. **Vintage Effect**
   - Advanced processing with ffmpeg
   - Film-like appearance
   - Best quality with ffmpeg installed

## Usage Instructions

### 1. Processing High-Resolution Images

Use the Django management command:

```bash
# Process all images in a directory
python manage.py process_images --source-dir /path/to/high-res-images --target-dir media/site_images/processed

# Custom settings
python manage.py process_images \
  --source-dir /path/to/images \
  --target-dir media/site_images/processed \
  --max-width 1920 \
  --quality 85
```

### 2. Adding Backdrop Images via Admin

1. Go to Django Admin → Backdrop Images
2. Click "Add Backdrop Image"
3. Upload your high-resolution image
4. Select processing style:
   - **Desaturated**: Best for most backdrops
   - **Sepia**: Classic, warm look
   - **Greyscale**: Clean, minimal
   - **Original**: Keep original colors
5. Save - image will be automatically processed

### 3. Batch Processing with Python

```python
from blog.utils.image_processor import AdvancedImageProcessor

# Initialize processor
processor = AdvancedImageProcessor()

# Process single image
processor.process_backdrop(
    'path/to/original.jpg',
    'path/to/processed.jpg',
    style='desaturated'
)

# Batch process directory
processed_files = processor.batch_process(
    'path/to/source/dir',
    'path/to/target/dir',
    style='desaturated'
)
```

### 4. Optimizing Book Covers

```python
from blog.utils.image_processor import optimize_book_cover

# Optimize book cover for web
optimize_book_cover(
    'path/to/original_cover.jpg',
    'path/to/optimized_cover.jpg',
    max_width=800
)
```

## File Size Optimization

### Target File Sizes

- **Book Covers**: 200-500KB (800px max width)
- **Author Photos**: 50-150KB (200px max width)
- **Backdrop Images**: 500KB-2MB (1920px max width)
- **Thumbnails**: 20-50KB (300px max width)

### Quality Settings

- **Book Covers**: 95% quality (high detail needed)
- **Author Photos**: 90% quality (good balance)
- **Backdrop Images**: 85% quality (good for size)
- **Thumbnails**: 85% quality (adequate detail)

## Installation Requirements

### Pillow (Required)

```bash
pip install Pillow>=10.0.0
```

### FFmpeg (Optional, for advanced effects)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Best Practices

### 1. Image Preparation

- Use high-resolution source images (5MB+ is fine)
- Prefer JPEG for photos, PNG for graphics
- Ensure good lighting and composition

### 2. Processing Workflow

1. Upload original high-res images
2. Let the system process them automatically
3. Review processed images in admin
4. Adjust processing style if needed
5. Use processed images in templates

### 3. Performance Considerations

- Process images during development/testing
- Use CDN for production (if available)
- Monitor file sizes and loading times
- Consider lazy loading for large images

### 4. Template Usage

```html
<!-- For backdrop images -->
{% if backdrop_image %}
<div
  class="backdrop"
  style="background-image: url('{{ backdrop_image.processed_image.url }}');"
>
  <!-- Content -->
</div>
{% endif %}

<!-- For book covers -->
{% if book.cover_image %}
<img
  src="{{ book.cover_image.url }}"
  alt="{{ book.title }}"
  class="book-cover"
/>
{% endif %}
```

## Troubleshooting

### Common Issues

1. **Large File Sizes**

   - Reduce quality setting (85% instead of 95%)
   - Reduce max width
   - Use more aggressive compression

2. **Poor Image Quality**

   - Increase quality setting
   - Use higher resolution source images
   - Check processing style settings

3. **Processing Errors**

   - Ensure Pillow is installed
   - Check file permissions
   - Verify image format support

4. **FFmpeg Not Available**
   - System will fallback to Pillow processing
   - Vintage effects may not be available
   - Other effects work normally

### Debug Commands

```bash
# Check Pillow installation
python -c "from PIL import Image; print('Pillow OK')"

# Check FFmpeg availability
ffmpeg -version

# Test image processing
python manage.py process_images --source-dir test_images --target-dir test_output
```

## Advanced Features

### Custom Processing Styles

You can extend the `AdvancedImageProcessor` class to add custom processing styles:

```python
def _apply_custom_effect(self, img):
    """Apply your custom image effect."""
    # Your custom processing code here
    return processed_img
```

### Batch Processing Scripts

Create custom scripts for specific processing needs:

```python
# Example: Process all book covers
from blog.utils.image_processor import optimize_book_cover
import os

for filename in os.listdir('media/book_covers/'):
    if filename.endswith('.jpg'):
        input_path = f'media/book_covers/{filename}'
        output_path = f'media/book_covers/optimized/{filename}'
        optimize_book_cover(input_path, output_path)
```

This system provides professional-grade image processing while maintaining excellent performance and user experience.
