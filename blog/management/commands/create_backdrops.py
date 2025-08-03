from django.core.management.base import BaseCommand
from blog.models import Book, BackdropImage


class Command(BaseCommand):
    help = 'Create backdrop images from book covers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        books_with_covers = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='')
        
        self.stdout.write(f'Found {books_with_covers.count()} books with cover images')
        
        created_count = 0
        
        for book in books_with_covers:
            # Check if backdrop already exists
            existing_backdrop = BackdropImage.objects.filter(name__icontains=book.title).first()
            
            if existing_backdrop:
                self.stdout.write(
                    self.style.WARNING(f'Backdrop already exists for: {book.title}')
                )
                continue
            
            if dry_run:
                self.stdout.write(
                    f'Would create backdrop for: {book.title}'
                )
            else:
                try:
                    backdrop = book.create_backdrop_from_cover()
                    if backdrop:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created backdrop for: {book.title}'
                            )
                        )
                        created_count += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to create backdrop for: {book.title}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating backdrop for {book.title}: {e}')
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} backdrop images')
            )
        else:
            self.stdout.write(f'\nWould create {books_with_covers.count()} backdrop images') 