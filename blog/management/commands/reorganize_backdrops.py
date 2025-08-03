from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import BackdropImage
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Reorganize backdrop images according to size and purpose'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--archive',
            action='store_true',
            help='Archive unused images instead of deleting them'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        archive = options['archive']
        
        # Define paths
        media_root = settings.MEDIA_ROOT
        site_images_dir = os.path.join(media_root, 'site_images')
        backdrops_dir = os.path.join(site_images_dir, 'backdrops')
        archive_dir = os.path.join(site_images_dir, 'archived_backdrops')
        
        # Image specifications
        portrait_images = ['shelfK_best.JPG']
        landscape_images = ['shelfL_RsideLight.JPG']
        small_images = ['shelfT_goodcloseup.JPG']
        
        # All images to keep
        keep_images = portrait_images + landscape_images + small_images
        
        # Get all backdrop images
        all_images = []
        if os.path.exists(site_images_dir):
            for file in os.listdir(site_images_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    all_images.append(file)
        
        self.stdout.write(f'Found {len(all_images)} backdrop images')
        
        # Create directories if needed
        if not dry_run:
            os.makedirs(backdrops_dir, exist_ok=True)
            if archive:
                os.makedirs(archive_dir, exist_ok=True)
        
        # Process each image
        moved_count = 0
        archived_count = 0
        deleted_count = 0
        
        for image in all_images:
            source_path = os.path.join(site_images_dir, image)
            
            if image in keep_images:
                # Move to backdrops directory
                dest_path = os.path.join(backdrops_dir, image)
                
                if dry_run:
                    self.stdout.write(f'Would move: {image} -> backdrops/')
                else:
                    try:
                        shutil.move(source_path, dest_path)
                        moved_count += 1
                        self.stdout.write(f'Moved: {image}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error moving {image}: {e}')
                        )
            else:
                # Archive or delete
                if archive:
                    archive_path = os.path.join(archive_dir, image)
                    if dry_run:
                        self.stdout.write(f'Would archive: {image} -> archived_backdrops/')
                    else:
                        try:
                            shutil.move(source_path, archive_path)
                            archived_count += 1
                            self.stdout.write(f'Archived: {image}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error archiving {image}: {e}')
                            )
                else:
                    if dry_run:
                        self.stdout.write(f'Would delete: {image}')
                    else:
                        try:
                            os.remove(source_path)
                            deleted_count += 1
                            self.stdout.write(f'Deleted: {image}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error deleting {image}: {e}')
                            )
        
        # Create backdrop records in database
        if not dry_run:
            self.create_backdrop_records(portrait_images, landscape_images, small_images)
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run complete. Would move {len(keep_images)} images, '
                    f'{"archive" if archive else "delete"} {len(all_images) - len(keep_images)} images.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully moved {moved_count} images, '
                    f'{"archived" if archive else "deleted"} {archived_count + deleted_count} images.'
                )
            )

    def create_backdrop_records(self, portrait_images, landscape_images, small_images):
        """Create or update backdrop records in the database."""
        
        # Portrait backdrops (page sized)
        for image in portrait_images:
            backdrop, created = BackdropImage.objects.get_or_create(
                name=f"Portrait Backdrop - {image.replace('.JPG', '')}",
                defaults={
                    'original_image': f'site_images/backdrops/{image}',
                    'processing_style': 'desaturated',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created backdrop record: {backdrop.name}')
            else:
                self.stdout.write(f'Updated backdrop record: {backdrop.name}')
        
        # Landscape backdrops
        for image in landscape_images:
            backdrop, created = BackdropImage.objects.get_or_create(
                name=f"Landscape Backdrop - {image.replace('.JPG', '')}",
                defaults={
                    'original_image': f'site_images/backdrops/{image}',
                    'processing_style': 'desaturated',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created backdrop record: {backdrop.name}')
            else:
                self.stdout.write(f'Updated backdrop record: {backdrop.name}')
        
        # Small backdrops (card infilling)
        for image in small_images:
            backdrop, created = BackdropImage.objects.get_or_create(
                name=f"Small Backdrop - {image.replace('.JPG', '')}",
                defaults={
                    'original_image': f'site_images/backdrops/{image}',
                    'processing_style': 'desaturated',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created backdrop record: {backdrop.name}')
            else:
                self.stdout.write(f'Updated backdrop record: {backdrop.name}') 