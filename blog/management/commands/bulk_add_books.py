from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Book, Author, Review
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Bulk add books and authors with interactive prompts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--images-dir',
            type=str,
            default='media/book_covers/',
            help='Directory containing book cover images'
        )
        parser.add_argument(
            '--auto-author',
            action='store_true',
            help='Automatically create authors if they don\'t exist'
        )

    def handle(self, *args, **options):
        images_dir = options['images_dir']
        auto_author = options['auto_author']
        
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
        
        self.stdout.write(f'Found {len(image_files)} image files')
        
        # Get existing books to avoid duplicates
        existing_books = set(Book.objects.values_list('title', flat=True))
        
        # Get existing authors
        existing_authors = {author.name.lower(): author for author in Author.objects.all()}
        
        added_books = 0
        added_authors = 0
        
        for filename in image_files:
            # Skip if already processed
            if any(filename.lower() in book.lower() for book in existing_books):
                continue
                
            # Extract potential title from filename
            potential_title = self._extract_title_from_filename(filename)
            
            self.stdout.write(f'\n--- Processing: {filename} ---')
            self.stdout.write(f'Potential title: {potential_title}')
            
            # Get book title
            title = input('Enter book title (or press Enter to skip): ').strip()
            if not title:
                self.stdout.write('Skipped.')
                continue
            
            # Check if book already exists
            if title in existing_books:
                self.stdout.write(f'Book "{title}" already exists. Skipped.')
                continue
            
            # Get author name
            author_name = input('Enter author name: ').strip()
            if not author_name:
                self.stdout.write('No author provided. Skipped.')
                continue
            
            # Get or create author
            author = self._get_or_create_author(author_name, existing_authors, auto_author)
            if not author:
                continue
            
            # Get genre
            genre = self._get_genre()
            
            # Get additional details
            isbn = input('Enter ISBN (optional): ').strip() or ''
            description = input('Enter description (optional): ').strip() or ''
            
            try:
                # Create book
                book = Book.objects.create(
                    title=title,
                    author=author,
                    genre=genre,
                    isbn=isbn,
                    description=description
                )
                
                # Link the image
                image_path = os.path.join(images_dir, filename)
                with open(image_path, 'rb') as img_file:
                    book.cover_image.save(filename, img_file, save=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Added book: "{title}" by {author.name}')
                )
                added_books += 1
                existing_books.add(title)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error adding book "{title}": {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSummary: Added {added_books} books and {added_authors} authors')
        )

    def _extract_title_from_filename(self, filename):
        """Extract potential title from filename."""
        # Remove extension
        name = Path(filename).stem
        
        # Replace underscores and dashes with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name

    def _get_or_create_author(self, author_name, existing_authors, auto_author):
        """Get or create author."""
        author_name_lower = author_name.lower()
        
        # Check if author exists
        if author_name_lower in existing_authors:
            return existing_authors[author_name_lower]
        
        # Create new author
        if auto_author:
            author = Author.objects.create(name=author_name)
            existing_authors[author_name_lower] = author
            return author
        else:
            create = input(f'Author "{author_name}" not found. Create? (y/n): ').strip().lower()
            if create == 'y':
                author = Author.objects.create(name=author_name)
                existing_authors[author_name_lower] = author
                return author
            else:
                return None

    def _get_genre(self):
        """Get genre from user."""
        genres = dict(Book.GENRE_CHOICES)
        
        self.stdout.write('Available genres:')
        for i, (key, value) in enumerate(genres.items(), 1):
            self.stdout.write(f'{i}. {value}')
        
        while True:
            choice = input('Enter genre number or name: ').strip()
            
            # Try as number
            try:
                num = int(choice)
                if 1 <= num <= len(genres):
                    return list(genres.keys())[num - 1]
            except ValueError:
                pass
            
            # Try as name
            for key, value in genres.items():
                if choice.lower() in value.lower():
                    return key
            
            self.stdout.write('Invalid genre. Please try again.') 