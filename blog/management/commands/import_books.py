import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Author, Book, Review
from django.utils.text import slugify
from datetime import datetime


class Command(BaseCommand):
    help = 'Import books and reviews from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to JSON file containing books data',
            default='export_book_reviews/all_books.json'
        )
        parser.add_argument(
            '--images-dir',
            type=str,
            help='Directory containing book cover images',
            default='export_book_reviews/images'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force import even if books already exist'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        images_dir = options['images_dir']
        force = options['force']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'JSON file not found: {json_file}')
            )
            return

        # Get or create a default user for reviews
        default_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        # Get or create a default author
        default_author, created = Author.objects.get_or_create(
            name='Unknown',
            defaults={
                'bio': 'Author information not available'
            }
        )

        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                books_data = json.load(file)

            imported_count = 0
            skipped_count = 0

            for book_data in books_data:
                try:
                    # Create or get the author
                    author_name = book_data.get('author', 'Unknown')
                    if author_name == 'Unknown':
                        author = default_author
                    else:
                        author, created = Author.objects.get_or_create(
                            name=author_name,
                            defaults={'bio': f'Author of {book_data["title"]}'}
                        )

                    # Generate a unique slug
                    base_slug = slugify(book_data['title'])
                    slug = base_slug
                    counter = 1
                    while Book.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    # Create the book
                    book, created = Book.objects.get_or_create(
                        title=book_data['title'],
                        author=author,
                        defaults={
                            'description': book_data.get('description', ''),
                            'genre': 'non-fiction',  # Default genre
                            'slug': slug
                        }
                    )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created book: {book.title}')
                        )
                        imported_count += 1
                    else:
                        if force:
                            # Update existing book
                            book.description = book_data.get('description', '')
                            book.save()
                            self.stdout.write(
                                self.style.SUCCESS(f'Updated book: {book.title}')
                            )
                            imported_count += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'Book already exists: {book.title}')
                            )
                            skipped_count += 1

                    # Handle rating - provide default if null
                    rating = book_data.get('rating')
                    if rating is None:
                        rating = 5  # Default to 5 stars

                    # Create the review
                    review_date = datetime.strptime(
                        book_data.get('review_date', '2025-01-01'), 
                        '%Y-%m-%d'
                    ).date()

                    # Check if review already exists
                    review, review_created = Review.objects.get_or_create(
                        book=book,
                        reviewer=default_user,
                        defaults={
                            'title': f"Review of {book.title}",
                            'content': book_data.get('content', ''),
                            'rating': rating,
                            'is_public': True
                        }
                    )

                    if review_created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created review for: {book.title}')
                        )
                    else:
                        if force:
                            # Update existing review
                            review.content = book_data.get('content', '')
                            review.rating = rating
                            review.save()
                            self.stdout.write(
                                self.style.SUCCESS(f'Updated review for: {book.title}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'Review already exists for: {book.title}')
                            )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing {book_data.get("title", "Unknown")}: {str(e)}')
                    )
                    skipped_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed! Imported: {imported_count}, Skipped: {skipped_count}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading JSON file: {str(e)}')
            ) 