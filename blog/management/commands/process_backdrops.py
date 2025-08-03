from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import BackdropImage
import os


class Command(BaseCommand):
    help = 'Process backdrop images with various effects (desaturation, sepia, greyscale, whitened)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--style',
            type=str,
            choices=['original', 'desaturated', 'sepia', 'greyscale', 'whitened'],
            default='desaturated',
            help='Processing style to apply'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all backdrop images'
        )
        parser.add_argument(
            '--backdrop-id',
            type=int,
            help='Process specific backdrop by ID'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing even if processed image exists'
        )

    def handle(self, *args, **options):
        style = options['style']
        process_all = options['all']
        backdrop_id = options['backdrop_id']
        force = options['force']
        
        if backdrop_id:
            # Process specific backdrop
            try:
                backdrop = BackdropImage.objects.get(id=backdrop_id)
                self.process_backdrop(backdrop, style, force)
            except BackdropImage.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Backdrop with ID {backdrop_id} not found')
                )
                return
        elif process_all:
            # Process all backdrops
            backdrops = BackdropImage.objects.all()
            if not backdrops:
                self.stdout.write(
                    self.style.WARNING('No backdrop images found')
                )
                return
                
            self.stdout.write(f'Processing {backdrops.count()} backdrop images...')
            for backdrop in backdrops:
                self.process_backdrop(backdrop, style, force)
        else:
            # Show available backdrops
            backdrops = BackdropImage.objects.all()
            if not backdrops:
                self.stdout.write(
                    self.style.WARNING('No backdrop images found. Add some in the admin panel.')
                )
                return
                
            self.stdout.write('Available backdrop images:')
            for backdrop in backdrops:
                self.stdout.write(f'  ID {backdrop.id}: {backdrop.name}')
            
            self.stdout.write('\nUse --all to process all backdrops or --backdrop-id <id> to process specific one.')
            return

    def process_backdrop(self, backdrop, style, force=False):
        """Process a single backdrop image."""
        if not backdrop.original_image:
            self.stdout.write(
                self.style.ERROR(f'Backdrop "{backdrop.name}" has no original image')
            )
            return
            
        if backdrop.processed_image and not force:
            self.stdout.write(
                self.style.WARNING(f'Backdrop "{backdrop.name}" already has processed image. Use --force to reprocess.')
            )
            return
            
        try:
            # Update processing style
            backdrop.processing_style = style
            backdrop.save()
            
            # Process the image
            backdrop.process_image()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed "{backdrop.name}" with {style} style')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing "{backdrop.name}": {e}')
            ) 