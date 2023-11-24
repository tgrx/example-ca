"""
This module contains only constants.
"""

from pathlib import Path
from typing import Final

_consts_py: Final[Path] = Path(__file__).resolve()

DIR_REPO: Final[Path] = _consts_py.parent.parent.parent.resolve()
"""
The path to the code repository, the root of all sources.
"""

DIR_DJANGO_PROJECT: Final[Path] = (DIR_REPO / "project").resolve()
"""
The path to Django project, where settings.py is situated.
"""


DIR_LOCAL: Final[Path] = (DIR_REPO / ".local").resolve()
"""
The path to local dir, where all caches, volumes and garbage is kept.
"""

_err = f"project-local dir is not found: {DIR_LOCAL.as_posix()}"
assert DIR_LOCAL.is_dir(), _err


DIR_DJANGO_STATIC_ROOT: Final[Path] = (DIR_LOCAL / "static").resolve()
"""
The path to where Django collects its static files (not static-sources).
"""

DIR_DJANGO_STATIC_ROOT.mkdir(exist_ok=True)


__all__ = (
    "DIR_DJANGO_PROJECT",
    "DIR_DJANGO_STATIC_ROOT",
    "DIR_LOCAL",
    "DIR_REPO",
)
