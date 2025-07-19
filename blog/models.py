from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


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


class Review(models.Model):
    """
    Model representing a book review.
    Demonstrates user relationships, validation, and rich text content.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, help_text="Review title")
    content = models.TextField(help_text="Review content")
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
