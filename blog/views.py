from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Book, Author, Review


class BookListView(ListView):
    """Home page view displaying all books with pagination."""
    model = Book
    template_name = 'blog/book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        """Optimize queryset with select_related to avoid N+1 queries."""
        return Book.objects.select_related('author').prefetch_related('reviews').all()
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['genres'] = Book.GENRE_CHOICES
        context['total_books'] = Book.objects.count()
        context['total_reviews'] = Review.objects.filter(is_public=True).count()
        return context


class BookDetailView(DetailView):
    """Detailed view for a single book with reviews."""
    model = Book
    template_name = 'blog/book_detail.html'
    context_object_name = 'book'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Optimize queryset with related data."""
        return Book.objects.select_related('author').prefetch_related('reviews__reviewer').all()
    
    def get_context_data(self, **kwargs):
        """Add reviews and statistics to context."""
        context = super().get_context_data(**kwargs)
        book = context['book']
        
        # Get public reviews for this book
        reviews = book.reviews.filter(is_public=True).select_related('reviewer')
        context['reviews'] = reviews
        
        # Calculate statistics
        context['review_count'] = reviews.count()
        context['average_rating'] = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        return context


class AuthorListView(ListView):
    """List view for all authors."""
    model = Author
    template_name = 'blog/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20
    
    def get_queryset(self):
        """Optimize queryset with book count."""
        return Author.objects.annotate(book_count=Count('books')).all()


class AuthorDetailView(DetailView):
    """Detailed view for a single author with their books."""
    model = Author
    template_name = 'blog/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        """Add author's books to context."""
        context = super().get_context_data(**kwargs)
        author = context['author']
        context['books'] = author.books.all()
        return context


class ReviewDetailView(DetailView):
    """Detailed view for a single review."""
    model = Review
    template_name = 'blog/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        """Only show public reviews."""
        return Review.objects.filter(is_public=True).select_related('book', 'reviewer')


class GenreBookListView(ListView):
    """List books filtered by genre."""
    model = Book
    template_name = 'blog/genre_books.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter books by genre."""
        genre = self.kwargs.get('genre')
        return Book.objects.filter(genre=genre).select_related('author').prefetch_related('reviews')
    
    def get_context_data(self, **kwargs):
        """Add genre information to context."""
        context = super().get_context_data(**kwargs)
        context['genre'] = self.kwargs.get('genre')
        context['genre_display'] = dict(Book.GENRE_CHOICES).get(context['genre'], context['genre'])
        return context


class SearchView(ListView):
    """Search functionality for books and authors."""
    model = Book
    template_name = 'blog/search_results.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        """Search in books and authors."""
        query = self.request.GET.get('q', '')
        if not query:
            return Book.objects.none()
        
        return Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query)
        ).select_related('author').prefetch_related('reviews').distinct()
    
    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
