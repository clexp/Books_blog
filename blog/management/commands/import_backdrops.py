from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import BackdropImage
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Import backdrop images from directory and create BackdropImage records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--images-dir',
            type=str,
            default='media/site_images/backdrops/',
            help='Directory containing backdrop images'
        )
        parser.add_argument(
            '--processing-style',
            type=str,
            default='desaturated',
            choices=['original', 'desaturated', 'sepia', 'greyscale'],
            help='Processing style for backdrop images'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )

    def handle(self, *args, **options):
        images_dir = options['images_dir']
        processing_style = options['processing_style']
        dry_run = options['dry_run']
        
        if not os.path.exists(images_dir):
            self.stdout.write(
                self.style.ERROR(f'Images directory not found: {images_dir}')
            )
            return

        # Get all image files
        image_files = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                image_files.append(filename)
        
        self.stdout.write(f'Found {len(image_files)} backdrop images')
        
        imported_count = 0
        
        for filename in image_files:
            # Create name from filename
            name = self._create_name_from_filename(filename)
            
            if dry_run:
                self.stdout.write(
                    f'Would import: {name} ({filename}) with style: {processing_style}'
                )
            else:
                try:
                    # Check if backdrop with this name already exists
                    existing = BackdropImage.objects.filter(name=name).first()
                    if existing:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {name} - already exists')
                        )
                        continue
                    
                    # Create new backdrop record
                    backdrop = BackdropImage(
                        name=name,
                        processing_style=processing_style
                    )
                    
                    # Set the original image
                    image_path = os.path.join(images_dir, filename)
                    with open(image_path, 'rb') as img_file:
                        backdrop.original_image.save(filename, img_file, save=False)
                    
                    # Save to trigger processing
                    backdrop.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Imported: {name} ({filename})'
                        )
                    )
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing {filename}: {e}')
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully imported {imported_count} backdrop images')
            )
        else:
            self.stdout.write(f'\nWould import {len(image_files)} backdrop images')

    def _create_name_from_filename(self, filename):
        """Create a readable name from filename."""
        # Remove extension
        name = Path(filename).stem
        
        # Replace underscores and dashes with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Add "Backdrop" if not present
        if 'backdrop' not in name.lower():
            name += ' Backdrop'
        
        return name 