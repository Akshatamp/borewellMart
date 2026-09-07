from django import template

register = template.Library()


@register.filter
def get_initials(company_name):
    """
    Extract initials from company name for logo generation.
    Examples:
    - 'Kalaburagi Irrigation' -> 'KI'
    - 'ABC Borewell Services' -> 'AB'
    - 'X' -> 'X'
    """
    if not company_name:
        return 'VN'
    
    # Remove common words and get meaningful words
    words = company_name.split()
    
    # Filter out common business words
    common_words = {'services', 'service', 'pvt', 'ltd', 'limited', 'private', 'corporation', 
                    'company', 'enterprises', 'traders', 'works', 'industries', 'solutions',
                    'agencies', 'associates', 'partners', 'group', 'international', 'global'}
    
    meaningful_words = [word for word in words if word.lower() not in common_words]
    
    # If no meaningful words after filtering, use original words
    if not meaningful_words:
        meaningful_words = words
    
    # Get initials (first letter of each word, max 2)
    initials = ''
    for word in meaningful_words[:2]:
        if word:
            initials += word[0].upper()
    
    # If still no initials, use default
    if not initials:
        initials = 'VN'
    
    return initials


@register.filter
def get_logo_color(company_name):
    """
    Generate a consistent color based on company name hash.
    Returns a CSS color string.
    """
    if not company_name:
        return '#06B6D4'
    
    # Simple hash function
    hash_value = sum(ord(c) for c in company_name)
    
    # Generate colors from a predefined palette
    colors = [
        '#06B6D4',  # Cyan
        '#8B5CF6',  # Purple
        '#EC4899',  # Pink
        '#F59E0B',  # Amber
        '#10B981',  # Emerald
        '#3B82F6',  # Blue
        '#EF4444',  # Red
        '#6366F1',  # Indigo
        '#14B8A6',  # Teal
        '#F97316',  # Orange
    ]
    
    return colors[hash_value % len(colors)]
