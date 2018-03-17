"""
This package requires that pip be available for import or many
operations will fail. So a test import of pip is tried immediately.

The pip library also has a bug (9.0.2) that requires it be imported
before the requests library is imported or it will fail. This initial
import serves to maintain order as well until that bug is fixed.
"""

try:
    import pip  # noqa
except ImportError:
    print('Pipper requires that the pip package be available for import')
    raise
