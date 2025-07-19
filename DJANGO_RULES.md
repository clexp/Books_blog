# Django Development Rules

## Core Philosophy: Work WITH Django, Not Against It

Django is a powerful framework with established patterns. Always follow Django's conventions rather than fighting the framework.

## 1. Django Workflow (Always Follow This Order)

### 1.1 Define URLs First

- Map URLs to views in `urls.py`
- Use descriptive URL patterns
- Include proper namespacing

### 1.2 Write Views Second

- Handle business logic and data retrieval
- Use Django's ORM for database queries
- Pass clean data to templates
- Use class-based views when appropriate

### 1.3 Create Templates Last

- Keep templates simple and focused on presentation
- Let Django handle the rendering
- Avoid complex template logic

## 2. Template Best Practices

### 2.1 Keep Templates Simple

```django
<!-- GOOD: Simple, clean template syntax -->
{% for book in books %}
<div class="book-card">
    <h3>{{ book.title }}</h3>
    <p>by {{ book.author.name }}</p>
    <p>{{ book.reviews.count }} reviews</p>
</div>
{% empty %}
<p>No books available.</p>
{% endfor %}
```

### 2.2 Avoid Complex Template Logic

```django
<!-- BAD: Complex conditional logic in templates -->
{{ book.reviews.count }} review{% if book.reviews.count != 1 %}s{% endif %} {% if book.reviews.exists %}

<!-- GOOD: Simple, readable template -->
<p>{{ book.reviews.count }} reviews</p>
```

### 2.3 Template Structure Rules

- Keep conditional statements on single lines when possible
- Use proper indentation
- Avoid deeply nested conditionals
- Let views handle data processing, not templates

## 3. View Best Practices

### 3.1 Use Django's ORM Properly

```python
# GOOD: Optimized queryset with select_related
def get_queryset(self):
    return Book.objects.select_related('author').prefetch_related('reviews').all()

# GOOD: Add context data in get_context_data
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['total_books'] = Book.objects.count()
    return context
```

### 3.2 Keep Views Focused

- Views should handle data retrieval and processing
- Pass clean, processed data to templates
- Avoid business logic in templates

## 4. Common Mistakes to Avoid

### 4.1 Template Syntax Errors

- **NEVER** split conditional statements across multiple lines incorrectly
- **NEVER** mix `{% if %}` and `{% endif %}` tags improperly
- **ALWAYS** ensure proper tag nesting

### 4.2 Fighting Django's Patterns

- **NEVER** try to override Django's template engine behavior
- **NEVER** create complex template logic that could be handled in views
- **ALWAYS** use Django's built-in template tags and filters

### 4.3 Debugging Template Issues

When encountering template syntax errors:

1. Check for malformed conditional statements
2. Ensure proper tag nesting
3. Simplify complex template logic
4. Move logic to views if needed

## 5. Development Workflow

### 5.1 Start Simple

1. Create basic URL patterns
2. Write simple views that return basic data
3. Create minimal templates
4. Iterate and enhance

### 5.2 Testing

- Always test URLs → Views → Templates in order
- Use Django's debug mode to identify issues
- Check server logs for template syntax errors

### 5.3 When Things Go Wrong

1. **STOP** trying to fix complex template logic
2. **SIMPLIFY** the template
3. **MOVE** logic to views if needed
4. **TEST** with simple, clean templates first

## 6. Key Principles

1. **Django Knows Best**: Trust Django's conventions
2. **Keep It Simple**: Complex logic belongs in views, not templates
3. **Test Incrementally**: Build and test each component separately
4. **Read the Error Messages**: Django provides clear error information
5. **Work WITH the Framework**: Don't fight Django's patterns

## 7. Template Debugging Checklist

When encountering template errors:

- [ ] Check for malformed `{% if %}` / `{% endif %}` pairs
- [ ] Ensure proper nesting of template tags
- [ ] Simplify complex conditional logic
- [ ] Move data processing to views
- [ ] Test with minimal template first
- [ ] Check Django debug output for specific line numbers

## 8. Remember

**The goal is to let Django do what it does best:**

- Handle URL routing
- Process data in views
- Render clean templates

**Don't try to make Django something it's not.**
