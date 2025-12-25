from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def contrast_color(hex_color):
    """
    Calculate contrasting text color (black or white) based on background color brightness.
    Uses relative luminance formula (WCAG standard).
    """
    if not hex_color or not isinstance(hex_color, str):
        return '#000000'
    
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Validate hex color
    if len(hex_color) != 6:
        return '#000000'
    
    try:
        # Convert hex to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        # Calculate relative luminance
        def gamma_correct(channel):
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return ((channel + 0.055) / 1.055) ** 2.4
        
        r = gamma_correct(r)
        g = gamma_correct(g)
        b = gamma_correct(b)
        
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        # Return white for dark backgrounds, black for light backgrounds
        return '#FFFFFF' if luminance < 0.5 else '#000000'
    except (ValueError, TypeError):
        return '#000000'
