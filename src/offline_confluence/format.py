from __future__ import annotations

import html
from dataclasses import dataclass, field
from html.parser import HTMLParser

# Tags that represent block-level structure; safe to add indentation around them.
BLOCK_TAGS: frozenset[str] = frozenset({
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "table", "tbody", "thead", "tfoot", "tr", "th", "td",
    "div", "blockquote", "pre",
    # Confluence ADF structural elements
    "ac:adf-extension", "ac:adf-node", "ac:adf-content", "ac:adf-fallback",
    "ac:adf-attribute", "ac:structured-macro", "ac:parameter",
})

# Standard HTML void elements — always serialized self-closed.
HTML_VOID: frozenset[str] = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


@dataclass
class _Element:
    tag: str
    attrs: list[tuple[str, str | None]]
    self_closing: bool = False
    children: list = field(default_factory=list)


@dataclass
class _Text:
    text: str


@dataclass
class _Comment:
    data: str


class _Root:
    def __init__(self) -> None:
        self.children: list = []


class _ConfluenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Root()
        self._stack: list = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        elem = _Element(tag, list(attrs))
        self._stack[-1].children.append(elem)
        if tag in HTML_VOID:
            elem.self_closing = True
        else:
            self._stack.append(elem)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._stack[-1].children.append(_Element(tag, list(attrs), self_closing=True))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):
            if isinstance(self._stack[i], _Element) and self._stack[i].tag == tag:
                self._stack = self._stack[:i]
                return

    def handle_data(self, data: str) -> None:
        self._stack[-1].children.append(_Text(data))

    def handle_comment(self, data: str) -> None:
        self._stack[-1].children.append(_Comment(data))


def _serialize_attrs(attrs: list[tuple[str, str | None]]) -> str:
    parts = []
    for name, val in attrs:
        if val is None:
            parts.append(f" {name}")
        else:
            parts.append(f' {name}="{html.escape(val, quote=True)}"')
    return "".join(parts)


def _has_significant_text(children: list) -> bool:
    return any(isinstance(c, _Text) and c.text.strip() for c in children)


def _serialize(
    node: _Root | _Element | _Text | _Comment,
    indent: int = 0,
    inline: bool = False,
    compact: bool = False,
) -> str:
    if isinstance(node, _Text):
        return html.escape(node.text, quote=False)

    if isinstance(node, _Comment):
        return f"<!--{node.data}-->"

    if isinstance(node, _Root):
        parts = []
        for child in node.children:
            if isinstance(child, _Text) and not child.text.strip():
                continue
            s = _serialize(child, indent=0, inline=False, compact=compact)
            if s:
                parts.append(s)
        return ("\n" if not compact else "").join(parts)

    # _Element
    tag = node.tag
    attrs_str = _serialize_attrs(node.attrs)
    is_block = tag in BLOCK_TAGS
    pad = ("  " * indent) if is_block and not inline and not compact else ""

    if node.self_closing:
        return f"{pad}<{tag}{attrs_str} />"

    # Indent children only when this is a block element in a non-inline, non-compact context,
    # and its direct children include at least one block-level element (no significant inline
    # text mixed in). Inline-only children (e.g. <p><strong>x</strong></p>) stay on one line.
    should_indent = (
        is_block
        and not inline
        and not compact
        and not _has_significant_text(node.children)
        and any(isinstance(c, _Element) and c.tag in BLOCK_TAGS for c in node.children)
    )

    if should_indent:
        child_parts = []
        for child in node.children:
            if isinstance(child, _Text) and not child.text.strip():
                continue  # skip whitespace-only text between block siblings
            child_parts.append(_serialize(child, indent=indent + 1, inline=False, compact=False))
        children_str = "\n".join(child_parts)
        return f"{pad}<{tag}{attrs_str}>\n{children_str}\n{pad}</{tag}>"
    else:
        child_parts = []
        for child in node.children:
            # In compact mode, strip whitespace-only text between block-context children.
            if compact and is_block and isinstance(child, _Text) and not child.text.strip():
                continue
            child_parts.append(_serialize(child, indent=0, inline=True, compact=compact))
        children_str = "".join(child_parts)
        return f"{pad}<{tag}{attrs_str}>{children_str}</{tag}>"


def prettify(html_str: str) -> str:
    """Return a human-readable, block-indented version of Confluence storage format HTML."""
    parser = _ConfluenceParser()
    parser.feed(html_str)
    return _serialize(parser.root, compact=False)


def compact(html_str: str) -> str:
    """Strip prettification whitespace from Confluence storage format HTML."""
    parser = _ConfluenceParser()
    parser.feed(html_str)
    return _serialize(parser.root, compact=True)
