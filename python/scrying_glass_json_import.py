"""JSON import decoding that rejects silent duplicate-key overwrites."""
import json
import math


class DuplicateJsonKeyError(ValueError):
    """A JSON object contains the same decoded key more than once."""


class InvalidJsonTextError(ValueError):
    """Import JSON contains decoded text that cannot be stored as UTF-8."""


class InvalidJsonNumberError(ValueError):
    """Import JSON contains a non-finite decoded numeric value."""


def _validate_values(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            pending.extend(item.keys())
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, float) and not math.isfinite(item):
            raise InvalidJsonNumberError("Import JSON numbers must be finite")
        elif isinstance(item, str):
            try:
                item.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise InvalidJsonTextError(
                    "Import JSON text contains an unpaired Unicode surrogate"
                ) from exc


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            preview = repr(key[:100]) + ("..." if len(key) > 100 else "")
            raise DuplicateJsonKeyError("Duplicate JSON object key: " + preview)
        result[key] = value
    return result


def load_import_json(raw):
    """Retain ordinary JSON decoding while requiring unique object keys."""
    value = json.loads(raw, object_pairs_hook=_unique_object)
    _validate_values(value)
    return value
