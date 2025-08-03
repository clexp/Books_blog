from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
import os


class BackdropImage(models.Model):
    """
    Model for managing backdrop/background images with processing options.
    """
    PROCESSING_CHOICES = [
        ('original', 'Original Color'),
        ('desaturated', 'Low Saturation'),
        ('sepia', 'Sepia Tone'),
        ('greyscale', 'Greyscale'),
        ('whitened', 'Whitened Backdrop'),
    ]
    
    name = models.CharField(max_length=200, help_text="Descriptive name for the backdrop")
    original_image = models.ImageField(
        upload_to='site_images/backdrops/',
        help_text="Original high-resolution backdrop image"
    )
    processed_image = models.ImageField(
        upload_to='site_images/backdrops/processed/',
        blank=True,
        null=True,
        help_text="Processed version for web use"
    )
    processing_style = models.CharField(
        max_length=20,
        choices=PROCESSING_CHOICES,
        default='desaturated',
        help_text="How the image should be processed"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this backdrop is available for use"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Backdrop Image"
        verbose_name_plural = "Backdrop Images"

    def __str__(self):
        return self.name

    def process_image(self):
        """Process the original image according to the selected style."""
        if not self.original_image:
            return
            
        # Open the original image
        img = Image.open(self.original_image.path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Apply processing based on style
        if self.processing_style == 'desaturated':
            # Reduce saturation by 60%
            img = self._desaturate_image(img, 0.4)
        elif self.processing_style == 'sepia':
            img = self._apply_sepia(img)
        elif self.processing_style == 'greyscale':
            img = img.convert('L').convert('RGB')
        
        # Resize for web optimization (max 1920px width)
        img = self._resize_image(img, max_width=1920)
        
        # Save processed image
        processed_path = self.original_image.path.replace(
            'site_images/backdrops/',
            'site_images/backdrops/processed/'
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        
        # Save with quality optimization
        img.save(processed_path, 'JPEG', quality=85, optimize=True)
        
        # Update the processed_image field
        self.processed_image.name = processed_path.replace(
            str(self.original_image.storage.location) + '/', ''
        )
        self.save()

    def _desaturate_image(self, img, factor=0.4):
        """Reduce saturation of an image."""
        # Convert to HSV, reduce saturation, convert back
        hsv = img.convert('HSV')
        h, s, v = hsv.split()
        s = s.point(lambda x: int(x * factor))
        hsv = Image.merge('HSV', (h, s, v))
        return hsv.convert('RGB')

    def _apply_sepia(self, img):
        """Apply sepia tone to an image."""
        # Sepia matrix
        sepia_matrix = [
            0.393, 0.769, 0.189,
            0.349, 0.686, 0.168,
            0.272, 0.534, 0.131
        ]
        return img.convert('RGB', matrix=sepia_matrix)

    def _resize_image(self, img, max_width=1920):
        """Resize image maintaining aspect ratio."""
        if img.width <= max_width:
            return img
        
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        return img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    def save(self, *args, **kwargs):
        """Override save to process image if original has changed."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Process image if it's new or the original has changed
        if is_new or hasattr(self, '_original_image_changed'):
            self.process_image()


class Author(models.Model):
    """
    Model representing a book author.
    Demonstrates proper model documentation and field choices.
    """
    name = models.CharField(max_length=200, help_text="Author's full name")
    bio = models.TextField(blank=True, help_text="Brief biography of the author")
    website = models.URLField(blank=True, help_text="Author's official website")
    birth_date = models.DateField(null=True, blank=True, help_text="Author's birth date")
    profile_image = models.ImageField(
        upload_to='author_photos/',
        blank=True,
        null=True,
        help_text="Author's profile photo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])


class Book(models.Model):
    """
    Model representing a book.
    Demonstrates foreign key relationships and field validation.
    """
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('mystery', 'Mystery & Thriller'),
        ('romance', 'Romance'),
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography & Memoir'),
        ('history', 'History'),
        ('self-help', 'Self-Help'),
        ('business', 'Business'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=300, help_text="Book title")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fiction')
    isbn = models.CharField(max_length=13, blank=True, help_text="ISBN-13 number")
    publication_date = models.DateField(null=True, blank=True, help_text="Date of publication")
    page_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of pages")
    description = models.TextField(blank=True, help_text="Book description/summary")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date', 'title']
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL to access a particular book instance."""
        return reverse('book-detail', args=[str(self.slug)])

    @property
    def average_rating(self):
        """Calculate average rating from all reviews."""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def create_backdrop_from_cover(self):
        """Create a backdrop image from the book cover."""
        if not self.cover_image:
            return None
            
        # Create backdrop image record
        backdrop_name = f"{self.title} Backdrop"
        backdrop = BackdropImage.objects.create(
            name=backdrop_name,
            original_image=self.cover_image,
            processing_style='whitened'
        )
        return backdrop


class Review(models.Model):
    """
    Model representing a book review.
    Demonstrates user relationships, validation, and rich text content.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, help_text="Review title")
    content = models.TextField(help_text="Review content")
    book_images = models.ImageField(
        upload_to='open_book_images/',
        blank=True,
        null=True,
        help_text="Images of the open book for the review"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Review status"
    )
    is_public = models.BooleanField(default=True, help_text="Whether this review is publicly visible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        unique_together = ['book', 'reviewer']  # One review per book per user

    def __str__(self):
        return f"Review of {self.book.title} by {self.reviewer.username}"

    def get_absolute_url(self):
        """Returns the URL to access a particular review instance."""
        return reverse('review-detail', args=[str(self.id)])

    @property
    def rating_stars(self):
        """Return rating as stars (★) for display."""
        return '★' * self.rating + '☆' * (5 - self.rating)
