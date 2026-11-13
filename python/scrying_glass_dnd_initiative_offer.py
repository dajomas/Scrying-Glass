"""Conservative explicit D&D Beyond initiative offers; no ability derivation."""
import re
from html.parser import HTMLParser
from .scrying_glass_initiative_input import creation_bonus_fields

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
IGNORED = {"script", "style", "noscript", "nav", "header", "footer"}


class _StatText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.roots = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else (None, None, False)
        style = attrs.get("style") or ""
        style_hidden = re.search(r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)(?:\s*!important)?\s*(?:;|$)", style, re.IGNORECASE)
        ignored = parent[2] or tag in IGNORED or "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true" or bool(style_hidden)
        root = parent[1]
        if root is None and not ignored and "mon-stat-block" in attrs.get("class", "").split():
            root = len(self.roots)
            self.roots.append([])
        if tag not in VOID:
            self.stack.append((tag, root, ignored))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack:
            _, root, ignored = self.stack[-1]
            if root is not None and not ignored:
                self.roots[root].append(data)


def dnd_initiative_offer(html):
    def unavailable(status, reason):
        return {"initiative_bonus": None, "initiative_bonus_status": status,
                "initiative_bonus_reason": reason}
    if not isinstance(html, str) or len(html) > 8_000_000:
        return unavailable("invalid", "Invalid or oversized monster HTML")
    reader = _StatText()
    try:
        reader.feed(html)
        reader.close()
    except Exception:
        return unavailable("invalid", "Monster HTML could not be parsed")
    if not reader.roots:
        return unavailable("missing", "Recognized monster stat block unavailable")
    if len(reader.roots) != 1:
        return unavailable("ambiguous", "Multiple monster stat blocks require review")
    text = " ".join(" ".join(reader.roots[0]).split())[:16_000]
    end = re.search(r"\b(?:HP|Hit Points|Speed|STR|Strength|Actions|Traits)\b", text, re.IGNORECASE)
    header = text[:end.end()] if end else text
    labels = re.findall(r"\bInitiative\b", header, re.IGNORECASE)
    if not labels:
        return unavailable("missing", "No explicit initiative modifier in the recognized header")
    if len(labels) != 1:
        return unavailable("ambiguous", "Conflicting initiative labels in the header")
    match = re.search(r"\bAC\s+[0-9]+\s+Initiative\s+([+\-−]\s*[0-9]{1,20})\s*\(\s*[0-9]+\s*\)\s+HP\b",
                      header, re.IGNORECASE)
    if match is None:
        return unavailable("invalid", "Unsupported explicit initiative header format")
    try:
        value = re.sub(r"\s+", "", match.group(1)).replace("−", "-")
        bonus = creation_bonus_fields(value, origin="source")["initiative_bonus"]
    except ValueError:
        return unavailable("invalid", "Explicit initiative modifier is outside the storage range")
    return {"initiative_bonus": bonus, "initiative_bonus_status": "available",
            "initiative_bonus_evidence": match.group(0)[:512]}
