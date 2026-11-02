import re
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError

from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

def normalized_dnd_name(value: str) -> str:
    """Normalized dnd name."""
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value).casefold(),
    ).strip()

def dnd_monster_candidates(monster_species: str) -> list[tuple[bool, str]]:
    """
    Return exact D&D Beyond monster candidates as (is_legacy, href).

    Candidates are sorted with a legacy-marked matching anchor first. This
    function deliberately uses the established anchor matcher because it is
    known to work with the current D&D Beyond search response.
    """
    requested_name = normalized_dnd_name(monster_species)

    if not requested_name:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 compatible; ScryingGlass/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }

    search_url = (
        "https://www.dndbeyond.com/monsters"
        f"?filter-search={quote(monster_species)}"
    )

    request = Request(search_url, headers=headers)

    with urlopen(request, timeout=5) as response:
        search_html = response.read(1_000_000).decode(
            "utf-8",
            "replace",
        )

    candidates: list[tuple[bool, str]] = []
    seen_hrefs: set[str] = set()

    for result in re.finditer(
        r'<a\b[^>]*href="(?P<href>/monsters/[^"]+)"[^>]*>'
        r"(?P<content>.*?)</a>",
        search_html,
        re.IGNORECASE | re.DOTALL,
    ):
        title = html_to_text(result.group("content"))

        if normalized_dnd_name(title) != requested_name:
            continue

        href = unescape(result.group("href"))

        if href in seen_hrefs:
            continue

        seen_hrefs.add(href)

        # Deliberately inspect the complete matched anchor, as agreed.
        is_legacy = "legacy" in result.group(0).casefold()

        candidates.append((is_legacy, href))

    candidates.sort(key=lambda candidate: not candidate[0])

    return candidates

def dnd_monster_content_locked(monster_html: str) -> bool:
    """Conservative visible-text evidence, not a generic 401/403 classifier."""
    parser = _AccessText()
    parser.feed(monster_html)
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).casefold()
    if any(marker in text for marker in (
        "verify you are human", "checking your browser", "just a moment", "captcha",
    )):
        return False
    return any(re.search(pattern, text) for pattern in (
        r"you (?:do not|don't) (?:have access to|own) this content",
        r"you (?:must|need to) (?:purchase|unlock) this (?:content|monster)",
        r"purchase this content to (?:view|access)",
        r"this content is locked",
    ))


class _AccessText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.ignored = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "header", "footer"}:
            self.ignored.append(tag)

    def handle_endtag(self, tag):
        if self.ignored and self.ignored[-1] == tag:
            self.ignored.pop()

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)


def dnd_monster_detail_html(href: str) -> str:
    """Return monster HTML, or empty HTML for positively identified access gates.

    Other failures still raise so callers do not confuse an incomplete lookup
    with zero usable matches. No authentication or access-control bypass occurs.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 compatible; ScryingGlass/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }
    monster_url = href if href.startswith(("http://", "https://")) else f"https://www.dndbeyond.com{href}"
    request = Request(monster_url, headers=headers)
    max_page_bytes = 8_000_000
    try:
        response = urlopen(request, timeout=15)
    except HTTPError as exc:
        if exc.code in {401, 403}:
            # A status code alone is not evidence of a locked content page.
            try:
                with exc:
                    raw = exc.read(128_001)
                if len(raw) <= 128_000 and dnd_monster_content_locked(raw.decode("utf-8", "replace")):
                    return ""
            except Exception:
                raise exc
        raise

    with response:
        final = urlsplit(response.geturl())
        if (
            final.scheme == "https"
            and final.hostname == "marketplace.dndbeyond.com"
            and not final.username
            and not final.password
            and final.path.startswith("/category/")
        ):
            return ""
        if (final.scheme != "https" or final.hostname not in {"www.dndbeyond.com", "dndbeyond.com"}
                or final.username or final.password):
            raise ValueError("D&D Beyond returned an untrusted monster redirect")
        path = final.path.rstrip("/").casefold()
        if any(path == gate or path.startswith(gate + "/") for gate in (
            "/marketplace", "/login", "/sign-in",
        )):
            return ""
        if not final.path.startswith("/monsters/"):
            raise ValueError("D&D Beyond did not return a monster page")
        content = response.read(max_page_bytes + 1)
    if len(content) > max_page_bytes:
        raise ValueError("D&D Beyond monster page exceeds 8000000 bytes")
    html = content.decode("utf-8", "replace")
    return "" if dnd_monster_content_locked(html) else html

def html_to_text(value: str) -> str:
    """Html to text."""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"&nbsp;", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"&amp;", "&", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", unescape(value)).strip()

def dnd_monster_stats_from_html(
    monster_html: str,
) -> tuple[int | None, str | None, str | None]:
    """
    Return (ac, hp_value, hp_source) from a D&D Beyond monster page.

    HP dice notation is preferred over the displayed numeric average.
    """
    ac: int | None = None
    hp_value: str | None = None
    hp_source: str | None = None

    armor_match = re.search(
        r"""
        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-label
            [^"']*["']
            [^>]*>
            \s*Armor\ Class\s*
        </span>

        (?P<content>.{0,3000}?)

        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-label
            [^"']*["']
            [^>]*>
        """,
        monster_html,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    if armor_match is not None:
        ac_match = re.search(
            r"""
            <span\b
                [^>]*\bclass=["'][^"']*
                mon-stat-block__attribute-data-value
                [^"']*["']
                [^>]*>
                \s*(?P<ac>\d+)\s*
            </span>
            """,
            armor_match.group("content"),
            re.IGNORECASE | re.DOTALL | re.VERBOSE,
        )

        if ac_match is not None:
            ac = int(ac_match.group("ac"))

    hp_match = re.search(
        r"""
        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-label
            [^"']*["']
            [^>]*>
            \s*Hit\ Points\s*
        </span>

        (?P<content>.{0,3000}?)

        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-label
            [^"']*["']
            [^>]*>
        """,
        monster_html,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    if hp_match is None:
        return ac, None, None

    hp_content = hp_match.group("content")

    dice_match = re.search(
        r"""
        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-data-extra
            [^"']*["']
            [^>]*>
            \s*
            \(
            \s*
            (?P<dice>
                [1-9]\d*
                \s*d\s*
                (?:[2-9]\d*|1\d+)
                (?:\s*[+-]\s*\d+)?
            )
            \s*
            \)
            \s*
        </span>
        """,
        hp_content,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    if dice_match is not None:
        return (
            ac,
            re.sub(r"\s+", "", dice_match.group("dice")),
            "dice",
        )

    average_match = re.search(
        r"""
        <span\b
            [^>]*\bclass=["'][^"']*
            mon-stat-block__attribute-data-value
            [^"']*["']
            [^>]*>
            \s*(?P<hp>\d+)\s*
        </span>
        """,
        hp_content,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    if average_match is not None:
        hp_value = average_match.group("hp")
        hp_source = "average"

    return ac, hp_value, hp_source
