"""
Freelance Timer Pro - Theme System
Modular theme/stylesheet system for easy customization
"""

# Available themes
from . import professional_gray
from . import dark_mode

# Theme registry for UI dropdown
AVAILABLE_THEMES = {
    'Professional Gray': professional_gray,
    'Dark Mode': dark_mode
}

__all__ = ['professional_gray', 'dark_mode', 'AVAILABLE_THEMES']
