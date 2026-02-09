"""
Freelance Timer Pro - Theme System
Modular theme/stylesheet system for easy customization
"""

# Available themes
from . import professional_gray
from . import dark_mode
from . import deep_navy_pro
from . import light_navy_pro
from . import balanced_navy
from . import sage_professional
from . import warm_professional
from . import burnt_orange

# Theme registry for UI dropdown
AVAILABLE_THEMES = {
    'Professional Gray': professional_gray,
    'Dark Mode': dark_mode,
    'Deep Navy Pro': deep_navy_pro,
    'Light Navy Pro': light_navy_pro,
    'Balanced Navy': balanced_navy,
    'Sage Professional': sage_professional,
    'Warm Professional': warm_professional,
    'Burnt Orange': burnt_orange
}

__all__ = ['professional_gray', 'dark_mode', 'deep_navy_pro', 'light_navy_pro', 'balanced_navy', 'sage_professional', 'warm_professional', 'burnt_orange', 'AVAILABLE_THEMES']
