import re

from urllib.parse import quote
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
        title = re.sub(r"<[^>]+>", "", result.group("content"))
        title = re.sub(r"\s+", " ", title).strip()

        if normalized_dnd_name(title) != requested_name:
            continue

        href = result.group("href")

        if href in seen_hrefs:
            continue

        seen_hrefs.add(href)

        # Deliberately inspect the complete matched anchor, as agreed.
        is_legacy = "legacy" in result.group(0).casefold()

        candidates.append((is_legacy, href))

    candidates.sort(key=lambda candidate: not candidate[0])

    return candidates

def dnd_monster_detail_html(href: str) -> str:
    """Dnd monster detail html."""
    headers = {
        "User-Agent": "Mozilla/5.0 compatible; ScryingGlass/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }

    monster_url = (
        href
        if href.startswith("http://") or href.startswith("https://")
        else f"https://www.dndbeyond.com{href}"
    )

    request = Request(monster_url, headers=headers)

    with urlopen(request, timeout=5) as response:
        return response.read(1_000_000).decode("utf-8", "replace")

def html_to_text(value: str) -> str:
    """Html to text."""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"&nbsp;", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"&amp;", "&", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip()

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
