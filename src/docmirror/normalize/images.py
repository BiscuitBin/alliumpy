"""Images keep absolute URLs and titles; empty `alt` borrows the title or figure caption."""

from __future__ import annotations

from lxml import etree, html


def transform(content: html.HtmlElement, counts: dict[str, int]) -> None:
    """Fill alt text and flatten figures."""
    for figure in list(content.iter("figure")):
        caption = figure.find("figcaption")
        caption_text = " ".join(caption.text_content().split()) if caption is not None else ""
        for image in figure.iter("img"):
            if not (image.get("alt") or "").strip():
                image.set("alt", caption_text or image.get("title") or "")
        holder = html.Element("div")
        if caption is not None:
            figure.remove(caption)
        holder.text = figure.text
        for child in list(figure):
            holder.append(child)
        if caption is not None and caption_text:
            # The caption's own nodes, so its links and inline markup survive.
            paragraph = etree.SubElement(holder, "p")
            emphasis = etree.SubElement(paragraph, "em")
            emphasis.text = (caption.text or "").lstrip()
            emphasis.extend(list(caption))
            if len(emphasis):
                emphasis[-1].tail = (emphasis[-1].tail or "").rstrip()
            else:
                emphasis.text = emphasis.text.rstrip()
        holder.tail = figure.tail
        parent = figure.getparent()
        if parent is not None:
            parent.replace(figure, holder)
    total = 0
    for image in content.iter("img"):
        total += 1
        if not (image.get("alt") or "").strip() and image.get("title"):
            image.set("alt", image.get("title") or "")
        for name in list(image.attrib):
            if name not in {"src", "alt", "title", "id"}:
                del image.attrib[name]
    counts["images"] = total
