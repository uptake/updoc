"""
Storage management classes.
"""

from ._base import Storage
from ._local import LocalStorage
from ._s3 import S3Storage

__all__ = [
    "Storage",
    "LocalStorage",
    "S3Storage"
]
