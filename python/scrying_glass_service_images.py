"""Images services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class ImagesService:
    """Group images operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def save_image(self, upload: UploadFile) -> str:
        """Save image."""
        ext = self.context.Path(upload.filename or '').suffix.lower()
        if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}:
            raise self.context.HTTPException(400, 'Image must be PNG, JPG, GIF, or WebP')
        dst = self.context.UPLOAD_DIR / f'{self.context.uuid.uuid4().hex}{ext}'
        with dst.open('wb') as f:
            self.context.shutil.copyfileobj(upload.file, f)
        return '/media/' + dst.name

    def dnd_image(self, monster_species: str) -> str | None:
        '\n    Find the dedicated D&D Beyond monster image for monster_species.\n\n    Exact normalized name matches are collected from D&D Beyond search results.\n    A match whose complete result HTML contains \'legacy\' is preferred. The\n    dedicated <img class="monster-image"> URL from that monster page is used,\n    not a generic Open Graph image.\n    '
        if not self.context.CONFIG["display"].get("dndbeyond_image_lookup", True):
            return None

        requested_name = self.context.re.sub(
            r"[^a-z0-9]+",
            " ",
            monster_species.casefold(),
        ).strip()

        if not requested_name:
            return None

        headers = {
            "User-Agent": "Mozilla/5.0 compatible; ScryingGlass/1.0",
            "Accept": "text/html,application/xhtml+xml",
        }

        try:
            search_url = (
                "https://www.dndbeyond.com/monsters"
                f"?filter-search={self.context.quote(monster_species)}"
            )

            request = self.context.Request(search_url, headers=headers)

            with self.context.urlopen(request, timeout=5) as response:
                search_html = response.read(1_000_000).decode(
                    "utf-8",
                    "replace",
                )

            candidates: list[tuple[bool, str]] = []

            for result in self.context.re.finditer(
                r'<a\b[^>]*href="(?P<href>/monsters/[^"]+)"[^>]*>'
                r"(?P<content>.*?)</a>",
                search_html,
                self.context.re.IGNORECASE | self.context.re.DOTALL,
            ):
                title = self.context.re.sub(r"<[^>]+>", "", result.group("content"))
                title = self.context.re.sub(r"\s+", " ", title).strip()

                normalized_title = self.context.re.sub(
                    r"[^a-z0-9]+",
                    " ",
                    title.casefold(),
                ).strip()

                if normalized_title != requested_name:
                    continue

                href = result.group("href")

                # Prefer an older / legacy monster page where D&D Beyond labels it
                # that way. Current exact-name matches remain fallback candidates.
                is_legacy = "legacy" in result.group(0).casefold()

                candidates.append((is_legacy, href))
            # True first: older/legacy exact matches are tried before current ones.
            candidates.sort(key=lambda candidate: not candidate[0])

            for _, href in candidates:
                monster_url = f"https://www.dndbeyond.com{href}"

                monster_request = self.context.Request(monster_url, headers=headers)
                with self.context.urlopen(monster_request, timeout=5) as response:
                    monster_html = response.read(1_000_000).decode(
                        "utf-8",
                        "replace",
                    )

                # Extract the actual monster illustration, not Open Graph metadata.
                image = self.context.re.search(
                    '\n                <img\\b\n                    [^>]*\\bclass=["\'][^"\']*\\bmonster-image\\b[^"\']*["\']\n                    [^>]*\\bsrc=["\'](?P<url>[^"\']+)["\']\n                    [^>]*>\n                ',
                    monster_html,
                    self.context.re.IGNORECASE | self.context.re.DOTALL | self.context.re.VERBOSE,
                )

                # Attributes are not guaranteed to remain in a fixed order. Retry
                # with src before class for pages that render it that way.
                if image is None:
                    image = self.context.re.search(
                        '\n                    <img\\b\n                        [^>]*\\bsrc=["\'](?P<url>[^"\']+)["\']\n                        [^>]*\\bclass=["\'][^"\']*\\bmonster-image\\b[^"\']*["\']\n                        [^>]*>\n                    ',
                        monster_html,
                        self.context.re.IGNORECASE | self.context.re.DOTALL | self.context.re.VERBOSE,
                    )

                if image is not None:
                    image_url = image.group("url").strip()

                    if image_url.startswith("//"):
                        image_url = f"https:{image_url}"
                    elif image_url.startswith("/"):
                        image_url = (
                            "https://www.dndbeyond.com"
                            f"{image_url}"
                        )

                    return image_url

            return None

        except Exception:
            # Image lookup is optional and must not block monster creation.
            return None

    def make_monster(self, fields: dict[str, Any], color: str, upload: UploadFile | None, image_url: str | None=None) -> dict[str, Any]:
        """Make monster."""
        hp = fields['hp']
        return {'id': self.context.uuid.uuid4().hex, **fields, 'max_hp': hp, 'original_hp': hp, 'color': color, 'image_url': image_url if image_url is not None else self.context.save_image(upload) if upload and upload.filename else self.context.dnd_image(fields['monster_species']), 'active': False, 'alive': True, 'visible': False, 'ally': False, 'initiative': None, 'original_initiative': None, 'show_ac': False, 'show_hp': False, 'show_initiative': False, 'in_turn': False}

    def make_monsters(self, fields: dict[str, Any], color: str, quantity: int, image_url: str | None) -> list[dict[str, Any]]:
        """Make monsters."""
        return [
            self.context.make_monster(
                {
                    **fields,
                    'name': (
                        fields['name']
                        if quantity == 1
                        else f"{fields['name']} - {number}"
                    ),
                },
                color,
                None,
                image_url,
            )
            for number in range(1, quantity + 1)
        ]
