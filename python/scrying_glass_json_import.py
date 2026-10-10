"""JSON import decoding that rejects silent duplicate-key overwrites."""
import json


class DuplicateJsonKeyError(ValueError):
    """A JSON object contains the same decoded key more than once."""


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
    return json.loads(raw, object_pairs_hook=_unique_object)
