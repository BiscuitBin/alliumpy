# Copyright 2026 Steven Cutting
"""Vendor upstream's allium CLI modules into crates/alliumpy-core/src/cli/ (decision 0014).

Usage: python -I vendor_cli.py <tag> <dir holding upstream's three files> <dest cli dir>

Every substitution asserts how many times it matched, so an upstream change to a line
the transform rewrites stops the script instead of producing a silent partial copy.
"""

import re
import sys
from pathlib import Path

HEADER = """\
// Vendored from juxt/allium-tools at {tag}: crates/allium/src/{name}
// (https://github.com/juxt/allium-tools/blob/{tag}/crates/allium/src/{name}).
// MIT License, Copyright (c) 2026, as upstream's LICENSE reads at that tag; the full
// text ships as crates/alliumpy/LICENSE-allium-tools. Changes from upstream are listed in
// crates/alliumpy-core/src/cli.rs; nothing else differs.
"""
SAME = "upstream's code, vendored unchanged (decision 0014)"
HASH = (
    "upstream's hash iteration, vendored unchanged; its output order is proved only as far"
    " as the parity corpus exercises it (decision 0014)"
)
PANIC = (
    "upstream panics here, vendored unchanged; cli::run returns 101 for it, as upstream's"
    " binary exits (decision 0014)"
)
PUB = "upstream's pub items, vendored unchanged inside a private module (decision 0014)"
# Per file: (lint, reason, cfg) in order; cfg is "", "test" or "not(test)".
LINTS = {
    "main.rs": [
        ("clippy::bool_to_int_with_if", SAME, ""),
        ("clippy::cognitive_complexity", SAME, ""),
        ("clippy::disallowed_types", HASH, ""),
        ("clippy::excessive_nesting", SAME, ""),
        ("clippy::iter_over_hash_type", HASH, ""),
        ("clippy::manual_let_else", SAME, ""),
        ("clippy::redundant_closure_for_method_calls", SAME, ""),
        ("clippy::str_to_string", SAME, ""),
        ("clippy::too_many_lines", SAME, ""),
        ("clippy::unnested_or_patterns", SAME, ""),
        ("clippy::unreachable", PANIC, ""),
        ("clippy::unwrap_used", PANIC, ""),
    ],
    "test_plan.rs": [
        ("unreachable_pub", PUB, ""),
        ("clippy::cognitive_complexity", SAME, ""),
        ("clippy::collapsible_if", SAME, ""),
        ("clippy::disallowed_types", HASH, ""),
        ("clippy::doc_markdown", SAME, ""),
        ("clippy::excessive_nesting", SAME, ""),
        ("clippy::if_not_else", SAME, ""),
        ("clippy::map_unwrap_or", SAME, ""),
        ("clippy::missing_const_for_fn", SAME, ""),
        ("clippy::redundant_closure_for_method_calls", SAME, ""),
        ("clippy::str_to_string", SAME, ""),
        ("clippy::too_many_arguments", SAME, ""),
        ("clippy::too_many_lines", SAME, ""),
        ("clippy::uninlined_format_args", SAME, ""),
        ("clippy::wildcard_imports", SAME, "not(test)"),
        ("clippy::assert_is_empty", SAME, "test"),
    ],
    "domain_model.rs": [
        ("unreachable_pub", PUB, ""),
        ("clippy::cognitive_complexity", SAME, ""),
        ("clippy::collapsible_if", SAME, ""),
        ("clippy::doc_markdown", SAME, ""),
        ("clippy::excessive_nesting", SAME, ""),
        ("clippy::map_unwrap_or", SAME, ""),
        ("clippy::missing_const_for_fn", SAME, ""),
        ("clippy::redundant_closure_for_method_calls", SAME, ""),
        ("clippy::str_to_string", SAME, ""),
        ("clippy::too_many_lines", SAME, ""),
        ("clippy::uninlined_format_args", SAME, ""),
        ("clippy::wildcard_imports", SAME, "not(test)"),
        ("clippy::assert_is_empty", SAME, "test"),
    ],
}
COMMANDS = ("check", "analyse", "parse", "plan", "model")
HANDLES = "stdout: &mut dyn Write, stderr: &mut dyn Write"


def replace(text: str, old: str, new: str, count: int = 1) -> str:
    """Replace exactly `count` occurrences, or stop."""
    found = text.count(old)
    if found != count:
        sys.exit(f"vendor_cli: expected {count} of {old!r}, found {found}")
    return text.replace(old, new)


def substitute(text: str, pattern: str, new: str, count: int) -> str:
    """Regex-replace exactly `count` matches, or stop."""
    result, found = re.subn(pattern, new, text)
    if found != count:
        sys.exit(f"vendor_cli: expected {count} matches of {pattern!r}, found {found}")
    return result


def transform_main(s: str) -> str:
    """Upstream's main.rs as alliumpy_core::cli's main module (cli.rs lists each change)."""
    s = replace(
        s, "mod domain_model;\nmod test_plan;\n\n", "use super::{domain_model, test_plan};\n"
    )
    s = replace(s, "use std::process::ExitCode;\n", "use std::io::Write;\n")
    s = replace(
        s,
        "fn main() -> ExitCode {\n"
        "    let args: Vec<String> = std::env::args().skip(1).collect();\n\n",
        f"pub(super) fn main(args: &[String], {HANDLES}) -> i32 {{\n",
    )
    s = replace(
        s,
        '            println!(\n                "allium {} (language versions: 1, 2, 3)",\n'
        '                env!("CARGO_PKG_VERSION")\n            );',
        '            println_to!(stdout, "{}", crate::ALLIUM_VERSION_STRING);',
    )
    s = substitute(s, r"\beprintln!\(", "eprintln_to!(stderr, ", 12)
    s = substitute(s, r"\bprintln!\(", "println_to!(stdout, ", 3)
    s = substitute(s, r"\bprint!\(", "print_to!(stdout, ", 4)
    s = substitute(s, r"ExitCode::SUCCESS", "0", 7)
    s = substitute(s, r"ExitCode::from\((\d)\)", r"\1", 10)
    s = substitute(s, r"-> ExitCode", "-> i32", 9)
    s = replace(
        s,
        '"help" => return cmd_help(&args[1..]),',
        '"help" => return cmd_help(&args[1..], stdout, stderr),',
    )
    for name in COMMANDS:
        s = replace(
            s, f'"{name}" => cmd_{name}(rest),', f'"{name}" => cmd_{name}(rest, stdout, stderr),'
        )
        s = replace(
            s,
            f"fn cmd_{name}(args: &[String]) -> i32 {{",
            f"fn cmd_{name}(args: &[String], {HANDLES}) -> i32 {{",
        )
    s = replace(
        s,
        "fn cmd_help(args: &[String]) -> i32 {",
        f"fn cmd_help(args: &[String], {HANDLES}) -> i32 {{",
    )
    for name in ("check", "analyse"):
        s = replace(
            s,
            f'run_multi_file("{name}", args, |',
            f'run_multi_file("{name}", args, stdout, stderr, |',
        )
    for name in ("plan", "model"):
        old = f'run_single_file("allium {name} <file.allium>", args, |'
        s = replace(s, old, old.replace("args, |", "args, stdout, stderr, |"))
    for first in ("command: &str,", "usage: &str,"):
        old = f"    {first}\n    args: &[String],\n"
        s = replace(s, old, old + "    stdout: &mut dyn Write,\n    stderr: &mut dyn Write,\n")
    return s


def transform_test_plan(s: str) -> str:
    """Upstream's tests read a fixture by its workspace path; read the parity corpus's copy."""
    return replace(
        s,
        '"../allium-parser/tests/fixtures/v3-lifecycle.allium"',
        '"../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium"',
        7,
    )


def attributes(name: str) -> str:
    """The file-level expectations for one vendored file, one lint per line."""
    lines = []
    for lint, reason, cfg in LINTS[name]:
        body = f'expect({lint}, reason = "{reason}")'
        lines.append(f"#![cfg_attr({cfg}, {body})]" if cfg else f"#![{body}]")
    return "\n".join(lines) + "\n"


def main() -> None:
    """Write the three vendored files."""
    tag, source, dest = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    transforms = {"main.rs": transform_main, "test_plan.rs": transform_test_plan}
    for name in LINTS:
        text = (source / name).read_text(encoding="utf-8")
        transform = transforms.get(name)
        if transform is not None:
            text = transform(text)
        out = HEADER.format(tag=tag, name=name) + attributes(name) + text
        (dest / name).write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
