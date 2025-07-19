from django import template

register = template.Library()

@register.filter
def star_rating(rating):
    """
    Convert a numeric rating to star display.
    Returns a string with filled (★) and empty (☆) stars.
    """
    if not rating:
        return ""
    
    # Convert to integer for full stars
    full_stars = int(rating)
    empty_stars = 5 - full_stars
    
    # Create star string
    stars = "★" * full_stars + "☆" * empty_stars
    return stars

@register.filter  
def display_rating(rating):
    """
    Display rating with stars and numeric value.
    """
    if not rating:
        return "No rating"
    
    stars = star_rating(rating)
    return f"{stars} ({rating:.1f})" 