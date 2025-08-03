from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Book
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Link book cover images to book records based on filename matching'

    def add_arguments(self, parser):
        parser.add_argument(
            '--images-dir',
            type=str,
            default='media/book_covers/',
            help='Directory containing book cover images'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be linked without making changes'
        )

    def handle(self, *args, **options):
        images_dir = options['images_dir']
        dry_run = options['dry_run']
        
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
        
        # Get all books
        books = Book.objects.all()
        self.stdout.write(f'Found {books.count()} books in database')
        
        linked_count = 0
        unmatched_images = []
        
        # Track which images have been used
        used_images = set()
        
        for book in books:
            # Try to find matching image
            matching_image = self._find_matching_image(book, image_files, used_images)
            
            if matching_image:
                image_path = os.path.join(images_dir, matching_image)
                used_images.add(matching_image)
                
                if dry_run:
                    self.stdout.write(
                        f'Would link: {book.title} ← {matching_image}'
                    )
                else:
                    # Update book with cover image
                    with open(image_path, 'rb') as img_file:
                        book.cover_image.save(matching_image, img_file, save=True)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Linked: {book.title} ← {matching_image}'
                        )
                    )
                    linked_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'No image found for: {book.title}')
                )
        
        # Report unmatched images
        for image in image_files:
            if not any(self._image_matches_book(image, book) for book in books):
                unmatched_images.append(image)
        
        if unmatched_images:
            self.stdout.write(
                self.style.WARNING(f'\nUnmatched images: {len(unmatched_images)}')
            )
            for img in unmatched_images[:10]:  # Show first 10
                self.stdout.write(f'  - {img}')
            if len(unmatched_images) > 10:
                self.stdout.write(f'  ... and {len(unmatched_images) - 10} more')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully linked {linked_count} book covers')
            )
        else:
            self.stdout.write(f'\nWould link {linked_count} book covers')

    def _find_matching_image(self, book, image_files, used_images):
        """Find image that matches book title."""
        book_title_lower = book.title.lower()
        
        # Try exact match first
        for img in image_files:
            if img in used_images:
                continue
                
            img_lower = img.lower()
            img_stem = Path(img).stem.lower()
            
            # Check if image filename contains book title
            if book_title_lower in img_lower or img_stem in book_title_lower:
                return img
            
            # Check for partial matches (common words)
            book_words = book_title_lower.split()
            img_words = img_stem.split('_')
            
            # Check if any book words appear in image filename
            for word in book_words:
                if len(word) > 3 and word in img_lower:  # Only significant words
                    return img
            
            # Check for specific book title patterns
            if 'python' in book_title_lower and 'python' in img_lower:
                return img
            if 'freebsd' in book_title_lower and 'freebsd' in img_lower:
                return img
            if 'linux' in book_title_lower and 'linux' in img_lower:
                return img
            if 'machine learning' in book_title_lower and 'machine' in img_lower:
                return img
            if 'statistics' in book_title_lower and 'stats' in img_lower:
                return img
            if 'graph theory' in book_title_lower and 'graph' in img_lower:
                return img
            if 'smart notes' in book_title_lower and 'notes' in img_lower:
                return img
            if 'httpd' in book_title_lower and 'httpd' in img_lower:
                return img
        
        return None

    def _image_matches_book(self, image, book):
        """Check if image matches a book."""
        return self._find_matching_image(book, [image], set()) is not None 