"""
Backward compatibility wrapper for the refactored Level class.

This file maintains the original import structure while the actual
implementation has been moved to the level/ module for better organization.
"""

# Import the refactored Level class
from .level import Level

# Re-export for backward compatibility
__all__ = ['Level']