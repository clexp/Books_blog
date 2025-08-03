from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from pathlib import Path
from blog.models import Book


class Command(BaseCommand):
    help = 'Reorganize book images by moving open book images to a new folder and removing them from book records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Define paths
        media_root = settings.MEDIA_ROOT
        book_covers_dir = os.path.join(media_root, 'book_covers')
        open_books_dir = os.path.join(media_root, 'open_book_images')
        
        if not os.path.exists(book_covers_dir):
            self.stdout.write(
                self.style.ERROR(f'Book covers directory not found: {book_covers_dir}')
            )
            return
        
        # Create open_books directory if it doesn't exist
        if not dry_run:
            os.makedirs(open_books_dir, exist_ok=True)
            self.stdout.write(f'Created directory: {open_books_dir}')
        
        # Get all books with cover images
        books_with_covers = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='')
        
        self.stdout.write(f'Found {books_with_covers.count()} books with cover images')
        
        moved_count = 0
        cleared_count = 0
        
        for book in books_with_covers:
            if not book.cover_image:
                continue
                
            cover_path = book.cover_image.path
            cover_name = os.path.basename(cover_path)
            
            # Define new path in open_books directory
            new_path = os.path.join(open_books_dir, cover_name)
            
            if dry_run:
                self.stdout.write(f'Would move: {cover_path} -> {new_path}')
                self.stdout.write(f'Would clear cover_image for book: {book.title}')
            else:
                try:
                    # Move the file
                    shutil.move(cover_path, new_path)
                    moved_count += 1
                    self.stdout.write(f'Moved: {cover_name}')
                    
                    # Clear the cover_image field
                    book.cover_image = None
                    book.save()
                    cleared_count += 1
                    self.stdout.write(f'Cleared cover_image for: {book.title}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {book.title}: {e}')
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run complete. Would move {moved_count} files and clear {cleared_count} book records.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully moved {moved_count} files and cleared {cleared_count} book records.')
            )
            
        # Create a default cover image placeholder
        default_cover_path = os.path.join(media_root, 'book_covers', 'default.jpg')
        if not os.path.exists(default_cover_path) and not dry_run:
            # Create a simple placeholder image
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create a 300x400 placeholder image
                img = Image.new('RGB', (300, 400), color='#f0f0f0')
                draw = ImageDraw.Draw(img)
                
                # Add text
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                text = "No Cover\nAvailable"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (300 - text_width) // 2
                y = (400 - text_height) // 2
                
                draw.text((x, y), text, fill='#666666', font=font)
                img.save(default_cover_path, 'JPEG', quality=85)
                
                self.stdout.write(f'Created default cover image: {default_cover_path}')
                
            except ImportError:
                self.stdout.write(
                    self.style.WARNING('PIL not available, skipping default cover creation')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating default cover: {e}')
                ) 