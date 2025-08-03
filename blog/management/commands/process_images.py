from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Process high-resolution images for web optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            help='Source directory containing high-res images',
        )
        parser.add_argument(
            '--target-dir',
            type=str,
            help='Target directory for processed images',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Maximum width for processed images',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='JPEG quality (1-100)',
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        target_dir = options['target_dir']
        max_width = options['max_width']
        quality = options['quality']

        if not source_dir:
            self.stdout.write(
                self.style.ERROR('Please provide a source directory with --source-dir')
            )
            return

        if not target_dir:
            target_dir = os.path.join(settings.MEDIA_ROOT, 'site_images', 'processed')

        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)

        # Process images
        processed_count = 0
        total_size_saved = 0

        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(target_dir, f"{Path(filename).stem}_web.jpg")

                try:
                    # Get original file size
                    original_size = os.path.getsize(source_path)

                    # Process image
                    with Image.open(source_path) as img:
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')

                        # Resize if needed
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                        # Save optimized version
                        img.save(target_path, 'JPEG', quality=quality, optimize=True)

                    # Get processed file size
                    processed_size = os.path.getsize(target_path)
                    size_saved = original_size - processed_size

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Processed: {filename} '
                            f'({original_size / 1024 / 1024:.1f}MB → '
                            f'{processed_size / 1024 / 1024:.1f}MB)'
                        )
                    )

                    processed_count += 1
                    total_size_saved += size_saved

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {filename}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nProcessing complete!\n'
                f'Processed {processed_count} images\n'
                f'Total space saved: {total_size_saved / 1024 / 1024:.1f}MB'
            )
        ) 