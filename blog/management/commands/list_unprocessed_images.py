from django.core.management.base import BaseCommand
from blog.models import Book
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'List all unprocessed book cover images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--images-dir',
            type=str,
            default='media/book_covers/',
            help='Directory containing book cover images'
        )

    def handle(self, *args, **options):
        images_dir = options['images_dir']
        
        if not os.path.exists(images_dir):
            self.stdout.write(
                self.style.ERROR(f'Images directory not found: {images_dir}')
            )
            return

        # Get all image files
        image_files = []
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
        
        # Get existing books
        existing_books = Book.objects.all()
        existing_titles = {book.title.lower() for book in existing_books}
        
        # Find unprocessed images
        unprocessed = []
        processed = []
        
        for filename in image_files:
            potential_title = self._extract_title_from_filename(filename)
            
            # Check if any book title contains words from this image
            is_processed = False
            for book in existing_books:
                if self._titles_match(potential_title, book.title):
                    processed.append((filename, book.title))
                    is_processed = True
                    break
            
            if not is_processed:
                unprocessed.append(filename)
        
        self.stdout.write(f'Found {len(image_files)} total images')
        self.stdout.write(f'Processed: {len(processed)}')
        self.stdout.write(f'Unprocessed: {len(unprocessed)}')
        
        if processed:
            self.stdout.write('\n--- Processed Images ---')
            for filename, book_title in processed:
                self.stdout.write(f'{filename} → {book_title}')
        
        if unprocessed:
            self.stdout.write('\n--- Unprocessed Images ---')
            for filename in unprocessed:
                potential_title = self._extract_title_from_filename(filename)
                self.stdout.write(f'{filename} (potential: {potential_title})')
        
        self.stdout.write(f'\nTo add unprocessed books, run:')
        self.stdout.write(f'python manage.py bulk_add_books')

    def _extract_title_from_filename(self, filename):
        """Extract potential title from filename."""
        # Remove extension
        name = Path(filename).stem
        
        # Replace underscores and dashes with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name

    def _titles_match(self, potential_title, book_title):
        """Check if potential title matches book title."""
        potential_words = set(potential_title.lower().split())
        book_words = set(book_title.lower().split())
        
        # Check for significant word overlap
        significant_words = {word for word in potential_words if len(word) > 3}
        book_significant = {word for word in book_words if len(word) > 3}
        
        overlap = significant_words & book_significant
        return len(overlap) >= 1  # At least one significant word matches 