"""Pipe tables when every cell is inline-only; otherwise a sanitized HTML island."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree, html

from docmirror.normalize.islands import sanitize

if TYPE_CHECKING:
    from docmirror.normalize.islands import Islands

BLOCK_IN_CELL = frozenset(
    {
        "p",
        "div",
        "ul",
        "ol",
        "pre",
        "table",
        "dl",
        "blockquote",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "figure",
        "details",
    }
)
TABLE_KEEP = frozenset({"rowspan", "colspan", "id", "scope", "href", "src", "alt", "title"})


def _cells(table: html.HtmlElement) -> list[html.HtmlElement]:
    return [c for c in table.iter("td", "th") if _owning_table(c) is table]


def _owning_table(cell: html.HtmlElement) -> html.HtmlElement | None:
    for ancestor in cell.iterancestors():
        if ancestor.tag == "table":
            return ancestor
    return None


def _unwrap_single_paragraphs(cell: html.HtmlElement) -> None:
    children = [c for c in cell if isinstance(c.tag, str)]
    if (
        len(children) == 1
        and children[0].tag == "p"
        and not (cell.text or "").strip()
        and not (children[0].tail or "").strip()
    ):
        paragraph = children[0]
        cell.text = paragraph.text
        for grandchild in list(paragraph):
            cell.append(grandchild)
        cell.remove(paragraph)


def is_layout(table: html.HtmlElement) -> bool:
    """A single-cell table, or one whose rows all hold one cell, only positions content."""
    cells = _cells(table)
    if len(cells) <= 1:
        return True
    rows = [r for r in table.iter("tr") if _owning_table(r) is table]
    return (
        bool(rows)
        and all(len([c for c in r if c.tag in {"td", "th"}]) == 1 for r in rows)
        and not any(c.tag == "th" for c in cells)
    )


def is_complex(table: html.HtmlElement) -> bool:
    """Whether any cell spans or holds block-level content, or no row can be a header.

    A pipe table needs a header row: a single row of `<td>` has none, and a converter
    turns it into a bullet list or an empty header, so it stays HTML.
    """
    cells = _cells(table)
    rows = [c.getparent() for c in cells if c.getparent() is not None]
    first_row = rows[0] if rows else None
    if len(set(rows)) == 1 and not any(c.tag == "th" for c in cells):
        return True
    if any(c.tag == "th" and c.getparent() is not first_row for c in cells):
        # Row headers (`<th>` down the first column) have no pipe-table form either.
        return True
    for cell in cells:
        if cell.get("rowspan", "1") not in {"1", ""} or cell.get("colspan", "1") not in {"1", ""}:
            return True
        _unwrap_single_paragraphs(cell)
        for child in cell.iter():
            if child is cell or not isinstance(child.tag, str):
                continue
            if child.tag in BLOCK_IN_CELL:
                return True
            if child.tag == "br" and any(sibling.tag == "br" for sibling in child.itersiblings()):
                return True
    return any(True for _ in table.iter("table") if _ is not table)


def _unwrap(table: html.HtmlElement) -> None:
    holder = html.Element("div")
    for cell in _cells(table):
        block = etree.SubElement(holder, "div")
        block.text = cell.text
        for child in list(cell):
            block.append(child)
    holder.tail = table.tail
    parent = table.getparent()
    if parent is not None:
        parent.replace(table, holder)


def transform(
    content: html.HtmlElement, islands: Islands, flags: set[str], counts: dict[str, int]
) -> None:
    """Classify every table; count the ones the output must carry."""
    kept = 0
    simple = 0
    cells = 0
    for table in list(content.iter("table")):
        if table.getparent() is None:
            continue
        if is_layout(table):
            _unwrap(table)
            continue
        if any(a.tag == "table" for a in table.iterancestors()):
            continue
        if is_complex(table):
            cells += len(_cells(table))
            islands.replace_element(table, sanitize(table, TABLE_KEEP))
            kept += 1
            continue
        cells += len(_cells(table))
        simple += 1
    counts["tables"] = kept + simple
    counts["table_cells"] = cells
    counts["html_tables"] = kept
    if kept:
        flags.add("html_table_kept")
