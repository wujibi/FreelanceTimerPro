"""
Freelance Timer Pro - Theme System
Modular theme/stylesheet system for easy customization
"""

# Available themes
from . import professional_gray
from . import dark_mode
from . import burnt_orange_pro
from . import burnt_orange_pro_v2
from . import burnt_orange_pro_v3

# Theme registry for UI dropdown
AVAILABLE_THEMES = {
    'Burnt Orange Pro': burnt_orange_pro,          # Original version
    'Burnt Orange Pro V2': burnt_orange_pro_v2,    # Two-tone orange (light peach groups)
    'Burnt Orange Pro V3': burnt_orange_pro_v3,    # Orange + Teal (teal groups)
    'Professional Gray': professional_gray,         # Original neutral option
    'Dark Mode': dark_mode                          # For night owls
}

# Default theme for new installations
DEFAULT_THEME = 'Burnt Orange Pro'

__all__ = ['burnt_orange_pro', 'burnt_orange_pro_v2', 'burnt_orange_pro_v3', 'professional_gray', 'dark_mode', 'AVAILABLE_THEMES', 'DEFAULT_THEME']
