"""
Advanced image processing utilities using Pillow and ffmpeg.
"""
import subprocess
import os
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from django.conf import settings


class AdvancedImageProcessor:
    """
    Advanced image processing with both Pillow and ffmpeg support.
    """
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is available on the system."""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def process_backdrop(self, input_path, output_path, style='desaturated'):
        """
        Process backdrop images with advanced techniques.
        
        Args:
            input_path: Path to input image
            output_path: Path for output image
            style: Processing style ('desaturated', 'sepia', 'greyscale', 'vintage')
        """
        if style == 'vintage' and self.ffmpeg_available:
            return self._process_vintage_ffmpeg(input_path, output_path)
        else:
            return self._process_backdrop_pillow(input_path, output_path, style)
    
    def _process_backdrop_pillow(self, input_path, output_path, style):
        """Process backdrop using Pillow."""
        with Image.open(input_path) as img:
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply style-specific processing
            if style == 'desaturated':
                img = self._desaturate_advanced(img, factor=0.3)
            elif style == 'sepia':
                img = self._apply_sepia_advanced(img)
            elif style == 'greyscale':
                img = img.convert('L').convert('RGB')
            elif style == 'vintage':
                img = self._apply_vintage_effect(img)
            
            # Add subtle blur for backdrop effect
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Optimize and save
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            return output_path
    
    def _desaturate_advanced(self, img, factor=0.3):
        """Advanced desaturation with color preservation."""
        # Convert to HSV
        hsv = img.convert('HSV')
        h, s, v = hsv.split()
        
        # Reduce saturation more aggressively
        s = s.point(lambda x: int(x * factor))
        
        # Slightly reduce brightness for backdrop effect
        v = v.point(lambda x: int(x * 0.95))
        
        hsv = Image.merge('HSV', (h, s, v))
        return hsv.convert('RGB')
    
    def _apply_sepia_advanced(self, img):
        """Advanced sepia with better color balance."""
        # Custom sepia matrix for more natural look
        sepia_matrix = [
            0.393, 0.769, 0.189,
            0.349, 0.686, 0.168,
            0.272, 0.534, 0.131
        ]
        
        img = img.convert('RGB', matrix=sepia_matrix)
        
        # Add slight contrast enhancement
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.1)
    
    def _apply_vintage_effect(self, img):
        """Apply vintage film effect."""
        # Convert to sepia first
        img = self._apply_sepia_advanced(img)
        
        # Add slight noise/grain effect
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Slightly reduce brightness
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(0.9)
    
    def _process_vintage_ffmpeg(self, input_path, output_path):
        """Process vintage effect using ffmpeg for better quality."""
        if not self.ffmpeg_available:
            return self._process_backdrop_pillow(input_path, output_path, 'vintage')
        
        # ffmpeg command for vintage effect
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'colorbalance=rs=-0.1:gs=-0.1:bs=0.1,eq=saturation=0.3:contrast=1.1',
            '-q:v', '3',  # High quality
            '-y',  # Overwrite output
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError:
            # Fallback to Pillow if ffmpeg fails
            return self._process_backdrop_pillow(input_path, output_path, 'vintage')
    
    def create_thumbnail(self, input_path, output_path, size=(300, 300)):
        """Create optimized thumbnail."""
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(output_path, 'JPEG', quality=90, optimize=True)
            return output_path
    
    def batch_process(self, source_dir, target_dir, style='desaturated'):
        """Batch process all images in a directory."""
        processor = AdvancedImageProcessor()
        processed_files = []
        
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                input_path = os.path.join(source_dir, filename)
                output_filename = f"{Path(filename).stem}_processed.jpg"
                output_path = os.path.join(target_dir, output_filename)
                
                try:
                    processor.process_backdrop(input_path, output_path, style)
                    processed_files.append(output_filename)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        return processed_files


def optimize_book_cover(input_path, output_path, max_width=800):
    """Optimize book cover images for web display."""
    with Image.open(input_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with high quality for book covers
        img.save(output_path, 'JPEG', quality=95, optimize=True)
        return output_path


def create_author_thumbnail(input_path, output_path, size=(200, 200)):
    """Create circular thumbnail for author photos."""
    with Image.open(input_path) as img:
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create square crop
        width, height = img.size
        size_square = min(width, height)
        left = (width - size_square) // 2
        top = (height - size_square) // 2
        right = left + size_square
        bottom = top + size_square
        
        img = img.crop((left, top, right, bottom))
        
        # Resize to target size
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        # Apply mask
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Save as PNG for transparency
        output.save(output_path, 'PNG', optimize=True)
        return output_path 