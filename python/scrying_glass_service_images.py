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
        """Save a bounded upload atomically without masking cleanup errors."""
        import logging
        import os
        import tempfile

        logger = logging.getLogger(__name__)
        max_upload_bytes = 10 * 1024 * 1024
        chunk_size = 1024 * 1024

        extension = self.context.Path(
            upload.filename or ""
        ).suffix.lower()

        if extension not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        }:
            raise self.context.HTTPException(
                400,
                "Image must be PNG, JPG, GIF, or WebP",
            )

        declared_size = getattr(upload, "size", None)

        if (
            type(declared_size) is int
            and declared_size > max_upload_bytes
        ):
            raise self.context.HTTPException(
                413,
                "Image must not exceed 10 MiB",
            )

        destination = (
            self.context.UPLOAD_DIR
            / f"{self.context.uuid.uuid4().hex}{extension}"
        )
        temporary = None

        try:
            self.context.UPLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            upload.file.seek(0)
            total = 0

            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=".upload-",
                suffix=".tmp",
                dir=str(self.context.UPLOAD_DIR),
                delete=False,
            ) as output:
                temporary = self.context.Path(output.name)

                while True:
                    chunk = upload.file.read(chunk_size)

                    if not chunk:
                        break

                    total += len(chunk)

                    if total > max_upload_bytes:
                        raise self.context.HTTPException(
                            413,
                            "Image must not exceed 10 MiB",
                        )

                    output.write(chunk)

                if total == 0:
                    raise self.context.HTTPException(
                        400,
                        "Image upload is empty",
                    )

            os.replace(temporary, destination)
            temporary = None
            # The database wrapper also owns rollback of newly created media.
            if getattr(self.context, "_defer_database_broadcast", False):
                self.context._bundle_files.append(destination)

        except self.context.HTTPException:
            raise

        except (OSError, ValueError) as exc:
            logger.exception(
                "Unable to save image upload",
            )

            raise self.context.HTTPException(
                500,
                "Unable to save image upload",
            ) from exc

        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    logger.warning(
                        "Unable to remove partial image upload %s",
                        temporary,
                        exc_info=True,
                    )

        return f"/media/{destination.name}"

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

    def make_monster(
        self,
        fields: dict[str, Any],
        color: str,
        upload: UploadFile | None,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """Validate creation/import fields before building an editable monster."""
        if not isinstance(fields, dict):
            raise self.context.HTTPException(422, "Monster fields must be an object")
        prepared = dict(fields)
        for field in ("name", "monster_species"):
            value = prepared.get(field)
            if not isinstance(value, str):
                raise self.context.HTTPException(422, f"{field} must be text")
            value = value.strip()
            if not 1 <= len(value) <= 100:
                raise self.context.HTTPException(422, f"{field} must contain 1-100 characters after trimming")
            prepared[field] = value
        ac = prepared.get("ac")
        if type(ac) is not int or not 0 <= ac <= 999:
            raise self.context.HTTPException(422, "AC must be an integer between 0 and 999")
        if not isinstance(color, str) or not 1 <= len(color.strip()) <= 40:
            raise self.context.HTTPException(422, "Color must contain 1-40 characters")
        color = color.strip()
        hp = prepared.get("hp")
        if type(hp) is not int or not -(2 ** 63) <= hp <= 2 ** 63 - 1:
            raise self.context.HTTPException(422, "HP must be an integer within the signed 64-bit storage range")

        if upload is not None and upload.filename:
            image_url = self.context.save_image(upload)

        return {
            **prepared,
            "id": self.context.uuid.uuid4().hex,
            "max_hp": hp,
            "original_hp": hp,
            "color": color,
            "image_url": image_url,
            "active": False,
            "alive": hp > 0,
            "visible": False,
            "ally": False,
            "initiative": None,
            "original_initiative": None,
            "show_ac": False,
            "show_hp": False,
            "show_initiative": False,
            "in_turn": False,
        }
    
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
