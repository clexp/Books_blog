from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Home page - list of books
    path('', views.BookListView.as_view(), name='home'),
    
    # Book detail pages
    path('book/<slug:slug>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Author pages
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    
    # Review pages
    path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    # Genre filtering
    path('genre/<str:genre>/', views.GenreBookListView.as_view(), name='genre-books'),
    
    # Search functionality
    path('search/', views.SearchView.as_view(), name='search'),
] 