"""Configuration: pydantic models, the TOML loader, precedence and built-in profiles."""

from __future__ import annotations

from docmirror.config.loader import ConfigError, load_config, render_toml
from docmirror.config.models import Config, Profile
from docmirror.config.profiles import BUILTIN_PROFILES, detect_profile

__all__ = [
    "BUILTIN_PROFILES",
    "Config",
    "ConfigError",
    "Profile",
    "detect_profile",
    "load_config",
    "render_toml",
]
