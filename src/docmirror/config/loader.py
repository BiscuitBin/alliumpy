"""Load `docmirror.toml` with the precedence CLI flags > `DOCMIRROR_*` > TOML > defaults.

Environment variables name a key by section and field joined with a double underscore:
`DOCMIRROR_SCOPE__MAX_PAGES=100`, `DOCMIRROR_FETCH__ROBOTS=ignore`. Lists are
comma-separated. CLI overrides arrive as dotted keys from the subcommands.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from docmirror.config.models import Config

ENV_PREFIX = "DOCMIRROR_"
CONFIG_FILENAME = "docmirror.toml"


class ConfigError(ValueError):
    """A configuration problem the user must fix; the CLI maps it to exit 2."""


def _set_dotted(target: dict[str, Any], dotted: str, value: Any) -> None:  # noqa: ANN401 - TOML values
    parts = dotted.split(".")
    node = target
    for part in parts[:-1]:
        child = node.setdefault(part, {})
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def _coerce_env(value: str, field_type: object) -> Any:  # noqa: ANN401 - TOML values
    text = value.strip()
    if field_type is bool or text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if field_type is list or ("," in text and not text.startswith("re:")):
        return [item.strip() for item in text.split(",") if item.strip()]
    try:
        return json.loads(text) if text and text[0] in "0123456789-[{" else text
    except json.JSONDecodeError:
        return text


def env_overrides(environ: Mapping[str, str]) -> dict[str, Any]:
    """The nested overrides `DOCMIRROR_*` variables express.

    >>> env_overrides({"DOCMIRROR_SCOPE__MAX_PAGES": "7", "PATH": "/bin"})
    {'scope': {'max_pages': 7}}
    """
    result: dict[str, Any] = {}
    for name, raw in environ.items():
        if not name.startswith(ENV_PREFIX):
            continue
        key = name[len(ENV_PREFIX) :].lower()
        if "__" not in key:
            continue
        section, _, field = key.partition("__")
        field_type: object = str
        model_field = Config.model_fields.get(section)
        if model_field is not None and hasattr(model_field.annotation, "model_fields"):
            inner = model_field.annotation.model_fields.get(field)  # type: ignore[union-attr]
            if inner is not None:
                field_type = inner.annotation
        _set_dotted(result, f"{section}.{field}", _coerce_env(raw, field_type))
    return result


def _deep_merge(base: dict[str, Any], layer: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in layer.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _format_errors(error: ValidationError) -> str:
    lines = []
    for item in error.errors():
        path = ".".join(str(part) for part in item["loc"])
        if item["type"] == "extra_forbidden":
            lines.append(f"unknown key: {path}")
        else:
            lines.append(f"{path}: {item['msg']}")
    return "; ".join(lines)


def validate_config(data: Mapping[str, Any]) -> Config:
    """A `Config` from nested data, or a `ConfigError` naming every bad key path."""
    try:
        return Config.model_validate(dict(data))
    except ValidationError as error:
        raise ConfigError(_format_errors(error)) from error


def load_config(
    path: Path,
    *,
    environ: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Config:
    """Read the TOML at `path` and apply the environment and CLI layers over it."""
    try:
        with path.open("rb") as stream:
            data: dict[str, Any] = tomllib.load(stream)
    except FileNotFoundError as error:
        message = f"configuration file not found: {path}"
        raise ConfigError(message) from error
    except tomllib.TOMLDecodeError as error:
        message = f"{path}: {error}"
        raise ConfigError(message) from error
    if environ is not None:
        data = _deep_merge(data, env_overrides(environ))
    if overrides:
        layered: dict[str, Any] = {}
        for dotted, value in overrides.items():
            if value is not None:
                _set_dotted(layered, dotted, value)
        data = _deep_merge(data, layered)
    return validate_config(data)


def _toml_value(value: Any) -> str:  # noqa: ANN401 - TOML values
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    message = f"cannot render {type(value).__name__} as a TOML value"
    raise TypeError(message)


def _render_table(name: str, table: Mapping[str, Any], out: list[str]) -> None:
    scalars = {k: v for k, v in table.items() if not isinstance(v, dict)}
    subtables = {k: v for k, v in table.items() if isinstance(v, dict)}
    if scalars or not subtables:
        out.append(f"[{name}]")
        for key, value in scalars.items():
            key_text = key if key.replace("_", "").replace("-", "").isalnum() else json.dumps(key)
            out.append(f"{key_text} = {_toml_value(value)}")
        out.append("")
    for key, value in subtables.items():
        sub = key if key.replace("_", "").replace("-", "").isalnum() else json.dumps(key)
        _render_table(f"{name}.{sub}", value, out)


def render_toml(config: Config) -> str:
    """The configuration as a TOML document, every section and default written out."""
    out: list[str] = []
    for section, table in config.model_dump(mode="json").items():
        _render_table(section, table, out)
    return "\n".join(out).rstrip() + "\n"
