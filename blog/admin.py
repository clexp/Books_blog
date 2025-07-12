from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Book, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin interface for Author model with professional features."""
    list_display = ['name', 'birth_date', 'website', 'book_count', 'created_at']
    list_filter = ['birth_date', 'created_at']
    search_fields = ['name', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'bio', 'birth_date')
        }),
        ('Contact Information', {
            'fields': ('website',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def book_count(self, obj):
        """Display the number of books by this author."""
        return obj.books.count()
    book_count.short_description = 'Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model with advanced features."""
    list_display = ['title', 'author', 'genre', 'publication_date', 'average_rating_display', 'review_count', 'cover_preview']
    list_filter = ['genre', 'publication_date', 'author', 'created_at']
    search_fields = ['title', 'author__name', 'description', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'genre', 'slug')
        }),
        ('Publication Details', {
            'fields': ('isbn', 'publication_date', 'page_count')
        }),
        ('Content', {
            'fields': ('description', 'cover_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def average_rating_display(self, obj):
        """Display average rating with stars."""
        if obj.average_rating > 0:
            stars = '★' * int(obj.average_rating) + '☆' * (5 - int(obj.average_rating))
            rating_text = f"{obj.average_rating:.1f}"
            return format_html('<span style="color: gold;">{}</span> ({})', stars, rating_text)
        return 'No reviews'
    average_rating_display.short_description = 'Average Rating'

    def review_count(self, obj):
        """Display the number of reviews for this book."""
        return obj.reviews.count()
    review_count.short_description = 'Reviews'

    def cover_preview(self, obj):
        """Display a small preview of the book cover."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.cover_image.url
            )
        return 'No cover'
    cover_preview.short_description = 'Cover'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model with moderation features."""
    list_display = ['book', 'reviewer', 'rating_stars', 'title', 'is_public', 'created_at']
    list_filter = ['rating', 'is_public', 'created_at', 'book__genre']
    search_fields = ['title', 'content', 'book__title', 'reviewer__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_public']
    actions = ['make_public', 'make_private']
    fieldsets = (
        ('Review Information', {
            'fields': ('book', 'reviewer', 'title', 'content')
        }),
        ('Rating & Visibility', {
            'fields': ('rating', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_stars(self, obj):
        """Display rating as stars."""
        return format_html(
            '<span style="color: gold;">{}</span>',
            obj.rating_stars
        )
    rating_stars.short_description = 'Rating'

    def make_public(self, request, queryset):
        """Action to make selected reviews public."""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} reviews were successfully made public.')
    make_public.short_description = "Make selected reviews public"

    def make_private(self, request, queryset):
        """Action to make selected reviews private."""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} reviews were successfully made private.')
    make_private.short_description = "Make selected reviews private"
