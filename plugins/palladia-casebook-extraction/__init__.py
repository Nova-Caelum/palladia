"""Palladia casebook extraction plugin registration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from .handlers import extract_case, locate_case
from . import schemas


def _bounded_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _json_handler(function: Callable[..., dict[str, Any]], settings: dict[str, Any]):
    def handler(args: dict[str, Any], **_kwargs: Any) -> str:
        try:
            result = function(
                vault_root=settings["vault_path"],
                catalog_query=str(args.get("catalog", "")),
                case_name=str(args.get("case_name", "")),
                max_index_pages=settings["max_index_pages"],
                search_radius=settings["search_radius"],
                max_inspected_pages=settings["max_inspected_pages"],
            )
        except Exception as exc:  # fail closed without leaking path/content in messages
            result = {
                "status": "refused",
                "reason": "plugin_handler_failed",
                "error_type": type(exc).__name__,
            }
        return json.dumps(result, ensure_ascii=False, sort_keys=True)

    return handler


def register(ctx) -> None:
    """Register two model-callable tools in a dedicated opt-in toolset."""
    default_vault = os.environ.get(
        "PALLADRIVE_PATH", "/home/daniel/obsidian-vaults/palladrive"
    )
    settings = {
        "vault_path": str(ctx.get_config("vault_path", default=default_vault)),
        "max_index_pages": _bounded_int(
            ctx.get_config("max_index_pages", default=32),
            default=32,
            minimum=1,
            maximum=64,
        ),
        "search_radius": _bounded_int(
            ctx.get_config("search_radius", default=18),
            default=18,
            minimum=0,
            maximum=32,
        ),
        "max_inspected_pages": _bounded_int(
            ctx.get_config("max_inspected_pages", default=96),
            default=96,
            minimum=16,
            maximum=128,
        ),
    }
    available = lambda: Path(settings["vault_path"]).expanduser().is_dir()
    ctx.register_tool(
        name="casebook_locate_case",
        toolset="palladia_casebook",
        schema=schemas.CASEBOOK_LOCATE_CASE,
        handler=_json_handler(locate_case, settings),
        check_fn=available,
        emoji="📐",
    )
    ctx.register_tool(
        name="casebook_extract_case",
        toolset="palladia_casebook",
        schema=schemas.CASEBOOK_EXTRACT_CASE,
        handler=_json_handler(extract_case, settings),
        check_fn=available,
        emoji="📕",
    )


__all__ = ["extract_case", "locate_case", "register", "schemas"]
