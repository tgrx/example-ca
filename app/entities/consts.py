"""
This module contains only constants.
"""

from pathlib import Path
from typing import Final

_consts_py: Final[Path] = Path(__file__).resolve()

"""
The path to the code repository, the root of all sources.
"""
DIR_REPO: Final[Path] = _consts_py.parent.parent.parent.resolve()

"""
The path to Django project, where settings.py is situated.
"""
DIR_DJANGO_PROJECT: Final[Path] = (DIR_REPO / "project").resolve()

"""
The path to local dir, where all caches, volumes and garbage is kept.
"""
DIR_LOCAL: Final[Path] = (DIR_REPO / ".local").resolve()
assert (
    DIR_LOCAL.is_dir()
), f"project-local dir is not found: {DIR_LOCAL.as_posix()}"

"""
The path to where Django collects its static files (not static-sources).
"""
DIR_DJANGO_STATIC_ROOT: Final[Path] = (DIR_LOCAL / "static").resolve()
DIR_DJANGO_STATIC_ROOT.mkdir(exist_ok=True)

__all__ = (
    "DIR_DJANGO_PROJECT",
    "DIR_DJANGO_STATIC_ROOT",
    "DIR_LOCAL",
    "DIR_REPO",
)
